"""
.. deprecated:: 0.9.29
   This module is deprecated. Please refer to :mod:`fastiot.util.config_helper` instead.
"""
from typing import Union, Optional, Dict
from warnings import warn

from fastiot.core import FastIoTService
from fastiot.util.config_helper import _get_config_file_name as __get_config_file_name, read_config as _read_config


def _get_config_file_name(service: Union[FastIoTService, str]) -> Optional[str]:
    """
    Find the yaml config file for the given service.

     .. deprecated:: 0.9.29
        Please use :meth:`fastiot.util.config_helper._get_config_file_name` instead now.
    """
    warn('The method `fastiot.util.read.yaml._get_config_file_name` is deprecated. Please use '
         '`fastiot.util.config_helper._get_config_file_name` instead.', DeprecationWarning, stacklevel=2)

    return __get_config_file_name(service=service)


def read_config(service: Union[FastIoTService, str]) -> Dict:
    """
    Load YAML-configuration files based on file (provide string) or, preferably, service.

     .. deprecated:: 0.9.29
        Please use :meth:`fastiot.util.config_helper.read_config` instead now.
    """
    warn('The method `fastiot.util.read.yaml.read_config` is deprecated. Please use '
         '`fastiot.util.config_helper.read_config` instead.', DeprecationWarning, stacklevel=2)

    return _read_config(service=service)
