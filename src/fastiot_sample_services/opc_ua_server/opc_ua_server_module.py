import logging

from asyncua import Server

from fastiot.core import FastIoTService, subscribe
from fastiot.msg.thing import Thing
from fastiot_sample_services.opc_ua_server.env import env_opc_ua_server


class OpcUaServerService(FastIoTService):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server = Server()

    async def _init_server(self):
        await self.server.init()
        self.server.set_endpoint(f'opc.tcp://0.0.0.0:{env_opc_ua_server.server_port}/freeopcua/server/')

        uri = 'http://examples.freeopcua.github.io'
        self.idx = await self.server.register_namespace(uri)

        # populating our address space
        # server.nodes, contains links to very common nodes like objects and root
        object = await self.server.nodes.objects.add_object(self.idx, 'MyObject')
        self.opc_ua_variable = await object.add_variable(self.idx, 'LastThingValue', 0)

        # Set MyVariable to be writable by clients
        # await myvar.set_writable()
        logging.info("Server setup complete, now starting Server")

        await self.server.start()

    async def _start(self):
        """ Methods to start once the module is initialized """

        await self._init_server()

    async def _stop(self):
        """ Methods to call on module shutdown """

        await self.server.stop()

    @subscribe(subject=Thing.get_subject('*'))
    async def _cb_received_data(self, _: str, msg: Thing):
        await self.opc_ua_variable.write_value(msg.value)
        logging.info("Received message from sensor %s: %s", msg.name, str(msg))
