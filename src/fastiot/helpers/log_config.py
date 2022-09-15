import logging.config
from typing import Dict


def get_log_config(level: int = logging.INFO) -> Dict:
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
                'format': '%(asctime)s.%(msecs)03d: %(levelname)-8s %(name)s: %(message)s',
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
