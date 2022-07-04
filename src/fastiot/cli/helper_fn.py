import importlib
import os
from typing import Dict, Optional, List

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from fastiot.cli.constants import TEMPLATES_DIR
from fastiot.cli.model import ServiceConfig


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


def find_services(package: str,
                  services: Optional[List[str]] = None,
                  use_per_service_cache: bool = False) -> List[ServiceConfig]:
    """
    Find services in a package

    :param package: The package name. Can be a nestet namespace, e.g. 'mypackage.modules'
    :param services: Optional; if specified it will only include the listed services
    :param use_per_service_cache: If enabled, it will use per service caches. This is useful if different services use
                                 different Dockerfiles.
    """
    p = importlib.import_module(package)
    package_dir = os.path.dirname(p.__file__)
    configs = []
    for m in os.listdir(package_dir):
        if os.path.isfile(os.path.join(package_dir, m, 'manifest.yaml')):
            if services is None or m in services:
                service = import_service(
                    package=package,
                    name=m,
                    use_per_service_cache=use_per_service_cache
                )
                configs.append(service)
    return configs


def import_service(package: str,
                   name: str,
                   use_per_service_cache: bool = False) -> ServiceConfig:
    """
    Import a module

    :param package: The package name. Can be a nestet namespace, e.g. 'mypackage.modules'
    :param name: The name of the module
    :param use_per_service_cache: If enabled, it will include the module name into the caches; therefore using per module
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
    return ServiceConfig(
        name=name,
        package=package,
        cache=default_cache(service=name, package=package, use_per_service_cache=use_per_service_cache),
        extra_caches=default_extra_caches(service=name, package=package, use_per_service_cache=use_per_service_cache)
    )


def default_cache(package: str, service: str, use_per_service_cache: bool) -> str:
    if use_per_service_cache:
        return f"{package}-{service}-cache"
    return f"{package}-cache"


def default_extra_caches(package: str, service: str, use_per_service_cache: bool) -> List[str]:
    return [default_cache(package=package, service=service, use_per_service_cache=use_per_service_cache) + ':latest']
