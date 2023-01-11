import io
from dataclasses import dataclass
from datetime import datetime, timedelta, date

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from flask import send_file

from fastiot.core import FastIoTService, subscribe
from fastiot.db.influxdb_helper_fn import influx_query_wrapper, influx_query
from fastiot.db.mongodb_helper_fn import get_mongodb_client_from_env
from fastiot.env import env_mongodb
from fastiot.msg.thing import Thing
from fastiot.util.read_yaml import read_config
from fastiot_core_services.dash.env import env_dash
from fastiot_core_services.dash.model.historic_sensor import HistoricSensor
from fastiot_core_services.dash.model.live_sensor import LiveSensor
from fastiot_core_services.dash.utils import ServerThread, thing_series_from_mongodb_data_set, \
    thing_series_from_influxdb_data_set


class DashModule(FastIoTService):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = read_config(self)
        self.live_sensor_list = []
        self.historic_sensor_list = []
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], prevent_initial_callbacks=True)
        self.server = ServerThread(self.app.server)
        self.setup_live_sensors()
        self.start_datetime = None
        self.end_datetime = None
        self._mongo_collection = None

    async def _start(self):
        """ Methods to start once the module is initialized """
        self.server.start()
        self._logger.info('=== Started Dash Service at %s:%s ===', env_dash.dash_host, env_dash.dash_port)
        self.initial_start_date = self.initial_date(self.config.get("initial_start_date"))
        self.initial_end_date = self.initial_date(self.config.get("initial_end_date"))
        self._setup_dash()
        self.setup_historic_sensors(self.initial_start_date, self.initial_end_date)

        await self._setup_mongodb()

    async def _setup_mongodb(self):
        configured_databases = [d.get('db') for d in self.config['dashboards']]
        if "mongodb" in configured_databases:
            client_mongodb = get_mongodb_client_from_env()
            mongodb = client_mongodb.get_database(env_mongodb.name)
            self._mongo_collection = mongodb.get_collection(self.config.get("collection"))

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

    def setup_historic_sensors(self, start_time: datetime, end_time: datetime):
        self.historic_sensor_list.clear()
        for dashboard in self.config.get("dashboards"):
            if not dashboard.get("live_data"):
                for sensor in dashboard.get("sensors"):
                    historic_sensor = HistoricSensor(sensor.get("name"),
                                                     sensor.get("machine"),
                                                     dashboard.get("customer"),
                                                     sensor.get("service")
                                                     )
                    if "mongodb" in dashboard.get("db"):
                        result = self._mongo_collection.find({
                            "name": historic_sensor.name,
                            "machine": historic_sensor.machine,
                            'timestamp': {'$gte': start_time, '$lte': end_time}
                        })
                        r = list(result)
                        self._logger.info(f'got results from mongodb is {r}')
                        historic_sensor.historic_sensor_data = thing_series_from_mongodb_data_set(r)
                        historic_sensor.historic_sensor_data.remove_until(start_time)
                        historic_sensor.historic_sensor_data.remove_from(end_time)
                    elif "influxdb" in dashboard.get("db"):
                        query_results = influx_query_wrapper(
                            influx_query,
                            sensor.get("machine"),
                            sensor.get("name"),
                            start_time.isoformat(),
                            end_time.isoformat())
                        historic_sensor.historic_sensor_data = \
                            thing_series_from_influxdb_data_set(query_results.to_json())
                    self.historic_sensor_list.append(historic_sensor)

    def download_excel(self, *args, **kwargs):
        if self.start_datetime and self.end_datetime and self.historic_sensor_list:
            self._logger.info("Download excel file from %s to %s", str(self.start_datetime), str(self.end_datetime))
            self.setup_historic_sensors(self.start_datetime, self.end_datetime)
            df = HistoricSensor.to_df(historic_sensor_list=self.historic_sensor_list)

            # Convert DF
            str_io = io.BytesIO()
            excel_writer = pd.ExcelWriter(str_io, engine='xlsxwriter')
            df.to_excel(excel_writer, sheet_name='labor')
            excel_writer.save()
            excel_data = str_io.getvalue()
            str_io.seek(0)
            return send_file(str_io, as_attachment=True,
                             download_name=f'{self.start_datetime}-{self.end_datetime} Data.xlsx')

        self._logger.warning('Please set the start_datetime and end_datetime in DatePicker first '
                             'to download the excel file')

    def show_graph(self, dashboard, start_date_str, end_date_str, value, *args, **kwargs):
        start_datetime = datetime.fromisoformat(start_date_str)
        end_datetime = datetime.fromisoformat(end_date_str)
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.setup_historic_sensors(start_datetime, end_datetime)
        traces = []

        for sensor in dashboard.get("sensors"):
            values = []
            timestamps = []
            for historic_sensor in self.historic_sensor_list:
                if historic_sensor.name == sensor.get("name") and \
                        historic_sensor.machine == sensor.get("machine") and \
                        dashboard.get("customer") == historic_sensor.customer and \
                        sensor.get("service") == historic_sensor.service:
                    if historic_sensor.historic_sensor_data.thing_list:
                        for thing in historic_sensor.historic_sensor_data.thing_list:
                            timestamps.append(thing.timestamp)
                            values.append(thing.value)

            trace1 = go.Scatter(
                x=timestamps,
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
