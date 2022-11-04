""" data models for FastIoT and infrastructure services """
import os
from typing import Optional, List

from pydantic import BaseModel

from fastiot.cli.constants import MANIFEST_FILENAME
from fastiot.cli.model import ServiceManifest


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

    def read_manifest(self, check_service_name: str = "") -> ServiceManifest:
        """ Reads out the service manifest, if not run before using the yaml-file otherwise just ``self.manifest``"""
        from fastiot.cli.model.project import ProjectContext  # pylint: disable=import-outside-toplevel
        default_context = ProjectContext.default
        manifest_path = os.path.join(default_context.project_root_dir, 'src',
                                     self.package, self.name, MANIFEST_FILENAME)
        return ServiceManifest.from_yaml_file(manifest_path, check_service_name=check_service_name)
