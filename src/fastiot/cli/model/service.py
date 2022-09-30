""" data models for FastIoT and infrastructure services """
import os
from typing import Dict, Optional, List

from pydantic import BaseModel

from fastiot.cli.constants import MANIFEST_FILENAME
from fastiot.cli.model import ServiceManifest
from fastiot.util.classproperty import classproperty


class Service(BaseModel):
    """
    The model class for a service
    """
    name: str
    package: str
    cache: str = ""
    """
    The name to use as the cache on the set docker cache registry. The tag will
    be appended automatically (in case not empty), please do not specify it.
    Example: mypackage-cache
    """
    extra_caches: List[str] = []
    """
    A list of extra caches used to speed up building which will all be read-only. It is intended if you want to read
    from other caches or different tags. Each extra cache must match a cache name extended by ':' followed by the tag
    for the cache. It is useful to always include the cache name followed by tag latest to always use latest cache for
    feature branches.
    Examples: mypackage-cache:latest, mypackage-cache:my-feature
    """
    manifest: Optional[ServiceManifest] = None

    def read_manifest(self, check_service_name: str = "") -> ServiceManifest:
        """ Reads out the service manifest, if not run before using the yaml-file otherwise just ``self.manifest``"""
        if self.manifest is None:
            from fastiot.cli.model.project import ProjectContext  # pylint: disable=import-outside-toplevel
            default_context = ProjectContext.default
            manifest_path = os.path.join(default_context.project_root_dir, 'src',
                                         self.package, self.name, MANIFEST_FILENAME)
            self.manifest = ServiceManifest.from_yaml_file(manifest_path, check_service_name=check_service_name)
        return self.manifest


class InfrastructureServiceEnvVar(BaseModel):
    name: str
    """ The name of the infrastructure service env var """
    default: str
    """ The default value for the infrastructure service env var """
    env_var: str = ''
    """ The env var which can be used for modification. If empty it cannot be modified, therefore is static for the
    infrastructure service """


class InfrastructureServicePort(BaseModel):
    container_port: int
    """ The port inside the container """
    default_port_mount: int
    """ The default port for mounting """
    env_var: str = ''
    """ The env var which can be used for port mount modification. If given, this env var will also be provided to all
    services with the given container port so they can connect to the service """


class InfrastructureServiceVolume(BaseModel):
    container_volume: str
    """ The volume inside the container """
    default_volume_mount: str = 'tmpfs'
    """ The default location to mount the volume to. A value of 'tmpfs' will mount the container to a
    temporary file system inside the RAM. """
    env_var: str
    """ The env var which can be used for volume mount modification. """


class InfrastructureService(BaseModel):
    """
    Class to describe external services to be integrated in the deployments.

    Please refer to :ref:`tut-own_infrastructure_services` for more information on adding your own infrastructure to
    your project.
    """
    name: str = ""
    """ Name of the external service, e.g. mariadb. Per convention these names should be in lower case """
    image: str = ""
    """ Name of the image """
    environment: List[InfrastructureServiceEnvVar] = []
    host_name_env_var: str = ""
    """ The environment variable setting the hostname. This variable needs special attention: When working in a
    local development environment this defaults to localhost. Within a docker network the value needs to be the
    docker-internal hostname. """
    password_env_vars: List[str] = []
    """ List of environment variables containing a password. Those will be filled with random passwords for new
     projects automatically. """
    ports: List[InfrastructureServicePort] = []
    volumes: List[InfrastructureServiceVolume] = []

    @classproperty
    def all(cls) -> Dict[str, "InfrastructureService"]:
        """ Method to get a dict of all available services as instantiated
        :class:`fastiot.cli.model.service.InfrastructureService`.

        To append own services you simply have to inherit from this class and put them into your project. Then import
        those parts using :attr:`fastiot.cli.model.project.ProjectConfig.extensions`. This method will try to import
        anything from there and for services.
        """
        service_classes = InfrastructureService.__subclasses__()
        i_service_class = 0
        while i_service_class < len(service_classes):
            for subcls in service_classes[i_service_class].__subclasses__():
                if subcls not in service_classes:  # We have to check for multiple inheritance
                    service_classes.append(subcls)
            i_service_class += 1
        services_list = [s() for s in service_classes]
        services = {s.name: s for s in services_list}
        return {k: services[k] for k in sorted(services.keys())}

    # we need this line for Pycharm IDE to detect type-hinting properly. Maybe it is fixed in the future
    all: Dict[str, "InfrastructureService"]

    def get_default_env(self, name: str) -> str:
        """ Will return the default set for the given FastIoT environment variable."""
        var = [e for e in self.environment if e.env_var == name]
        if not var:
            raise ValueError(f"Environment variable {name} not found.")

        return var[0].default

    def get_default_port(self, name: Optional[str] = "") -> int:
        """
        Will return the default value for the given FastIoT port by environment variable.
        If you leave out the name the first port configured will be returned.
        """
        if not self.ports:
            raise ValueError(f"No ports configured for service {self.name}")

        if not name:
            return self.ports[0].default_port_mount

        var = [e for e in self.ports if e.env_var == name]
        if not var:
            raise ValueError(f"Port {name} not found.")
        return var[0].default_port_mount

