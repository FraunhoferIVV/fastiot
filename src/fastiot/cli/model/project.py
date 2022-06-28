""" data model for project configuration """
import os
from typing import List, Optional, Dict
from enum import Enum
from glob import glob

from pydantic.main import BaseModel

from fastiot.cli.constants import DEPLOYMENTS_CONFIG_DIR, DEPLOYMENTS_CONFIG_FILE
from fastiot.cli.model import DeploymentConfig, ModuleConfig


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
    modules: List[ModuleConfig] = []
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

    def get_all_deployment_names(self) -> List[str]:
        """ Returns a list of all deployment names configured by configuration
        (:attr:`fastiot.cli.model.project.ProjectConfig.deploy_configs`) or by convention."""
        if self.deploy_configs:
            return self.deploy_configs

        deployments = glob(os.path.join(self.project_root_dir, DEPLOYMENTS_CONFIG_DIR, '*', DEPLOYMENTS_CONFIG_FILE))
        return [os.path.basename(os.path.dirname(d)) for d in deployments]

    def get_deployment_by_name(self, deployment_name: str) -> DeploymentConfig:
        """ Returns a specific deployment by its name. """
        deployment_file = os.path.join(self.project_root_dir, DEPLOYMENTS_CONFIG_DIR,
                                       deployment_name, DEPLOYMENTS_CONFIG_FILE)
        return DeploymentConfig.from_yaml_file(deployment_file)
