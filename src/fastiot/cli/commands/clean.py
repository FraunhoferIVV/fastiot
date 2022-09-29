import os
from shutil import rmtree

import typer

from fastiot.cli.model import ProjectContext
from fastiot.cli.typer_app import DEFAULT_CONTEXT_SETTINGS, app, extras_cmd


@app.command(context_settings=DEFAULT_CONTEXT_SETTINGS)
def clean(do_clean_all: bool = typer.Option(False, '-a', '--all', help="If specified, it will also cleanup local "
                                                                       "docker instance.")
          ):
    """
    This command cleans up all generated files and removes all container and images from docker daemon.
    """
    _clean_generated_files(context=ProjectContext.default)
    if do_clean_all:
        os.system("docker ps -q | xargs -r docker kill")
        os.system("docker ps -aq | xargs -r docker rm")
        os.system("docker images -q | xargs -r docker rmi -f")


def _clean_generated_files(context: ProjectContext):
    build_dir = os.path.join(context.project_root_dir, context.build_dir)
    if os.path.exists(build_dir):
        rmtree(build_dir)


@extras_cmd.command(context_settings=DEFAULT_CONTEXT_SETTINGS)
def remove_all_container(kill: bool = typer.Option(False, '-k', '--kill',
                                                   help="Sending kill signal to containers, instead of stop signal.")):
    """
    Remove all running container
    """
    if kill:
        os.system("docker ps -q | xargs -r docker kill")
    else:
        os.system("docker ps -q | xargs -r docker stop")
    os.system("docker ps -aq | xargs -r docker rm")
