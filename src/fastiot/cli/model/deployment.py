""" Data models for deployment configurations """
# pylint: disable=no-self-argument
import os
from typing import Dict, Optional

import yaml
from pydantic import BaseModel
from pydantic.class_validators import root_validator

from fastiot.util.case_conversions import kebab_case_to_snake_case


class InfrastructureServiceConfig(BaseModel):
    external: bool = False
    """
    Allows to mention services running on external servers and configured manually. This will avoid warnings in the
    setup process if services specified by the services as dependency could not be found.

    *Attention*: You need to manage the environment variables like host and port yourself if using ``external = True``.
    """


class ServiceConfig(BaseModel):
    """
    The config for a service
    """

    image: str
    """ The name defines which service is taken. Must contain possible namespace identifiers as a prefix,
    e.g. fastiot/time_series """
    docker_registry: str = ''
    """ The specified docker registry. If given it will override the docker_registry for the service, otherwise the
    locally  configured docker registry will be used."""
    tag: str = ''
    """ The specified tag. If given it will override the tag for the service """
    environment: Dict[str, str] = {}
    """ Includes all environment variables specifically for this service """


class AnsibleHost(BaseModel):
    """
    Represents a host for Ansible based deployments, used by
    :class:`fastiot.cli.models.deployment.DeploymentTargetSetup`
    """
    ip: str
    """ IP-Address (or DNS-resolvable hostname) where to find the host.

    You may also add additional parameters to be placed in the inventory (hosts) file for ansible like
     ``ansible_user=some_special_user`` directly following the string."""


class DeploymentTargetSetup(BaseModel):
    """
    Configuration options to generate ansible playbooks on the fly to deploy your project
    """
    hosts: Dict[str, AnsibleHost]
    """ A list with ansible hosts to deploy the setup to"""
    remote_user: Optional[str] = 'ubuntu'
    """ The remote user to use to logins for all hosts, defaults to ``ubuntu``"""
    link_prometheus: bool = False
    """ Set to ``True`` to enable automatically link the Prometheus-Client configuration copied by Ansible to host to
    the current project. Only works if you do *not* have :file:`docker-compose.override.yaml` in your deployment
    already."""

class DeploymentLogging(BaseModel):
    """
    Adjust docker-compose logging configuration if needed. The defaults should fit well
    """
    log_driver: str = "local"
    """
    Set a logging driver. The docker default is ``json-file`` with recommandation for ``local`` (used as default here)
    """
    max_size: Optional[str] = "10m"
    """ Maximum size for a single logfile, defaults to '10m' (10 MB) """
    max_file: Optional[int] = 5
    """ Maximum number of files to keep """
    additional_options: Dict[str, str] = {}
    """ Any additional options you may want to set for your selected driver """

class DeploymentConfig(BaseModel):
    """
    Represents an imported config. All fields are already overwritten specified command line parameters, currently
    including environment, docker_registry and tag
    """
    name: str
    version: int = 1
    services: Dict[str, Optional[ServiceConfig]] = {}
    """ List of services for the deployment """
    infrastructure_services: Dict[str, InfrastructureServiceConfig] = {}
    """ List of infrastructure services for the deployment """
    deployment_target: Optional[DeploymentTargetSetup] = None
    """ A deployment configuration to auto-generate Ansible Playbooks
    """
    docker_registry: str = ''
    """ Specify a docker registry which acts as a default registry for all services (not infrastructure services).
    Overrides any docker registry specified by CLI. """
    tag: str = ''
    """ Specify a docker tag which acts as a default tag for all services (not infrastructure services). Overrides any
    docker tag specified by CLI. """
    config_dir: str = './config_dir'
    """ Specify a config dir. The config dir will get mounted to /etc/fastiot

        It defaults to :file:`config_dir`
    """
    logging_config: DeploymentLogging = DeploymentLogging()

    @root_validator
    def check_services(cls, values):
        from fastiot.cli.model import InfrastructureService
        services = InfrastructureService.all

        for service in values.get("infrastructure_services"):
            if service not in services:
                raise ValueError(f"Service {service} not found in service list!")

        return values

    @staticmethod
    def from_yaml_file(filename) -> "DeploymentConfig":
        with open(filename, 'r') as config_file:
            config = yaml.safe_load(config_file)
            kebab_case_to_snake_case(config)
            if "infrastructure_services" in config:
                for item, value in config["infrastructure_services"].items():
                    if value is None:
                        config["infrastructure_services"][item] = InfrastructureServiceConfig()
        return DeploymentConfig(**{'name': os.path.basename(os.path.dirname(filename)), **config})

    def to_yaml_file(self, filename: str):
        with open(filename, 'w') as manifest_file:
            manifest_file.seek(0)
            yaml.safe_dump(self.dict(), manifest_file)
