import logging
from datetime import datetime
from random import randint

import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go

from fastiot.core.service import FastIoTService
from fastiot.core.service_annotations import subscribe
from fastiot.core.data_models import Subject
from fastiot.msg.thing import Thing
from fastiot_sample_services.dash.utils import ServerThread


class DashModule(FastIoTService):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._subscriptions = []

        self.app = dash.Dash()
        self._setup_dash()

        self.server = ServerThread(self.app.server)

        self._received_values = []

    async def _start(self):
        """ Methods to start once the module is initialized """
        self.server.start()

    async def _stop(self):
        """ Methods to call on module shutdown """
        self.server.shutdown()

    def _setup_dash(self):
        self.app.layout = html.Div([
            html.H1("Some Data"),
            dcc.Graph(id='graph'),
            dcc.Interval(
                id='interval-component',
                interval=1 * 1000,  # in milliseconds
                n_intervals=0
            )
        ])

        # Hooking up callbacks takes place here. Keep in mind the not so common syntax at the end `(self._update_graph)`
        self.app.callback(dash.dependencies.Output('graph', 'figure'),
                          dash.dependencies.Input('interval-component', 'n_intervals'))(self._update_graph)

    def _update_graph(self, n_intervals):
        trace1 = go.Scatter(x=[i for i, _ in enumerate(self._received_values)],
                            y=self._received_values)

        random_value = randint(1, 50)
        fancy_value: Thing = self.broker_connection.request_sync(subject=Subject(name='reply_test',
                                                                                 msg_cls=Thing, reply_cls=Thing),
                                                                 msg=Thing(machine="Test_Machine",
                                                                           name='Some_Sensor',
                                                                           value=random_value,
                                                                           timestamp=datetime.now()),
                                                                 timeout=10)
        #fancy_value = Thing(machine="Test_Machine", name='Some_Sensor', value=random_value, timestamp=datetime.now())

        trace2 = go.Scatter(x=list(range(20)),
                            y=10 * [random_value, fancy_value.value])

        return {
            'data': [trace1, trace2],
            'layout':
                go.Layout(
                    title='Some Data',
                    barmode='stack')
        }

    @subscribe(subject=Thing.get_subject('*'))
    async def _cb_received_data(self, subject: str, msg: Thing):
        logging.info("Received message from sensor %s: %s", msg.name, str(msg))
        self._received_values.append(msg.value)
        self._received_values = self._received_values[-20:]


if __name__ == '__main__':
    DashModule.main()
