import os
from typing import Optional, List

from pydantic import BaseModel

from fastiot.cli.model import ModuleManifest


class ModuleConfig(BaseModel):
    name: str
    package: str
    cache: str = ''
    """
    The name to use as the cache on the set docker cache registry. If not defined and a cache registry is configured
    the `project_namespace:latest` will be used.
    Example: mypackage-cache
    """
    extra_caches: List[str] = []
    """
    A list of extra caches used to speed up building. It is intended if you want to read from other caches or different
    tags. Each extra cache must match a cache name extended by ':' followed by the tag for the cache. Per default no
    extra caches are used. You might find it useful to always include the cache name of the current module package
    followed by tag latest to always use latest cache for feature branches.
    Examples: mypackage-cache:latest, fastiot-cache:latest, fastiot-cache:mybranch
    """
    manifest: Optional[ModuleManifest] = None

    def read_manifest(self, check_module_name: str = "") -> ModuleManifest:
        """ Reads out the module manifest, if not run before using the yaml-file otherwise just ``self.manifest``"""
        if self.manifest is None:
            from fastiot.cli.model.context import get_default_context  # pylint: disable=import-outside-toplevel

            default_context = get_default_context()
            manifest_path = os.path.join(default_context.project_config.project_root_dir, 'src',
                                         self.package, self.name, 'manifest.yaml')
            self.manifest = ModuleManifest.from_yaml_file(manifest_path, check_module_name=check_module_name)
        return self.manifest
