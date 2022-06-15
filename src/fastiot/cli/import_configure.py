import glob
import importlib.util
import os
import sys
from typing import Optional

from fastiot.cli.constants import CONFIGURE_FILE_NAME
from fastiot.cli.model import ProjectConfig


def import_configure(file_name: Optional[str] = None) -> ProjectConfig:
    """ Imports the :file:`configure.py` in the project root (if not specified otherwise) and returns  """
    config = _import_configure_py(file_name)

    deploy_configs = glob.glob(os.path.join(os.getcwd(), 'deployments'))
    deploy_configs = [os.path.basename(d) for d in deploy_configs]

    data = dict()
    for field, options in ProjectConfig.__dict__['__fields__'].items():
        if hasattr(config, field):
            data[field] = getattr(config, field)
        elif options.required:
            raise ValueError(f"Error reading configure.py: Mandatory setting for {field} not found!")
        else:
            data[field] = options.default

    # Use all available configs if not specified otherwise
    data['deploy_configs'] = data['deploy_configs'] or deploy_configs

    return ProjectConfig(**data)


def _import_configure_py(file_name):
    file_name = file_name or os.path.join(os.getcwd(), CONFIGURE_FILE_NAME)
    spec = importlib.util.spec_from_file_location("config", file_name)
    config = importlib.util.module_from_spec(spec)
    sys.modules["config"] = config
    spec.loader.exec_module(config)
    return config
