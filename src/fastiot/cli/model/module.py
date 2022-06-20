import os
from typing import Optional

from pydantic import BaseModel

from fastiot.cli.model import ModuleManifest


class ModuleConfiguration(BaseModel):
    name: str
    module_package_name: str
    manifest: Optional[ModuleManifest] = None

    def read_manifest(self, check_module_name: str = "") -> ModuleManifest:
        from fastiot.cli.model.context import get_default_context

        default_context = get_default_context()
        manifest_path = os.path.join(default_context.project_config.project_root_dir, 'src',
                                     self.module_package_name, self.name, 'manifest.yaml')
        self.manifest = ModuleManifest.from_yaml_file(manifest_path, check_module_name=check_module_name)
        return self.manifest
