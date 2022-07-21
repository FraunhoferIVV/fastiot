import os


FASTIOT_OPCUA_EXAMPLE_PORT = 'FASTIOT_OPCUA_EXAMPLE_PORT'


class OpcUaServerModuleConstants:

    @property
    def server_port(self) -> int:
        return int(os.environ.get(FASTIOT_OPCUA_EXAMPLE_PORT, 4840))


env_opc_ua_server = OpcUaServerModuleConstants()
