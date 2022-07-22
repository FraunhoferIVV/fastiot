import os


FASTIOT_OPCUA_EXAMPLE_PORT = 'FASTIOT_OPCUA_EXAMPLE_PORT'


class OpcUaServerModuleConstants:

    @property
    def server_port(self) -> int:
        """ ..envvar:: FASTIOT_OPCUA_EXAMPLE_PORT

        Set the port the OPC UA Server from the sample module :mod:`fastiot_sample_services.opc_ua_server` listens to.
        """
        return int(os.environ.get(FASTIOT_OPCUA_EXAMPLE_PORT, 4840))


env_opc_ua_server = OpcUaServerModuleConstants()
