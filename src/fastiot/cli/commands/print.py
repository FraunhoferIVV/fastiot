from enum import Enum
from typing import Optional, List

import typer

from fastiot.cli.infrastructure_service_fn import get_services_list
from fastiot.cli.model import ProjectConfig
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import app, DEFAULT_CONTEXT_SETTINGS


class ToPrint(str, Enum):
    project_namespace = 'project_namespace'
    library_package = 'library_package'
    library_setup_py_dir = 'library_setup_py_dir'
    services = 'services'
    deployments = 'deployments'
    integration_test_deployment = 'integration_test_deployment'
    test_package = 'test_package'
    npm_test_dir = 'npm_test_dir'


_name_help = """
Name can be any of:\n
* project_namespace ... prints the project namespace.\n
* library_package ... prints the specified library package.\n
* library_setup_py_dir ... prints the library directory which includes the setup.py. If unset, nothing will be 
printed.\n
* services ... prints all services which can be built.\n
* deployments ... prints all deploy configs.\n
* integration_test_deployment ... prints the name of the test integration deployment.\n
* test_package ... prints the package for testing.\n
* npm_test_dir ... prints the npm dir for testing.\n
"""


def check_name(name: str):
    included = True
    try:
        ToPrint(name)
    except ValueError:
        included = False

    if included is False:
        raise typer.BadParameter(f"Parameter for name is not valid: '{name}'")
    return name


def _name_completion() -> List[str]:
    return [e.value for e in ToPrint]


@app.command('print', context_settings=DEFAULT_CONTEXT_SETTINGS)
def print_cmd(name: str = typer.Argument(..., help=_name_help, callback=check_name, shell_complete=_name_completion),
              deployment: Optional[str] = typer.Option(None,
                                                       help="Only applicable if <name> is services. If specified, "
                                                            "it doesn't print services which are not needed for the "
                                                            "deployment."),
              platform: Optional[str] = typer.Option(None,
                                                     help="Only applicable if <name> is services. If "
                                                          "specified, it doesn't print services which cannot be built "
                                                          "for the platform. Can be used together with --deployment "
                                                          "flag.")):
    project_config = get_default_context().project_config
    platforms = platform.split(',') if platform else []
    if name == 'project_namespace':
        print(project_config.project_namespace)
    elif name == 'library_package':
        if project_config.library_package:
            print(project_config.library_package)
    elif name == 'library_setup_py_dir':
        if project_config.library_setup_py_dir:
            print(project_config.library_setup_py_dir)
    elif name == 'services':
        if deployment is not None:
            deployment_obj = project_config.deployment_by_name(deployment)
            print("\n".join(deployment_obj.services))
        else:
            for service in project_config.services:
                if len(platforms) > 0:
                    manifest = service.read_manifest()
                    platforms_in_manifest = [p.value for p in manifest.platforms]
                    if len([p for p in platforms if p in platforms_in_manifest]) == 0:
                        continue
                print(service.name)
    elif name == 'deployments':
        for deployment in project_config.deployments:
            print(deployment.name)
    elif name == 'integration_test_deployment':
        if project_config.integration_test_deployment:
            print(project_config.integration_test_deployment)
    elif name == 'test_package':
        if project_config.test_package:
            print(project_config.test_package)
    elif name == 'npm_test_dir':
        if project_config.npm_test_dir:
            print(project_config.npm_test_dir)
    else:
        raise NotImplementedError(f"Print command for value '{name}' is not implemented")
