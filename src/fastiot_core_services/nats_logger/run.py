import logging

from fastiot_core_services.nats_logger.nats_logger_module import NatsLoggerService

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    NatsLoggerService.main()
