import logging.config
from typing import Dict


def get_log_config(level: int = logging.INFO) -> Dict:
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
