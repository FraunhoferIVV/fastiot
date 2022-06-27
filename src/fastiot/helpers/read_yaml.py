""" Providing methods to import yaml configuration per module"""

import logging
import os
from typing import Optional, Dict, Union, Type

import yaml

from fastiot.core.app import FastIoTApp
from fastiot.env import env_basic


def get_config_file_name(module: Union[FastIoTApp, str]) -> Optional[str]:
    """
    Find the yaml config file for the given module.

    If both module.yaml and module_id.yaml exist, module_id.yaml will be preferred.

    :param module: Module to load the config for (preferred) or name of the config file.
    :return: Filename. May be None if no file was found.
    """

    if isinstance(module, str):
        config_file = os.path.join(env_basic.config_dir, f"{module}")  # Look for file in SAM config
        if os.path.isfile(config_file):
            return config_file
        if (module.startswith("/") or module.startswith(".")) and os.path.isfile(module):
            # An absolute or relative path was provided, so we don’t have to look in the module configuration
            return module

        logging.getLogger("yaml_config").warning("Provided config file %s could not be found.", module)
    else:
        module_name = module.__class__.__name__
        module_id = module.module_id

        config_file_per_module = os.path.join(env_basic.config_dir, f"{module_name}.yaml")
        config_file_per_instance = os.path.join(env_basic.config_dir, f"{module_name}_{module_id}.yaml")

        if os.path.isfile(config_file_per_instance):
            return config_file_per_instance
        if os.path.isfile(config_file_per_module):
            return config_file_per_module

        logging.getLogger("yaml_config").warning("No configuration for module %s was found in %s!",
                                                 module_name, env_basic.config_dir)
    return None


def read_config(module: Union[Type[FastIoTApp], str]) -> Dict:
    """
    Load YAML-configuration files based on file or, preferably, module name.

    :param module: Module to load the config for (preferred) or name of the config file.
    :return: Dictionary with the loaded configuration. May be empty if no configuration was found.
    """

    config_file = get_config_file_name(module)
    if config_file is None:
        return {}

    try:
        with open(config_file) as file:
            loader = yaml.safe_load_all(file)
            result = [x for x in loader]
    except:
        logging.getLogger("yaml_config").warning("Could not open or parse yaml file %s", config_file)
        return {}

    if not result:
        logging.getLogger("yaml_config").warning("Could not parse yaml file %s", config_file)
        return {}
    logging.getLogger("yaml_config").info("Successfully read configuration %s", config_file)
    return result[0]
