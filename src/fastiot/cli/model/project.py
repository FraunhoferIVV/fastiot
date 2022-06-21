import os
from glob import glob
from typing import List, Optional

from pydantic.main import BaseModel

from fastiot.cli.constants import DEPLOYMENTS_CONFIG_DIR, DEPLOYMENTS_CONFIG_FILE
from fastiot.cli.helper_fn import find_modules
from fastiot.cli.model import DeploymentConfig
from fastiot.cli.model.module import ModuleConfiguration


class ModulePackageConfig(BaseModel):
    """
    Definition of modules via a package name and a list of modules inside the package. Modules, which are not specified
    in the list, but are in the package are ignored.
    """
    package_name: str
    """The package name of the modules"""
    module_names: Optional[List[str]] = None
    """The module names as a list of strings. Leave empty to use all modules found in the package."""
    cache_name: Optional[str] = None
    """
    The name to use as the cache on the set docker cache registry. If not defined and a cache registry is configured 
    the `project_namespace:latest` will be used.  
    Example: mypackage-cache:latest
    """
    extra_caches: Optional[List[str]] = None
    """
    A list of extra caches used to speed up building. It is intended if you want to read from other caches or different 
    tags. Each extra cache must match a cache name extended by ':' followed by the tag for the cache. Per default no
    extra caches are used. You might find it useful to always include the cache name of the current module package 
    followed by tag latest to always use latest cache for feature branches.
    Examples: mypackage-cache:latest, fastiot-cache:latest, fastiot-cache:mybranch
    """


class ProjectConfig(BaseModel):
    """ This class holds all variables reade from :file:`configure.py` in the project root directory. """

    project_root_dir: str = os.getcwd()
    project_namespace: str
    library_package: Optional[str] = None
    library_setup_py_dir: str = os.getcwd()
    module_packages: Optional[List[ModulePackageConfig]] = None
    deploy_configs: Optional[List[str]] = None
    test_config: Optional[str]
    test_package: Optional[str]
    imports_for_test_config_environment_variables: Optional[List[str]] = None
    npm_test_dir: Optional[str] = None
    build_dir: str = 'build'
    extensions: Optional[List[str]] = None

    def get_all_modules(self) -> List[ModuleConfiguration]:
        """ Returns a list of all modules configured in the project """
        modules = list()
        for module_package in self.module_packages:
            if not module_package.module_names:
                module_package.module_names = find_modules(module_package.package_name, self.project_root_dir)
            for module_name in module_package.module_names:
                modules.append(ModuleConfiguration(name=module_name, module_package_name=module_package.package_name))

        return modules

    def get_module_package_by_name(self, package_name: str) -> ModulePackageConfig:
        for module_package in self.module_packages:
            if module_package.package_name == package_name:
                return module_package

        raise ValueError(f"Module Package {package_name} not found in project configuration.")

    def get_all_deployment_names(self) -> List[str]:
        if self.deploy_configs is not None:
            return self.deploy_configs
        else:
            deployments = (os.path.join(self.project_root_dir, DEPLOYMENTS_CONFIG_DIR))
            return [d for d in deployments if os.path.isdir(d)]

    def get_deployment_by_name(self, deployment_name: str) -> DeploymentConfig:
        deployment_file = os.path.join(self.project_root_dir, DEPLOYMENTS_CONFIG_DIR,
                                       deployment_name, DEPLOYMENTS_CONFIG_FILE)
        return DeploymentConfig.from_yaml_file(deployment_file)
