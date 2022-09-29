import glob
import os
from pathlib import Path
from typing import Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from fastiot.cli.constants import TEMPLATES_DIR, DEPLOYMENTS_CONFIG_DIR, DEPLOYMENTS_CONFIG_FILE, MANIFEST_FILENAME
from fastiot.cli.model import Service, DeploymentConfig


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


def find_services(package: Optional[str] = None,
                  path: Optional[str] = None,
                  services: Optional[List[str]] = None,
                  use_per_service_cache: bool = False) -> List[Service]:
    """
    Find services in a package

    :param package: The package name within your :file:`src`. If not defined the whole :path:`src` will be searched for
                    suitable services containing a :file:`manifest.yaml` and a :file:`run.py`
    :param path: Optional, specify a search path, uses ``os.getcwd()`` as default
    :param services: Optional; if specified it will only include the listed services
    :param use_per_service_cache: If enabled, it will use per service caches. This is useful if different services use
                                 different Dockerfiles.
    """
    path = path or os.getcwd()
    package = package or '*'

    found_services = []
    for manifest_filename in glob.glob(os.path.join(path, 'src', package, '*', MANIFEST_FILENAME)):
        manifest_path = Path(manifest_filename)
        service_directory = manifest_path.parent
        service_name = service_directory.name

        if services and service_name not in services:
            continue

        package_name = service_directory.parent.name
        if not os.path.isfile(os.path.join(service_directory.absolute(), 'run.py')):
            continue

        found_services.append(Service(name=service_name,
                                      package=package_name,
                                      cache=_default_cache(service=service_name, package=package_name,
                                                           use_per_service_cache=use_per_service_cache),
                                      extra_caches=_default_extra_caches(service=service_name, package=package_name,
                                                                         use_per_service_cache=use_per_service_cache)))
    return found_services


def find_deployments(deployments: Optional[List[str]] = None, path: str = '') -> Dict[str, DeploymentConfig]:
    """
    Creates a dict of all deployments found the projects :file:`deployments` path.

    :param deployments: Optional, specify a list of deployments to be exclusively included
    :param path: Optional, specify a search path, uses ``os.getcwd()`` as default
    """
    path = path or os.getcwd()

    deploy_configs = {}
    for config_filename in glob.glob(os.path.join(path, DEPLOYMENTS_CONFIG_DIR, '*', DEPLOYMENTS_CONFIG_FILE)):
        deployment_name = os.path.basename(os.path.dirname(config_filename))
        if not deployments or deployment_name in deployments:
            deploy_configs[deployment_name] = DeploymentConfig.from_yaml_file(config_filename)
    return deploy_configs


def _default_cache(package: str, service: str, use_per_service_cache: bool) -> str:
    if use_per_service_cache:
        return f"{package}-{service}-cache"
    return f"{package}-cache"


def _default_extra_caches(package: str, service: str, use_per_service_cache: bool) -> List[str]:
    return [_default_cache(package=package, service=service, use_per_service_cache=use_per_service_cache) + ':latest']
