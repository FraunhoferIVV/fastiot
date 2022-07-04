""" data model for external services """
import os
from typing import Dict, Union, Optional, List

from pydantic import BaseModel

from fastiot.cli.model import ServiceManifest


class ServiceConfig(BaseModel):
    name: str
    package: str
    cache: str
    """
    The name to use as the cache on the set docker cache registry. The tag will be appended automatically, please do not
    specify it.
    Example: mypackage-cache
    """
    extra_caches: List[str]
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
            from fastiot.cli.model.context import get_default_context  # pylint: disable=import-outside-toplevel

            default_context = get_default_context()
            manifest_path = os.path.join(default_context.project_config.project_root_dir, 'src',
                                         self.package, self.name, 'manifest.yaml')
            self.manifest = ServiceManifest.from_yaml_file(manifest_path, check_service_name=check_service_name)
        return self.manifest


class InfrastructureService(BaseModel):
    """ Class to describe external services to be integrated in the deployments. """
    name: str  # Name of the external service, e.g. mariadb. Per convention these names should be in lower case
    docker_image: str  # Name of the docker image to be put in the :file:`docker-compose.yaml`
    port: int  # Default port of the service exposed by its docker image
    port_env_var: str
    """ Environment variable to read the port number, as for internal purposes the port number may change """
    password_env_var: Optional[str]  # If the service needs a password use this env
    additional_env: Optional[Dict[str, Union[str, int]]] = None
    """ Provide any additional environment variables to be set here as a dictionary with the variable name and a
    sensible default. """
