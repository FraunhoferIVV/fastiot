from fastiot.cli.version import get_version
from fastiot.logger import logging
from fastiot.cli.commands import *
from fastiot.cli.common.infrastructure_services import *

try:
    from fastiot.__version__ import __version__
except ImportError:
    __version__ = get_version(complete=True)
