""" data model for project configuration """
import os
from enum import Enum
from typing import List, Optional

from pydantic.main import BaseModel

from fastiot.cli.constants import DEPLOYMENTS_CONFIG_DIR, DEPLOYMENTS_CONFIG_FILE
from fastiot.cli.model.deployment import DeploymentConfig
from fastiot.cli.model.service import ServiceConfig


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
    This class holds all variables reade from :file:`configure.py` in the project root directory. Use this as for hints
    to do custom adjustments to your :file:`configure.py`. We try to set sensible defaults so that changes should only
    be needed in rare cases.
    """

    project_namespace: str
    """ Namespace of the project used e.g. on the docker registry. This should be your project name."""

    project_root_dir: str = os.getcwd()
    """ Project root directory. As the cli is intended to be run from the project root directory the default using the
    current working directory should be fine."""

    library_package: Optional[str] = None
    """ Define a python package within your :file:`src` directory containing library methods to be shared between your
    services. If not specified no library will be built."""

    library_setup_py_dir: str = os.getcwd()
    """ Path where to find the :file:`setup.py` to build your library for exporting. The default with the current
     working directory should be fine, if you put your :file:`setup.py` at the toplevel of your project (common)."""

    services: Optional[List[ServiceConfig]] = []
    """ Define a list of :class:`fastiot.cli.model.service.ServiceConfig`. If not defined the cli will look for python
    packages containing a :file:`manifest.py` and a `run.py` with the pattern :file:`src/*/*/manifest.py` and call this
    package a FastIoT Service. Be aware of this when creating a :file:`manifest.py` somewhere, e.g. in your tests. This
    may bring the system to fail!
    
    *Hint:* If you want to override this configuration you may use :func:`fastiot.cli.helper_fn.find_services` to create
    a list of services to build by package."""

    deploy_configs: Optional[List[DeploymentConfig]] = []
    """ Manually define a list of deployments as :class:`fastiot.cli.model.DeploymentConfig` to actually build using the
    command :meth:`fastiot.cli.commands.config.config`. If left empty all deployment configurations in the path
    :file:`deployments` will be used.
    
    *Hint:* You may use :func:`fastiot.cli.helper_fn.find_deployments` to create a list of deployments according to your special
    needs."""

    test_config: Optional[str]
    """ If you need any services to be started for automatic testing your project you may define the name of this
    special deployment found within the :attr:`fastiot.cli.model.project.ProjectConfig.deploy_configs`."""

    test_package: Optional[str]
    """ Name of the package in the :file:`src` directory where unittests are stored. Common is to use something like
    :file:`myproject_tests`."""

    imports_for_test_deployment_env_vars: Optional[List[str]] = None
    npm_test_dir: Optional[str] = None

    build_dir: str = 'build'
    """ If you do not want to store generated build files (Dockerfiles, …) in the directory :file:`build` in your
    project root, please change!"""

    extensions: Optional[List[str]] = []
    """ Use to add own extensions to the fastapi CLI. The CLI will try to import your services. Make sure importing
    this service will import further commands and :class:`fastiot.cli.model.service.InfrastructureService`. Most of the
    times this is done filling the :file:`__init__.py` correspondingly."""

    compile_lib: Optional[CompileSettingsEnum] = CompileSettingsEnum.only_compiled
    """ Set to false if you do not want your library to be compiled (and obfuscated), use options from
    :class:`fastiot.cli.model.project.CompileSettingsEnum` """

    def get_all_deployment_names(self) -> List[str]:
        """ Returns a list of all deployment names configured by configuration
        (:attr:`fastiot.cli.model.project.ProjectConfig.deploy_configs`) or by convention in deployments dir."""

        return [d.deployment_name for d in self.deploy_configs]

    def get_deployment_by_name(self, deployment_name: str) -> DeploymentConfig:
        """ Returns a specific deployment by its name. """
        deployment_file = os.path.join(self.project_root_dir, DEPLOYMENTS_CONFIG_DIR,
                                       deployment_name, DEPLOYMENTS_CONFIG_FILE)
        return DeploymentConfig.from_yaml_file(deployment_file)

    def get_all_service_names(self) -> List[str]:
        """ Returns a list of all configured services """
        if self.services:
            return [s.name for s in self.services]
        return []
