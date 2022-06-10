import glob
import importlib.util
import os
import sys
from typing import Optional

from fastiot.cli.model import ProjectConfiguration

CONFIGURE_FILE_NAME = 'configure.py'


def import_configure(file_name: Optional[str] = None) -> ProjectConfiguration:
    """ Imports the :file:`configure.py` in the project root (if not specified otherwise) and returns  """
    file_name = file_name or os.path.join(os.getcwd(), CONFIGURE_FILE_NAME)

    spec = importlib.util.spec_from_file_location("config", file_name)
    config = importlib.util.module_from_spec(spec)
    sys.modules["config"] = config
    spec.loader.exec_module(config)

    def _read_from_config(argument, optional=True):
        if hasattr(config, argument):
            return getattr(config, argument)
        else:
            if optional:
                return None
            else:
                raise ValueError(f"Error reading configure.py: Mandatory setting for {argument} not found!")

    deploy_configs = glob.glob(os.path.join(os.getcwd(), 'deployments'))
    deploy_configs = [os.path.basename(d) for d in deploy_configs]

    return ProjectConfiguration(project_root_dir=_read_from_config("project_root_dir") or os.getcwd(),
                                project_namespace=_read_from_config("project_namespace", optional=False),
                                library_package=_read_from_config("library_package"),
                                library_setup_py_dir=_read_from_config("library_setup_py_dir") or os.getcwd(),
                                module_packages=_read_from_config("module_packages"),
                                custom_modules=_read_from_config('custom_modules'),
                                deploy_configs=_read_from_config('deploy_configs') or deploy_configs,
                                test_config=_read_from_config('test_config'),
                                test_package=_read_from_config('test_package'),
                                imports_for_test_config_environment_variables=_read_from_config(
                                    'imports_for_test_config_environment_variables'),
                                npm_test_dir=_read_from_config('npm_test_dir')
                                )

