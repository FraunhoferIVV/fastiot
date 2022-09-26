from fastiot import logging
from fastiot.core import FastIoTService, Subject, subscribe
from fastiot_core_services.nats_logger.env import nats_logger_env as env


class NatsLoggerService(FastIoTService):

    @subscribe(subject=Subject(name=env.subject,
                               msg_cls=dict))
    async def _on_data_received(self, subject_name: str, msg: dict):
        if env.filter_field is None or str(msg.get(env.filter_field)) == env.filter_value:
            logging('NatsLoggerService').info("%s: %s", subject_name, str(msg))


if __name__ == '__main__':
    NatsLoggerService.main()
