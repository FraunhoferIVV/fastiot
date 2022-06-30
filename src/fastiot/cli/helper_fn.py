import importlib
import logging
import os
import sys
from glob import glob
from typing import Dict, Optional, List

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from fastiot.cli.constants import TEMPLATES_DIR
from fastiot.cli.model import ModuleConfig


def parse_env_file(env_filename: str) -> Dict[str, str]:
    environment = {}
    with open(env_filename, 'r') as stream:
        for i_line, line in enumerate(stream.readlines()):
            # need a space before '#' or e.g. password containing # will be split
            i_comment = line.find(' #')
            if i_comment != -1:
                line = line[0:i_comment]
            line = line.strip()
            if line == '' or line[0] == '#':
                continue
            parts = line.split('=', maxsplit=2)
            parts = [p.strip() for p in parts]
            if len(parts) == 1 or parts[0].replace("_", "").isalnum() is False:
                raise ValueError(f"Cannot parse env file: Invalid line {i_line + 1}: {line}")
            environment[parts[0]] = parts[1]
    return environment


_jinja_env = None


def get_jinja_env():
    global _jinja_env
    if _jinja_env is None:
        _jinja_env = Environment(
            loader=FileSystemLoader(searchpath=TEMPLATES_DIR),
            trim_blocks=True,
            undefined=StrictUndefined
        )
    return _jinja_env


def find_modules(package: str,
                 modules: Optional[List[str]] = None,
                 use_per_module_cache: bool = False) -> List[ModuleConfig]:
    """
    Find modules in a package

    :param package: The package name. Can be a nestet namespace, e.g. 'mypackage.modules'
    :param modules: Optional; if specified it will only include the listed modules
    :param use_per_module_cache: If enabled, it will use per module caches. This is useful if different modules use
                                 different Dockerfiles.
    """
    p = importlib.import_module(package)
    package_dir = os.path.dirname(p.__file__)
    configs = []
    for m in os.listdir(package_dir):
        if os.path.isfile(os.path.join(package_dir, m, 'manifest.yaml')):
            if modules is None or m in modules:
                module = import_module(
                    package=package,
                    name=m,
                    use_per_module_cache=use_per_module_cache
                )
                configs.append(module)
    return configs


def import_module(package: str,
                  name: str,
                  use_per_module_cache: bool = False) -> ModuleConfig:
    """
    Import a module

    :param package: The package name. Can be a nestet namespace, e.g. 'mypackage.modules'
    :param name: The name of the module
    :param use_per_module_cache: If enabled, it will include the module name into the caches; therefore using per module
                                 caches. This is useful if different modules use different Dockerfiles.
    """
    if package:
        full_name = package + '.' + name
    else:
        full_name = name

    m = importlib.import_module(full_name)
    package_dir = os.path.dirname(m.__file__)
    if not os.path.isfile(os.path.join(package_dir, 'manifest.yaml')):
        raise RuntimeError(f"Expected a manifest file at '{os.path.join(package_dir, 'manifest.yaml')}'")
    return ModuleConfig(
        name=name,
        package=package,
        cache=default_cache(module=name, package=package, use_per_module_cache=use_per_module_cache),
        extra_caches=default_extra_caches(module=name, package=package, use_per_module_cache=use_per_module_cache)
    )


def default_cache(package: str, module: str, use_per_module_cache: bool) -> str:
    if use_per_module_cache:
        return f"{package}-{module}-cache"
    else:
        return f"{package}-cache"


def default_extra_caches(package: str, module: str, use_per_module_cache: bool) -> List[str]:
    return [default_cache(package=package, module=module, use_per_module_cache=use_per_module_cache) + ':latest']
