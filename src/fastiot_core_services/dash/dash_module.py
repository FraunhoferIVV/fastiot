from dataclasses import dataclass
from datetime import datetime, timedelta, date
from random import randint

import dash
import plotly.graph_objects as go
from dash import dcc, html
import dash_bootstrap_components as dbc

from fastiot.core import FastIoTService, Subject, subscribe, ReplySubject
from fastiot.db.mongodb_helper_fn import get_mongodb_client_from_env
from fastiot.env import env_mongodb, env_mongodb_cols
from fastiot.msg.thing import Thing
from fastiot.util.read_yaml import read_config
from fastiot_core_services.dash.env import env_dash
from fastiot_core_services.dash.model.historic_sensor import HistoricSensor
from fastiot_core_services.dash.model.live_sensor import LiveSensor
from fastiot_core_services.dash.utils import ServerThread


class DashModule(FastIoTService):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._subscriptions = []
        self.config = read_config(self)
        self.live_sensor_list = []
        self.historic_sensor_list = []
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], prevent_initial_callbacks=True)
        self.server = ServerThread(self.app.server)
        self.setup_live_sensors()
        self.data_resolution = 1
        self.start_datetime = None
        self.end_datetime = None
        self.__down = False

    async def _start(self):
        """ Methods to start once the module is initialized """
        self.server.start()
        self._logger.info('=== Started Dash Service at %s:%s ===', env_dash.dash_host, env_dash.dash_port)
        self.initial_start_date = self.initial_date(self.config.get("initial_start_date"))
        self.initial_end_date = self.initial_date(self.config.get("initial_end_date"))
        self._setup_dash()
        await self.setup_historic_sensors(self.initial_start_date, self.initial_end_date)

    async def _stop(self):
        """ Methods to call on module shutdown """
        self.server.shutdown()

    def initial_date(self, date_in):
        if isinstance(date_in, str):
            date_out = datetime.utcnow()
            date_in = date_in.replace("now", "")
            if "-" in date_in:
                date_in = date_in.replace("-", "")
                x = datetime.strptime(date_in, '%H:%M:%S')
                date_out = date_out - timedelta(hours=x.hour, minutes=x.minute, seconds=x.second)

        else:
            date_out = date_in
        return date_out

    def setup_live_sensors(self):
        for dashboard in self.config.get("dashboards"):
            if dashboard.get("live_data"):
                for sensor in dashboard.get("sensors"):
                    live_sensor = LiveSensor(sensor.get("name"),
                                             sensor.get("machine"),
                                             dashboard.get("customer"),
                                             sensor.get("service")
                                             )
                    self.live_sensor_list.append(live_sensor)

    def _setup_dash(self):
        self.app.title = "Data Dashboard"

        self.app.layout = html.Div(self.setup_html(
            self.initial_start_date,
            self.initial_end_date)
        )
        for i_dashboard, dashboard in enumerate(self.config.get("dashboards")):
            if dashboard.get("live_data"):
                self.app.callback(
                    dash.dependencies.Output(str(i_dashboard), 'figure'),
                    [dash.dependencies.Input('refreshing' + str(i_dashboard), 'value'),
                     dash.dependencies.Input(str(i_dashboard) + "interval", 'n_intervals')]
                )(GraphCallbacks(module=self, dashboard=dashboard).update_graph)
            else:

                self.app.callback(
                    dash.dependencies.Output(str(i_dashboard), 'figure'),
                    [dash.dependencies.Input(str(i_dashboard) + 'date-picker', 'start_date'),
                     dash.dependencies.Input(str(i_dashboard) + 'date-picker', 'end_date'),
                     dash.dependencies.Input(str(i_dashboard) + 'Input', 'value'),
                     dash.dependencies.Input(str(i_dashboard) + 'button', 'n_clicks')]
                )(GraphCallbacks(module=self, dashboard=dashboard).show_graph)

                self.app.server.route(
                    "/download_excel/")(self.download_excel)

    def update_graph(self, dashboard, *args, **kwargs):
        traces = []
        for sensor in dashboard.get("sensors"):
            values = []
            timestamp = []
            for live_sensor in self.live_sensor_list:
                if live_sensor.name == sensor.get("name"):
                    for sensor_list in live_sensor.live_sensors:
                        values.append(sensor_list.value)
                        timestamp.append(sensor_list.timestamp)
            trace1 = go.Scatter(
                x=timestamp,
                y=values,
                name=sensor.get("name"),

            )
            traces.append(trace1)
        return traces
    def setup_html(self, start_date, end_date):
        html_cards = []
        html_navbar_elements = []
        html_elements = []

        for i_dashboard, dashboard in enumerate(self.config.get("dashboards")):
            html_card_elements = []
            html_navbar_elements.extend([
                html.A(dbc.Button(dashboard.get("name"), id=str(i_dashboard) + "nav_button", className="ms-1"),
                       href='#card' + str(i_dashboard), )])

            if dashboard.get("live_data"):
                html_card_elements.extend([
                    dcc.RadioItems(
                        id='refreshing' + str(i_dashboard),
                        options=[
                            {'label': 'Stop refreshing', 'value': 'stop'},
                            {'label': 'refreshing', 'value': 'start'},
                        ],
                        value='start',
                        labelStyle={'display': 'inline-block'}
                    )])
                html_card_elements.extend([
                    dcc.Graph(id=str(i_dashboard)),
                    dcc.Interval(
                        id=str(i_dashboard) + "interval",
                        interval=dashboard.get("refresh_time"),
                        n_intervals=0,
                    )
                ])
            else:
                html_card_elements.extend([
                    html.Button('Click to reload', id=str(i_dashboard) + 'button', n_clicks=0)])
                html_card_elements.extend([
                    dcc.Input(
                        id=str(i_dashboard) + "Input",
                        type='number',
                        placeholder="Resolution of the data in minutes"
                    )
                ])
                html_card_elements.extend([
                    dcc.Graph(id=str(i_dashboard))
                ])

            if not dashboard.get("live_data"):
                html_card_elements.extend([
                    dcc.DatePickerRange(
                        id=str(i_dashboard) + 'date-picker',
                        display_format='DD-MM-YYYY',
                        max_date_allowed=date.today(),
                        updatemode='bothdates',
                        initial_visible_month=date.today(),
                        start_date=start_date,
                        end_date=end_date)
                ])
                html_card_elements.extend([
                    html.A("download excel", href="/download_excel/")])
            card = dbc.Card([
                dbc.CardHeader(dashboard.get("name")),
                dbc.CardBody(html_card_elements),
            ], color="#a2d4c7", outline=True, className="mb-4", id="card" + str(i_dashboard),
            )
            html_cards.append(card)
        html_navbar = dbc.Navbar(
            dbc.Row(
                [

                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Col(
                        [
                            html.Img(src="/assets/fraunhofer_logo.png", height="40px", className="mb-3"),
                            dbc.NavbarBrand("Data Dashboard", className="ms-4"),

                        ],
                        className="ps-3"
                    ),
                    dbc.Col(
                        html_navbar_elements,
                        width="auto",
                        align="center",
                    ),
                ],
            ),
            color="#185a47",
            dark=True,
            sticky="top",
        )
        html_elements.append(html_navbar)
        html_elements.extend(html_cards)
        return html_elements

    async def setup_historic_sensors(self, start_time: datetime, end_time: datetime):
        self.historic_sensor_list.clear()
        client_mongodb = get_mongodb_client_from_env()
        try:
            mongodb = client_mongodb.get_database(env_mongodb.name)
            col_mongo = mongodb.get_collection(env_mongodb_cols.time_series)
            for dashboard in self.config.get("dashboards"):
                if not dashboard.get("live_data"):
                    for sensor in dashboard.get("sensors"):
                        historic_sensor = HistoricSensor(sensor.get("name"),
                                                         sensor.get("machine"),
                                                         dashboard.get("customer"),
                                                         sensor.get("module")
                                                         )
                        if "mongo" in dashboard.get("db_type"):
                            result = col_mongo.find({
                                "sensor_name": sensor.get("name"),
                                "machine_id": sensor.get("machine"),
                                'dt_start': {'$gte': start_time},
                                'dt_end': {'$lte': end_time}

                            })
                            for r in result:
                                if historic_sensor.historic_sensor_data is None:
                                    historic_sensor.historic_sensor_data = time_series_data_from_mongodb_data_set(r)
                                else:
                                    historic_sensor.historic_sensor_data = self.append_time_series(
                                        historic_sensor.historic_sensor_data, time_series_data_from_mongodb_data_set(r))

                                historic_sensor.historic_sensor_data.remove_until(start_time)
                                historic_sensor.historic_sensor_data.remove_from(end_time)
                        else:

                            query_results = influx_query(
                                sensor.get("name"),
                                start_time.isoformat(),
                                end_time.isoformat(),
                                self.data_resolution)
                            values = []
                            for table in query_results:
                                for record in table.records:
                                    values.append((record.get_time(), record.get_value()))
                            try:
                                result = TimeSeriesData(
                                    machine_id=sensor.get("machine"),
                                    sensor_name=sensor.get("name"),
                                    dt_start=values[0][0],
                                    dt_end=values[-1][0],
                                    values=values,
                                    customer_id="",
                                    module_id="",
                                    measurement_id="",
                                    modified_at=""
                                )
                                historic_sensor.historic_sensor_data = result
                            except IndexError:
                                print("Sensor " + sensor.get("name") + " failed to load")
                        self.historic_sensor_list.append(historic_sensor)

        finally:
            client_mongodb.close()

    def show_graph(self, dashboard, start_date_str, end_date_str, value, *args, **kwargs):
        start_datetime = datetime.fromisoformat(start_date_str)
        end_datetime = datetime.fromisoformat(end_date_str)
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.setup_historic_sensors(start_datetime, end_datetime)
        traces = []
        if value is not None:
            self.data_resolution = value

        for sensor in dashboard.get("sensors"):
            values = []
            timestamp = []
            for historic_sensor in self.historic_sensor_list:
                if historic_sensor.name == sensor.get("name") and \
                        historic_sensor.machine == sensor.get("machine") and \
                        dashboard.get("customer") == historic_sensor.customer and \
                        sensor.get("module") == historic_sensor.module:
                    if historic_sensor.historic_sensor_data is not None:
                        for sensor_info in historic_sensor.historic_sensor_data.values:
                            timestamp.append(sensor_info[0])
                            values.append(sensor_info[1])

            trace1 = go.Scatter(
                x=timestamp,
                y=values,
                name=sensor.get("name")
            )
            traces.append(trace1)
        return traces

    @subscribe(subject=Thing.get_subject('*'))
    async def _cb_received_data(self, subject: str, msg: Thing):
        self._logger.info("Received message from sensor %s: %s", msg.name, str(msg))
        for dashboard in self.config.get("dashboards"):
            for sensor in dashboard.get("sensors"):
                if sensor.get("name") == msg.name:
                    for live_sensor in self.live_sensor_list:
                        if sensor.get("name") == live_sensor.name:
                            live_sensor.live_sensors.append(msg)
                        live_sensor.clean_until(msg.timestamp, dashboard.get("time_shown"))


@dataclass
class GraphCallbacks:
    module: DashModule
    dashboard: {}

    def show_graph(self, *args, **kwargs):

        traces = self.module.show_graph(self.dashboard, *args, **kwargs)
        return {
            'data': traces,
            'layout':
                go.Layout(
                    title='Historic Data',
                    barmode='stack')
        }

    def update_graph(self, refresh, *args, **kwargs):
        if refresh == 'stop':
            return dash.no_update
        else:
            traces = self.module.update_graph(self.dashboard, *args, **kwargs)
            return {
                'data': traces,
                'layout':
                    go.Layout(
                        title='Live Data',
                        barmode='stack')
            }


if __name__ == '__main__':
    DashModule.main()
