""" Commands to compile the project library """
import logging
import os
import subprocess
import sys
from enum import Enum
from glob import glob
from shutil import rmtree
from typing import Optional, List

import typer

from fastiot.cli.model import CompileSettingsEnum
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import app

libraries = []


class BuildLibStyles(str, Enum):
    all = 'all'
    compiled = 'compiled'
    wheel = 'wheel'
    sdist = 'sdist'


def _styles_completion() -> List[str]:
    return [s.value for s in BuildLibStyles]


@app.command()
def build_lib(build_style: Optional[str] = typer.Argument('all', shell_complete=_styles_completion,
                                                          help="Compile all styles configured for the project or force compiled, "
                                                               "wheel or sdist")):
    """ Compile the project library according to the project configuration. """

    project_config = get_default_context().project_config
    if project_config.library_package is None:
        logging.info("No library package configured in configure.py. Exiting.")
        return

    styles = []
    if build_style == BuildLibStyles.all:
        if project_config.lib_compilation_mode == CompileSettingsEnum.only_compiled:
            styles.append(BuildLibStyles.compiled)
        elif project_config.lib_compilation_mode == CompileSettingsEnum.only_source:
            styles += [BuildLibStyles.wheel, BuildLibStyles.sdist]
        else:
            styles += [BuildLibStyles.wheel, BuildLibStyles.sdist, BuildLibStyles.compiled]
    else:
        styles = [build_style]

    env = os.environ.copy()
    env['MAKEFLAGS'] = f"-j{len(os.sched_getaffinity(0))}"
    command_args = {BuildLibStyles.wheel: 'bdist_wheel -q',
                    BuildLibStyles.sdist: 'sdist -q',
                    BuildLibStyles.compiled: 'bdist_nuitka'}

    setup_py = os.path.join(project_config.library_setup_py_dir, 'setup.py')
    for style in styles:
        cmd = f"{sys.executable} {setup_py} {command_args.get(style)}"
        exit_code = subprocess.call(cmd.split(), env=env, cwd=project_config.project_root_dir)

        try:
            for file in glob(os.path.join(project_config.project_root_dir, 'src', '*.egg-info')):
                rmtree(file)
        except FileNotFoundError:
            pass

        if exit_code != 0:
            logging.error("Building library with style %s failed with exit code %s", str(style.value), str(exit_code))
            raise typer.Exit(exit_code)

