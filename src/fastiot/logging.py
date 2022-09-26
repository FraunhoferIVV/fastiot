
from fastiot.env import env_basic
from fastiot.helpers.log_config import get_log_config


def logging(name: str = None):
    """
    This logging is a wrapper for logging from python, you can use it like following.
    Also the :envvar:`FASTIOT_LOG_LEVEL_NO` must be set to the expected level.
    s. https://docs.python.org/3/library/logging.html#logging-levels

    .. code:: python

      from fastiot import logging

      logger = logging(name='my_service/my_function')


    """
    import logging.config
    logging.config.dictConfig(get_log_config(env_basic.log_level_no))
    return logging.getLogger(name)
