import asyncio
from dataclasses import dataclass
import os
from typing import Any, Dict, Optional

from opcua import Client

from fastiot.core import FastIoTService, loop
from fastiot.core.time import get_time_now
from fastiot.env.env import env_opcua
from fastiot.env.model import OPCUARetrievalMode
from fastiot.msg.thing import Thing
from fastiot_core_services.machine_monitoring.extract_thing_metadata import extract_thing_metadata_from_csv


class MachineMonitoring(FastIoTService):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._loop = asyncio.get_event_loop()
        self._thing_queue = asyncio.Queue()
        self._mainloop_wait_condition = asyncio.Condition()
        self._data_received_event_for_max_allowed_data_delay = asyncio.Event()
        self._things: Dict[str, Thing] = {}
        self._load_config()

    def _load_config(self):
        config_dir = env_opcua.machine_monitoring_config_dir
        if os.path.isdir(config_dir):
            self._logger.info("Importing from csv")
            things_filename = os.path.join(config_dir, "machine_monitoring_things.csv")

            if os.path.isfile(things_filename):
                for thing in extract_thing_metadata_from_csv(things_filename):
                    if thing.name in self._things:
                        self._logger.warning(f'Thing with name "{thing.name}" skipped because it is '
                                             f'already included')
                    else:
                        self._things[thing.name] = thing
                self._logger.info(f'File "{things_filename}" successfully imported.')
            else:
                self._logger.info(f'File "{things_filename}" does not exist. Skipping import of sensors.')

        else:
            self._logger.warning(f'Config dir "{config_dir}" does not exist')

    async def _start(self):
        if env_opcua.max_allowed_data_delay > 0.0:
            self._logger.info("Opcua max allowed data delay is set.")
        else:
            self._logger.info("Opcua max allowed data delay is not set.")

        self._setup_opcua_client()

        if len(self._things) > 0:
            if env_opcua.retrieval_mode is OPCUARetrievalMode.subscription:
                self._setup_monitoring_subscriptions()
            elif env_opcua.retrieval_mode is OPCUARetrievalMode.polling:
                self.run_task(self._poll_monitored_node_values())
            else:
                raise NotImplementedError()

    def _setup_opcua_client(self):
        self._opcua_client = Client(url=env_opcua.endpoint_url)

        if env_opcua.security_string:
            self._opcua_client.set_security_string(env_opcua.security_string)

        if env_opcua.user:
            self._opcua_client.set_user(env_opcua.user)

        if env_opcua.password:
            self._opcua_client.set_password(env_opcua.password)

        if env_opcua.application_uri:
            self._opcua_client.application_uri = env_opcua.application_uri

        self._opcua_client.connect()
        self._opcua_client_subscription = None

    def _setup_monitoring_subscriptions(self):
        opcua_nodes = []
        for thing in self._things.values():
            opcua_node = self._opcua_client.get_node(thing.name)
            opcua_nodes.append(opcua_node)

        self._opcua_client_subscription = self._opcua_client.create_subscription(0, self)
        self._opcua_client_subscription.subscribe_data_change(opcua_nodes)

    def datachange_notification(self, node, val, data):
        sensor_data = self._things[node.nodeid.to_string()]
        self._apply_changes_to_thing(sensor_data, val)

    async def _poll_monitored_node_values(self):
        while await self.wait_for_shutdown(0.2) is False:
            for thing in self._things.values():
                opc_node = self._opcua_client.get_node(thing.name)
                val = opc_node.get_value()
                self._apply_changes_to_thing(thing, val)

                if self._shutdown_event.is_set() is True:
                    # if a large amount of sensors is polled; evaluating shutdown
                    # after each poll ensures responsiveness in case of shutdown request
                    break

    @loop
    async def _mainloop_cb(self):
        while self._thing_queue.qsize() > 0:
            enqueued_thing: Thing = await self._thing_queue.get()
            self._thing_queue.task_done()

            await self.broker_connection.publish(
                subject=enqueued_thing.get_subject(),
                msg=enqueued_thing
            )
            self._data_received_event_for_max_allowed_data_delay.set()

        async with self._mainloop_wait_condition:
            await self._mainloop_wait_condition.wait()

        return asyncio.sleep(0)

    @loop
    async def _check_max_allowed_data_delay_cb(self):
        if not env_opcua.max_allowed_data_delay:
            return asyncio.Event().wait()

        self._data_received_event_for_max_allowed_data_delay.clear()
        try:
            await asyncio.wait_for(
                self._data_received_event_for_max_allowed_data_delay.wait(), env_opcua.max_allowed_data_delay
            )
        except asyncio.TimeoutError:
            self._logger.error("Receiving no data. Writing to opcua error logfile.")

            error_log_dir = os.path.dirname(env_opcua.machine_monitoring_error_logfile)
            if os.path.isdir(error_log_dir) is False:
                os.makedirs(error_log_dir)
            with open(env_opcua.machine_monitoring_error_logfile, "a") as f:
                f.write(f"{get_time_now()} Receiving no data.\n")
        return asyncio.sleep(0.0)

    def _apply_changes_to_thing(self, thing: Thing, new_val):
        if thing.value == new_val:
            return

        thing.value = new_val
        thing.timestamp = get_time_now()
        self._enqueue_thing(thing=thing)

    def _enqueue_thing(self, thing: Thing):
        asyncio.run_coroutine_threadsafe(
            self._put_into_queue(queue=self._thing_queue, msg=thing.copy(deep=True)),
            self._loop
        )

    async def _put_into_queue(self, queue: asyncio.Queue, msg: Any):
        await queue.put(msg)
        async with self._mainloop_wait_condition:
            self._mainloop_wait_condition.notify_all()

    async def _stop(self):
        self._data_received_event_for_max_allowed_data_delay.set()
        self._opcua_client.disconnect()

        async with self._mainloop_wait_condition:
            self._mainloop_wait_condition.notify_all()
