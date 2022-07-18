import logging

from fastiot.core.app import FastIoTService
from fastiot.core.app_annotations import subscribe
from fastiot.core.data_models import Subject
from fastiot_core_services.nats_logger.env import nats_logger_env as env


class NatsLoggerService(FastIoTService):

    @subscribe(subject=Subject(name=env.subject,
                               msg_cls=dict))
    async def _data_received_cb(self, data: dict):
        if env.filter_field is None or getattr(data, env.filter_field) == env.filter_value:
            logging.info(str(data))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    NatsLoggerService.main()
