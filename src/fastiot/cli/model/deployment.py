from typing import Dict, List, Optional

import yaml
from pydantic.class_validators import root_validator, validator
from pydantic.main import BaseModel


class ModuleDeploymentConfig(BaseModel):
    """
    The config for a module
    """

    image_name: str
    """The name defines which module is taken. Contains namespace identifier as a prefix, e.g. fastiot/time_series """
    service_name: Optional[str]
    """The service name defines how this module is named in compose file. Useful if one image is used many times within 
    on deployment. Will be set to image_name if not specified. """
    docker_registry: Optional[str] = None
    """The specified docker registry"""
    tag: Optional[str] = 'latest'
    """The specified tag, defaults to `latest` if not specified."""
    environment: Optional[Dict[str, str]] = dict()
    """Includes all environment variables for the module"""
    environment_modifications: Optional[Dict[str, str]]
    """Includes all environment variables which are specified for this module specifically"""

    @root_validator
    def check_create_service_name(cls, values):
        values['service_name'] = values['service_name'] or values['image_name']
        return values

    @property
    def is_local_docker_registry(self) -> bool:
        return self.docker_registry == ''

    @property
    def docker_registry_image_prefix(self) -> str:
        if self.is_local_docker_registry:
            return ""
        else:
            return f"{self.docker_registry}/"

    @property
    def docker_image_name(self) -> str:
        return f"{self.docker_registry_image_prefix}{self.image_name}:{self.tag}"


class AnsibleHost(BaseModel):
    """
    Represents a host for Ansible based deployments, used by
    :class:`fastiot.cli.models.deployment.DeploymentTargetSetup`
    """
    name: str
    """ Readable name of the host"""
    ip: str
    """ IP-Address (or DNS-resolvable hostname) where to find the host. 

    You may also add additional parameters to be placed in the inventory (hosts) file for ansible like
     ``ansible_user=some_special_user``."""


class DeploymentTargetSetup(BaseModel):
    """
    Configuration options to generate ansible playbooks on the fly to deploy your project
    """
    hosts: List[AnsibleHost]
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

    deployment_config_version: int = 1
    modules: Dict[str, Optional[ModuleDeploymentConfig]] = {}
    """ List of modules to integrate in the deployment."""
    services: Optional[List[str]] = list()
    """ List of services to integrate """
    services_external: Optional[List[str]] = list()
    """ Allows to mention services running on external servers and configured manually. This will avoid warnings in the 
    setup process if services specified by the modules as dependency could not be found. 
    """
    deployment_target: Optional[DeploymentTargetSetup]
    """ A deployment configuration to auto-generate Ansible Playbooks
    """
    docker_registry: Optional[str] = ""
    tag: Optional[str] = 'latest'
    """ Define the tag to use for all docker images, defaults to ``latest``."""
    config_dir: Optional[str]

    @validator('modules')
    def module_defaults(cls, v):
        for module_name, module in v.items():
            if module is None:
                # TODO: Don't do this: Validate function should not manipulate objects
                v[module_name] = ModuleDeploymentConfig(image_name=module_name)
        return v

    @root_validator
    def check_services(cls, values):
        for service_list in [values.get("services"), values.get("services_external")]:
            for service in service_list:
                # TODO: Reference to context to find available services.
                pass
                #if service not in context.services:
                #    raise()
        return values

    @staticmethod
    def from_yaml_file(filename) -> "DeploymentConfig":
        with open(filename, 'r') as config_file:
            config = yaml.safe_load(config_file)
        return DeploymentConfig(**config)
