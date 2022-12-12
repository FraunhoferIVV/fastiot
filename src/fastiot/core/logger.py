from typing import Optional, Dict
from fastiot.env import env_basic


def setup_logger(name: Optional[str] = 'root'):
    """
    This logging is a wrapper for logging from python, you can use it like following.
    Also the :envvar:`FASTIOT_LOG_LEVEL` must be set to the expected level.
    s. https://docs.python.org/3/library/logging.html#logging-levels

    .. code:: python

      from fastiot import logging

      logging.debug('debug message')
      logging.info('info message')

    """
    from logging import getLogger, config  # pylint:disable=import-outside-toplevel
    config.dictConfig(get_log_config(env_basic.log_level))
    return getLogger(name)


def get_log_config(level: int = 20) -> Dict:
    """
    This function is used to set the logging configuration globally,
    now the console log should have this format:
    timestamp: LOG_LEVEL     module name: Log message
    If the log should be saved to a file, this configuration can also be modified by using logging.Filehandler.
    """
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s.%(msecs)03d: %(levelname)-8s %(filename)s:%(lineno)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'level': level,
                'formatter': 'standard',
                'class': 'logging.StreamHandler'
            }
        },
        'loggers': {
            'root': {
                'level': level,
                'handlers': ['console']
            }
        }
    }


logging = setup_logger()
