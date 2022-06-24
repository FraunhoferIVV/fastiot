""" data model for project configuration """
import os
from enum import Enum
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
    """ The package name of the modules"""
    module_names: Optional[List[str]] = None
    """ The module names as a list of strings. Leave empty to use all modules found in the package."""
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


class CompileSettingsEnum(str, Enum):
    """ Different settings to define how to compile the library. """
    # pylint disable=invalid-name
    only_compiled = 'only_compiled'
    # Only provide a compiled version of the library
    only_source = 'only_source'
    # Only provide a source-version (.tar.gz and .whl)
    all_variants = 'all_variants'
    # Provide compiled and source version of the library


class ProjectConfig(BaseModel):
    """
    This class holds all variables reade from :file:`configure.py` in the project root directory. """
    project_namespace: str
    """ Namespace of the project used e.g. on the docker registry. This should be your project name."""

    project_root_dir: str = os.getcwd()
    """ Project root directory. As the cli is intended to be run from the project root directory the default using the
    current working directory should be fine."""

    library_package: Optional[str] = None
    """ Define a python package within your :file:`src` directory containing library methods to be shared between your
    services. If not specified no library will be built. """
    library_setup_py_dir: str = os.getcwd()
    """ Path where to find the :file:`setup.py` to build your library for exporting. The default with the current
     working directory should be fine, if you put your :file:`setup.py` at the toplevel of your project (common)."""
    module_packages: Optional[List[ModulePackageConfig]] = []
    """ Define a list of :class:`fastiot.cli.model.project.ModulePackageConfig` where to find your services. Most
    projects will most probably only contain a single ModulePackage. This is optional if you, for example, only want
    to build a library using the framework."""
    deploy_configs: Optional[List[str]] = []
    """ Manually define a list of deployments to actually build using the command
    :meth:`fastiot.cli.commands.config.config`. If left empty all deployment configurations in the path
    :file:`deployments` will be used."""
    test_config: Optional[str]
    """ If you need any services to be started for automatic testing your project you may define the name of this
    special deployment found within the :attr:`fastiot.cli.model.project.ProjectConfig.deploy_configs`."""
    test_package: Optional[str]
    """ Name of the package in the :file:`src` directory where unittests are stored. Common is to use something like
    :file:`myproject_tests`."""
    imports_for_test_config_environment_variables: Optional[List[str]] = None
    npm_test_dir: Optional[str] = None
    build_dir: str = 'build'
    """ If you do not want to store generated build files (Dockerfiles, …) in the directory :file:`build` in your
    project root, please change!"""
    extensions: Optional[List[str]] = []
    """ Use to add own extensions to the fastapi CLI. The CLI will try to import your modules. Make sure importing
    this module will import further commands and :class:`fastiot.cli.model.service.ExternalService`. Most of the times
    this is done filling the :file:`__init__.py` correspondingly."""
    compile_lib: Optional[CompileSettingsEnum] = CompileSettingsEnum.only_compiled
    """ Set to false if you do not want your library to be compiled (and obfuscated), use options from
    :class:`fastiot.cli.model.project.CompileSettingsEnum` """

    def get_all_modules(self) -> List[ModuleConfiguration]:
        """ Returns a list of all modules configured in the project """
        modules = []
        for module_package in self.module_packages:
            if not module_package.module_names:
                module_package.module_names = find_modules(module_package.package_name, self.project_root_dir)
            for module_name in module_package.module_names:
                modules.append(ModuleConfiguration(name=module_name, module_package_name=module_package.package_name))

        return modules

    def get_module_package_by_name(self, package_name: str) -> ModulePackageConfig:
        """ Get a :class:`fastiot.cli.model.project.ModulePackageConfig` by its name."""
        for module_package in self.module_packages:
            if module_package.package_name == package_name:
                return module_package

        raise ValueError(f"Module Package {package_name} not found in project configuration.")

    def get_all_deployment_names(self) -> List[str]:
        """ Returns a list of all deployment names configured by configuration
        (:attr:`fastiot.cli.model.project.ProjectConfig.deploy_configs`) or by convention."""
        if not self.deploy_configs is not None and self.deploy_configs != []:
            return self.deploy_configs

        deployments = glob(os.path.join(self.project_root_dir, DEPLOYMENTS_CONFIG_DIR, '*', 'deployment.yaml'))
        return [os.path.basename(os.path.dirname(d)) for d in deployments]

    def get_deployment_by_name(self, deployment_name: str) -> DeploymentConfig:
        """ Returns a specific deployment by its name. """
        deployment_file = os.path.join(self.project_root_dir, DEPLOYMENTS_CONFIG_DIR,
                                       deployment_name, DEPLOYMENTS_CONFIG_FILE)
        return DeploymentConfig.from_yaml_file(deployment_file)
