import os
from typing import List, Optional, Dict

from pydantic.main import BaseModel


#class ModulePackageConfig(BaseModel):
#    """
#    Definition of modules via a package name and a list of modules inside the package. Modules, which are not specified
#    in the list, but are in the package are ignored.
#    """
#    package_name: str
#    """The package name of the modules"""
#    module_names: List[str] = []
#    """The module names as a list of strings. Leave empty to use all modules found in the package."""
#    cache_name: str = ''
#    """
#    The name to use as the cache on the set docker cache registry. If not defined and a cache registry is configured
#    the `[project_namespace]/[package_name]-cache:latest` will be used.
#    Example: mypackage-cache
#    """
#    extra_caches: List[str] = []
#    """
#    A list of extra caches used to speed up building. It is intended if you want to read from other caches or different
#    tags. Each extra cache must match a cache name extended by ':' followed by the tag for the cache. Per default no
#    extra caches are used. You might find it useful to always include the cache name of the current module package
#    followed by tag latest to always use latest cache for feature branches.
#    Examples: mypackage-cache:latest, fastiot-cache:latest, fastiot-cache:mybranch
#    """


class ModuleConfig(BaseModel):
    model_name: str
    package_name: str


class ProjectConfig(BaseModel):
    """ This class holds all variables reade from :file:`configure.py` in the project root directory. """

    project_root_dir: str = os.getcwd()
    project_namespace: str
    library_package: str = ''
    library_setup_py_dir: str = os.getcwd()
    module_configs: List[ModuleConfig] = []
    deploy_configs: List[str] = []
    test_config: str = ''
    test_package: str = ''
    imports_for_test_config_environment_variables: List[str] = []
    npm_test_dir: Optional[str] = ''
    build_dir: str = 'build'

    def all_modules(self) -> List[ModuleConfig]:
        configs = []
        for module_config in self.module_configs:
            configs.extend(module_config)
        return configs
