from typing import Optional
from fastiot.env import env_basic
from fastiot.util.log_config import get_log_config


def setup_logger(name: Optional[str] = 'root'):
    """
    This logging is a wrapper for logging from python, you can use it like following.
    Also the :envvar:`FASTIOT_LOG_LEVEL_NO` must be set to the expected level.
    s. https://docs.python.org/3/library/logging.html#logging-levels

    .. code:: python

      from fastiot import logging

      logging.debug('debug message')
      logging.info('info message')

    """
    import logging.config
    logging.config.dictConfig(get_log_config(env_basic.log_level_no))
    return logging.getLogger(name)


logging = setup_logger()
