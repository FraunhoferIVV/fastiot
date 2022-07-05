""" Data models for deployment configurations """
# pylint: disable=no-self-argument
import os
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel
from pydantic.class_validators import root_validator, validator


class InfrastructureServiceConfig(BaseModel):
    external: bool = False
    """ 
    Allows to mention services running on external servers and configured manually. This will avoid warnings in the
    setup process if services specified by the services as dependency could not be found.
    """


class ServiceConfig(BaseModel):
    """
    The config for a service
    """

    image: str
    """ The name defines which service is taken. Must contain possible namespace identifiers as a prefix, 
    e.g. fastiot/time_series """
    docker_registry: str = ''
    """ The specified docker registry. If given it will override the docker_registry for the service """
    tag: str = ''
    """ The specified tag. If given it will override the tag for the service """
    environment: Dict[str, str] = {}
    """ Includes all environment variables for the service """

    @property
    def is_local_docker_registry(self) -> bool:
        return self.docker_registry == ''

    @property
    def docker_registry_image_prefix(self) -> str:
        if self.is_local_docker_registry:
            return ""

        return f"{self.docker_registry}/"

    @property
    def full_image_name(self) -> str:
        return f"{self.docker_registry_image_prefix}{self.image}:{self.tag}"


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


class DeploymentConfig(BaseModel):
    """
    Represents an imported config. All fields are already overwritten specified command line parameters, currently
    including environment, docker_registry and tag
    """
    name: str
    """ Name of the deployment. This should always be the directory name where the corresponding :file:`deployment.yaml`
    is located. """
    version: int = 1
    services: Dict[str, Optional[ServiceConfig]] = {}
    """ List of services for the deployment """
    infrastructure_services: Dict[str, Optional[InfrastructureServiceConfig]] = []
    """ List of infrastructure services for the deployment """
    deployment_target: Optional[DeploymentTargetSetup]
    """ A deployment configuration to auto-generate Ansible Playbooks
    """
    docker_registry: str = ''
    """ Specify a docker registry which acts as a default registry for all services (not infrastructure services). 
    Overrides any docker registry specified by CLI. """
    tag: str = ''
    """ Specify a docker tag which acts as a default tag for all services (not infrastructure services). Overrides any
    docker tag specified by CLI """
    config_dir: str = ''
    """ Specify a config dir. The config dir will get mounted to /etc/fastiot """

    @root_validator
    def check_services(cls, values):
        try:
            from fastiot.cli.infrastructure_service_helper import get_services_list
            services = get_services_list()
        except AttributeError:
            return values  # If the project is not configured completely this will fail
        for service in values.get("infrastructure_services"):
            if service not in services.keys():
                raise ValueError(f"Service {service} not found in service list!")
        return values

    @staticmethod
    def from_yaml_file(filename) -> "DeploymentConfig":
        with open(filename, 'r') as config_file:
            config = yaml.safe_load(config_file)
        return DeploymentConfig(**{'name': os.path.basename(os.path.dirname(filename)), **config})
