""" data model for project configuration """
import os
from enum import Enum
from typing import Dict, List

from pydantic.main import BaseModel
import yaml

from fastiot.cli.constants import DEPLOYMENTS_CONFIG_DIR, DEPLOYMENTS_CONFIG_FILE
from fastiot.cli.model.deployment import DeploymentConfig
from fastiot.cli.model.service import Service
from fastiot.util.classproperty import classproperty


class CompileSettingsEnum(str, Enum):
    """ Different settings to define how to compile the library. """
    # pylint disable=invalid-name
    only_compiled = 'only_compiled'
    # Only provide a compiled version of the library
    only_source = 'only_source'
    # Only provide a source-version (.tar.gz and .whl)
    all_variants = 'all_variants'
    # Provide compiled and source version of the library


class ProjectContext(BaseModel):
    """
    This class holds all variables reade from :file:`configure.py` in the project root directory. Use this as for hints
    to do custom adjustments to your :file:`configure.py`. We try to set sensible defaults so that changes should only
    be needed in rare cases.
    """

    project_namespace: str = ''
    """ Namespace of the project used e.g. on the docker registry. This should be your project name."""

    project_root_dir: str = os.getcwd()
    """ Project root directory. As the cli is intended to be run from the project root directory the default using the
    current working directory should be fine."""

    library_package: str = ''
    """ Define a python package within your :file:`src` directory containing library methods to be shared between your
    services. If not specified no library will be built."""

    library_setup_py_dir: str = os.getcwd()
    """ Path where to find the :file:`setup.py` to build your library for exporting. The default with the current
     working directory should be fine, if you put your :file:`setup.py` at the toplevel of your project (common)."""

    services: List[Service] = []
    """ Define a list of :class:`fastiot.cli.model.service.ServiceConfig`. If not defined the cli will look for python
    packages containing a :file:`manifest.yaml` and a `run.py` with the pattern :file:`src/*/*/manifest.yaml` and call
    this package a FastIoT Service. Be aware of this when creating a :file:`manifest.yaml` somewhere, e.g. in your
    tests.

    *Hint:* If you want to override this configuration you may use :func:`fastiot.cli.helper_fn.find_services` to create
    a list of services to build by package."""

    deployments: Dict[str, DeploymentConfig] = {}
    """ Manually define a list of deployments as :class:`fastiot.cli.model.DeploymentConfig` to actually build using the
    command :meth:`fastiot.cli.commands.config.config`. If left empty all deployment configurations in the path
    :file:`deployments` will be used.

    *Hint:* You may use :func:`fastiot.cli.helper_fn.find_deployments` to create a list of deployments according to your
    special needs."""

    integration_test_deployment: str = ''
    """ If you need any services to be started for automatic testing your project you may define the name of this
    special deployment found within the :attr:`fastiot.cli.model.project.ProjectContext.deployments`."""

    test_package: str = ''
    """ Name of the package in the :file:`src` directory where automated tests are stored. Common is to use something
    like :file:`myproject_tests`."""

    npm_test_dir: str = ''

    build_dir: str = 'build'
    """ The dir where generated build files (Dockerfiles, Docker-compose files, etc.) are stored. This dir is relative
    to your project_root_dir.
    """

    extensions: List[str] = []
    """
    Use to add own extensions to the FastIoT CLI. The CLI will try to import your custom infrastructure services as
    described in :ref:`tut-custom_infrastructure_services`.

    Make sure importing this service will import further commands and
    :class:`fastiot.cli.model.infrastructure_service.InfrastructureService`.
    Most of the times this is done filling the :file:`__init__.py` correspondingly.
    """

    lib_compilation_mode: CompileSettingsEnum = CompileSettingsEnum.only_compiled
    """ Set to false if you do not want your library to be compiled (and obfuscated), use options from
    :class:`fastiot.cli.model.project.CompileSettingsEnum` """

    _default_context = None

    @classproperty
    def default(cls) -> "ProjectContext":
        """
        Use this method to retrieve the singleton :class:`fastiot.cli.model.project.ProjectContext`
        """
        if cls._default_context is None:
            cls._default_context = ProjectContext()
            from fastiot.cli.import_configure import import_configure
            import_configure(
                project_context=cls._default_context,
            )
        return cls._default_context

    # we need this line for Pycharm IDE to detect type-hinting properly. Maybe it is fixed in the future
    default: "ProjectContext"

    @property
    def deployment_names(self) -> List[str]:
        """ Returns a list of all deployment names configured by configuration
        (:attr:`fastiot.cli.model.project.ProjectContext.deployments`) or by convention in deployments dir."""
        return list(self.deployments.keys())

    def deployment_by_name(self, name: str) -> DeploymentConfig:
        """ Returns a specific deployment by its name. """
        deployment_file = os.path.join(self.deployment_dir(name=name), DEPLOYMENTS_CONFIG_FILE)
        return DeploymentConfig.from_yaml_file(deployment_file)

    def deployment_dir(self, name: str) -> str:
        """ Returns the deployment build dir for specific deployment """
        return os.path.join(self.project_root_dir, DEPLOYMENTS_CONFIG_DIR, name)

    def deployment_build_dir(self, name: str) -> str:
        """ Returns the deployment build dir for specific deployment """
        return os.path.join(self.project_root_dir, self.build_dir, DEPLOYMENTS_CONFIG_DIR, name)

    def env_file_for_deployment(self, name: str) -> str:
        return os.path.join(self.deployment_dir(name=name), '.env')

    def env_for_deployment(self, name: str) -> Dict[str, str]:
        env_filename = self.env_file_for_deployment(name=name)
        if os.path.isfile(env_filename):
            return parse_env_file(env_filename)

        return {}

    def build_env_file_for_deployment(self, name: str) -> str:
        return os.path.join(self.deployment_build_dir(name=name), '.env')

    def build_env_for_deployment(self, name: str) -> Dict[str, str]:
        env_filename = self.build_env_file_for_deployment(name=name)
        if os.path.isfile(env_filename):
            return parse_env_file(env_filename)

        return {}

    def build_env_for_internal_services_deployment(self, name: str) -> Dict[str, str]:
        docker_compose_file = os.path.join(self.deployment_build_dir(name=name), 'docker-compose.yaml')
        if os.path.isfile(docker_compose_file):
            with open(docker_compose_file) as file:
                result = yaml.safe_load(file)
                if 'x-env' in result:
                    return result['x-env']
                else:
                    return {}

        return {}

    def get_service_by_name(self, name: str) -> Service:
        """ Get a configured service from the project by name """
        for service in self.services:
            if service.name == name:
                return service
        raise ValueError(f"Service {name} not found in project services!")

    def get_all_service_names(self) -> List[str]:
        """ Returns a list of all configured services """
        if self.services:
            return [s.name for s in self.services]
        return []


def parse_env_file(env_filename: str) -> Dict[str, str]:
    environment = {}
    with open(env_filename, 'r') as stream:
        for i_line, line in enumerate(stream.readlines()):
            # need a space before '#' or e.g. password containing # will be split
            i_comment = line.find(' #')
            if i_comment != -1:
                line = line[0:i_comment]
            line = line.strip()
            if line == '' or line[0] == '#':
                continue
            parts = line.split('=', maxsplit=2)
            parts = [p.strip() for p in parts]
            log_info = f"Cannot parse env file: Invalid line {i_line + 1}: "
            if len(parts) == 1 or parts[0].replace("_", "").isalnum() is False:
                raise ValueError(f"{log_info}{line}")
            parts[1] = _parse_env_value(value=parts[1], log_info=log_info)
            environment[parts[0]] = parts[1]
    return environment

def _parse_env_value(value: str, log_info: str) -> str:
    """
    A mini parser which takes care of env value parsing including encapsulation of char " and char '
    """
    if len(value) == 0:
        return value
    if value.startswith(" "):
        raise ValueError(f"{log_info}Env value should not start with space")
    if value[0] not in ['"', "'"]:
        bracket = ""
    else:
        bracket = value[0]
        value = value[1:]
    parsed = []
    encapsulated = False
    parsing_finished = False
    for v in value:
        if parsing_finished == True:
            if value != ' ':
                raise ValueError(f"{log_info}Didn't expected char '{value}' because parsing is finished")
            encapsulated = False
            continue

        if encapsulated:
            encapsulated = False
            parsed.append(v)
        elif v == '\\':
            encapsulated = True
        elif v == bracket:
            parsing_finished = True
        else:
            parsed.append(v)
    if encapsulated:
        raise ValueError(f"{log_info}Didn't expect '\\' at end of var")
    return ''.join(parsed)
