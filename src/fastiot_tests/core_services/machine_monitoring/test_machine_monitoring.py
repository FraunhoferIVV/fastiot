import asyncio
import os
import tempfile
import threading
import unittest
from unittest.mock import patch, Mock

from opcua import Client, Server

from fastiot.core.broker_connection import NatsBrokerConnection
from fastiot.core.core_uuid import get_uuid
from fastiot.env.env import env_broker
from fastiot_core_services.machine_monitoring.env import env_opcua, FASTIOT_OPCUA_ENDPOINT_URL, \
    FASTIOT_OPCUA_RETRIEVAL_MODE, OPCUARetrievalMode, FASTIOT_MACHINE_MONITORING_CONFIG_NAME, \
    FASTIOT_OPCUA_SECURITY_STRING, FASTIOT_OPCUA_USER, FASTIOT_OPCUA_PASSWORD, FASTIOT_OPCUA_APPLICATION_URI, \
    FASTIOT_MACHINE_MONITORING_ERROR_LOGFILE, FASTIOT_OPCUA_MAX_ALLOWED_DATA_DELAY
from fastiot.env.env_constants import *
from fastiot.msg.thing import Thing
from fastiot.testlib import populate_test_env
from fastiot.util.ports import get_local_random_port
from fastiot_core_services.machine_monitoring.machine_monitoring_module import MachineMonitoring

module_id = "machine_monitoring"

_default_state_sensor_int = get_uuid()
_default_state_sensor_bool = get_uuid()
_default_var_sensor = get_uuid()
_default_zero_sensor = get_uuid()

_machine_monitoring_sensors = {
    _default_state_sensor_int:
        (_default_state_sensor_int, 'ns=2;i=3', 'MainEngineInt', 'sim_customer', 'MachineForTesting', 'MachPart1'),
    _default_state_sensor_bool:
        (_default_state_sensor_bool, 'ns=2;i=4', 'MainEngineBool', 'sim_customer', 'MachineForTesting', 'MachPart1'),
    _default_var_sensor:
        (_default_var_sensor, 'ns=2;i=5', 'SimVar', 'sim_customer', 'MachineForTesting', 'MachPart2'),
    _default_zero_sensor:
        (_default_var_sensor, 'ns=2;i=6', 'ZeroVar', 'sim_customer', 'MachineForTesting', 'MachPart2')
}


class TestMachineMonitoring(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        random_port = get_local_random_port()
        os.environ[FASTIOT_OPCUA_ENDPOINT_URL] = f"opc.tcp://127.0.0.1:{random_port}"
        cls._server_thread = threading.Thread(cls._start_server_cb(), daemon=True).start()

    @classmethod
    def _start_server_cb(cls):
        cls._server = Server()
        cls._server.set_endpoint(env_opcua.endpoint_url)
        cls._server.set_server_name("Sim OpcUa Machine - Object Server")

        # setup our own namespace, not really necessary but should as spec
        uri = "http://dummyMachine.device.io"
        cls._idx = cls._server.register_namespace(uri)

        cls._objects = cls._server.get_objects_node()
        machine_part1 = cls._objects.add_object(cls._idx, "MachPart1")
        machine_part2 = cls._objects.add_object(cls._idx, "MachPart2")

        cls._state_variable_int = machine_part1.add_variable(cls._idx, "MainEngineInt", 1)
        cls._state_variable_bool = machine_part1.add_variable(cls._idx, "MainEngineBool", False)
        cls._sim_variable = machine_part2.add_variable(cls._idx, "SimVar", 20)
        cls._zero_variable = machine_part2.add_variable(cls._idx, "ZeroVar", 0)
        cls._server.start()

    @classmethod
    def tearDownClass(cls):
        cls._server.stop()
        super().tearDownClass()

    async def asyncSetUp(self):
        populate_test_env()
        os.environ[FASTIOT_CONFIG_DIR] = os.path.dirname(__file__)
        self.broker_connection = await NatsBrokerConnection.connect()

    async def ascyncTearDown(self):
        del os.environ[FASTIOT_CONFIG_DIR]
        await self.broker_connection.close()

    async def test_machine_monitoring_empty_config(self):
        async with MachineMonitoring(broker_connection=self.broker_connection):
            self.assertTrue(True)

    async def test_publish_machine_data_msg_polling(self):
        os.environ[FASTIOT_OPCUA_RETRIEVAL_MODE] = OPCUARetrievalMode.polling.value
        await self._execute_publish_machine_data_msg()

    async def test_publish_machine_data_msg_subscription(self):
        os.environ[FASTIOT_OPCUA_RETRIEVAL_MODE] = OPCUARetrievalMode.subscription.value
        await self._execute_publish_machine_data_msg()

    async def _execute_publish_machine_data_msg(self):
        os.environ[FASTIOT_MACHINE_MONITORING_CONFIG_NAME] = 'config_default_sensor'

        msg_queue = asyncio.Queue()

        await self.broker_connection.subscribe_msg_queue(
            subject=Thing.get_subject(">"),
            msg_queue=msg_queue
        )
        async with MachineMonitoring(broker_connection=self.broker_connection):
            thing: Thing = await msg_queue.get()
            msg_queue.task_done()
            self.assertEqual('sim_machine', thing.machine)
            self.assertEqual('a_sensor', thing.name)
            self.assertEqual(20, thing.value)

    async def test_publish_multiple_machine_data_msg_polling(self):
        os.environ[FASTIOT_OPCUA_RETRIEVAL_MODE] = OPCUARetrievalMode.polling.value
        await self._execute_publish_multiple_machine_data_msg()

    async def test_publish_multiple_machine_data_msg_subscription(self):
        os.environ[FASTIOT_OPCUA_RETRIEVAL_MODE] = OPCUARetrievalMode.subscription.value
        await self._execute_publish_multiple_machine_data_msg()

    async def _execute_publish_multiple_machine_data_msg(self):
        os.environ[FASTIOT_MACHINE_MONITORING_CONFIG_NAME] = 'config_default_sensor'

        msg_queue = asyncio.Queue()
        await self.broker_connection.subscribe_msg_queue(
            subject=Thing.get_subject(">"),
            msg_queue=msg_queue
        )
        async with MachineMonitoring(broker_connection=self.broker_connection):
            thing: Thing = await asyncio.wait_for(msg_queue.get(), env_broker.default_timeout)
            msg_queue.task_done()
            self.assertEqual(20, thing.value)
            self._sim_variable.set_value(10)
            machine_data: Thing = await asyncio.wait_for(msg_queue.get(), env_broker.default_timeout)
            msg_queue.task_done()
            self.assertEqual(10, machine_data.value)
            self._sim_variable.set_value(20)

    async def test_publish_machine_data_zero_polling(self):
        os.environ[FASTIOT_OPCUA_RETRIEVAL_MODE] = OPCUARetrievalMode.polling.value
        await self._execute_publish_machine_data_zero()

    async def test_publish_machine_data_zero_subscription(self):
        os.environ[FASTIOT_OPCUA_RETRIEVAL_MODE] = OPCUARetrievalMode.subscription.value
        await self._execute_publish_machine_data_zero()

    async def _execute_publish_machine_data_zero(self):
        os.environ[FASTIOT_MACHINE_MONITORING_CONFIG_NAME] = 'config_zero_var_sensor'

        msg_queue = asyncio.Queue()

        await self.broker_connection.subscribe_msg_queue(
            subject=Thing.get_subject(">"),
            msg_queue=msg_queue
        )
        async with MachineMonitoring(broker_connection=self.broker_connection):
            thing: Thing = await msg_queue.get()
            msg_queue.task_done()
            self.assertEqual(0, thing.value)

    async def test_set_security_string(self):
        a_security_string = \
            "Basic256Sha256," \
            "Sign," \
            "/path/to/certificate/test_certificate.der," \
            "/path/to/key/test_key.pem"
        os.environ[FASTIOT_OPCUA_SECURITY_STRING] = a_security_string
        with patch.object(Client, 'set_security_string', new_callable=Mock) as mock:
            async with MachineMonitoring(broker_connection=self.broker_connection):
                pass

            self.assertEqual(1, mock.call_count)
            self.assertEqual(1, len(mock.call_args[0]))
            self.assertEqual(0, len(mock.call_args[1]))
            self.assertEqual(a_security_string, mock.call_args[0][0])
        del os.environ[FASTIOT_OPCUA_SECURITY_STRING]

    async def test_no_security_string(self):
        with patch.object(Client, 'set_security_string', new_callable=Mock) as mock:
            async with MachineMonitoring(broker_connection=self.broker_connection):
                pass
            self.assertEqual(0, mock.call_count)

    async def test_set_user_and_password(self):
        a_user = "user1"
        a_pw = "pw1"
        os.environ[FASTIOT_OPCUA_USER] = a_user
        os.environ[FASTIOT_OPCUA_PASSWORD] = a_pw
        with patch.object(Client, 'set_user', new_callable=Mock) as user_mock:
            with patch.object(Client, 'set_password', new_callable=Mock) as pw_mock:
                async with MachineMonitoring(broker_connection=self.broker_connection):
                    pass

        self.assertEqual(1, user_mock.call_count)
        self.assertEqual(1, len(user_mock.call_args[0]))
        self.assertEqual(0, len(user_mock.call_args[1]))
        self.assertEqual(a_user, user_mock.call_args[0][0])

        self.assertEqual(1, pw_mock.call_count)
        self.assertEqual(1, len(pw_mock.call_args[0]))
        self.assertEqual(0, len(pw_mock.call_args[1]))
        self.assertEqual(a_pw, pw_mock.call_args[0][0])

        del os.environ[FASTIOT_OPCUA_USER]
        del os.environ[FASTIOT_OPCUA_PASSWORD]

    async def test_no_application_uri(self):
        async with MachineMonitoring(broker_connection=self.broker_connection) as m:
            self.assertEqual('urn:freeopcua:client', m._opcua_client.application_uri)

    async def test_set_application_uri(self):
        an_application_uri = "sample"
        os.environ[FASTIOT_OPCUA_APPLICATION_URI] = an_application_uri
        async with MachineMonitoring(broker_connection=self.broker_connection) as m:
            self.assertEqual(an_application_uri, m._opcua_client.application_uri)
        del os.environ[FASTIOT_OPCUA_APPLICATION_URI]

    async def test_log_opcua_error(self):
        with tempfile.TemporaryDirectory() as tempdir:
            os.environ[FASTIOT_MACHINE_MONITORING_ERROR_LOGFILE] = os.path.join(tempdir, "error.log")
            os.environ[FASTIOT_OPCUA_MAX_ALLOWED_DATA_DELAY] = '0.1'
            try:
                async with MachineMonitoring(broker_connection=self.broker_connection):
                    # Make sure machine monitoring deletes file during start
                    self.assertFalse(os.path.isfile(env_opcua.machine_monitoring_error_logfile))
                    while os.path.isfile(env_opcua.machine_monitoring_error_logfile) is False:
                        await asyncio.sleep(0.01)

                with open(env_opcua.machine_monitoring_error_logfile) as f:
                    content = f.read()
                    pos = content.find('Receiving no data')
                    self.assertTrue(pos != -1)
            finally:
                del os.environ[FASTIOT_MACHINE_MONITORING_ERROR_LOGFILE]
                del os.environ[FASTIOT_OPCUA_MAX_ALLOWED_DATA_DELAY]


if __name__ == '__main__':
    unittest.main()
