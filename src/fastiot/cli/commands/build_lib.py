""" Commands to compile the project library """
import logging
import os
import subprocess
import sys
from enum import Enum
from glob import glob
from shutil import rmtree
from typing import Optional, List

import tomli
import tomli_w
import typer
from setuptools import find_packages

from fastiot import get_version
from fastiot.cli.model import CompileSettingsEnum
from fastiot.cli.model.project import ProjectContext
from fastiot.cli.typer_app import DEFAULT_CONTEXT_SETTINGS, extras_cmd

libraries = []


class BuildLibStyles(str, Enum):
    all = 'all'
    compiled = 'compiled'
    wheel = 'wheel'
    sdist = 'sdist'


def _styles_completion() -> List[str]:
    return [s.value for s in BuildLibStyles]


@extras_cmd.command(context_settings=DEFAULT_CONTEXT_SETTINGS)
def build_lib(build_style: Optional[str] = typer.Argument('all', shell_complete=_styles_completion,
                                                          help="Compile all styles configured for the project or force "
                                                               "compiled, wheel or sdist")):
    """ Compile the project library according to the project configuration. """

    context = ProjectContext.default
    if not context.library_package:
        logging.info("No library package configured in configure.py. Exiting.")
        return

    if not isinstance(build_style, str):
        build_style = build_style.default

    if build_style == BuildLibStyles.all:
        if context.lib_compilation_mode == CompileSettingsEnum.only_compiled:
            styles = [BuildLibStyles.compiled]
        elif context.lib_compilation_mode == CompileSettingsEnum.only_source:
            styles = [BuildLibStyles.wheel, BuildLibStyles.sdist]
        elif context.lib_compilation_mode == CompileSettingsEnum.all_variants:
            styles = [BuildLibStyles.wheel, BuildLibStyles.sdist, BuildLibStyles.compiled]
        else:
            raise NotImplementedError()
    else:
        styles = [build_style]

    env = os.environ.copy()
    env['MAKEFLAGS'] = f"-j{len(os.sched_getaffinity(0))}"
    command_args = {
        BuildLibStyles.wheel: 'bdist_wheel -q',
        BuildLibStyles.sdist: 'sdist -q',
        BuildLibStyles.compiled: 'bdist_nuitka'
    }

    pyproject_toml = os.path.join(context.library_setup_py_dir, 'pyproject.toml')
    if not os.path.isfile(pyproject_toml):
        logging.warning("Can not build library without a `pyproject.toml in project root dir.")
    else:
#--------
        requirement_files = glob("requirements*.txt", root_dir=os.path.join(ProjectContext.default.project_root_dir, 'requirements'))
        requirement_files_abs = [os.path.join(ProjectContext.default.project_root_dir, 'requirements', f) for f in requirement_files]
        install_requires = []
        extras_require = {'all': []}

        for req_name, req_name_abs in zip(requirement_files, requirement_files_abs):
            req_list = []
            with open(req_name_abs) as f:
                for req in f.read().splitlines():
                    req = req.strip()
                    if req != '' and not req.startswith('#'):
                        req_list.append(req)
            if req_name == 'requirements.txt':
                install_requires.extend(req_list)
            else:
                middle_name = req_name.removeprefix('requirements.').removesuffix('.txt')
                extras_require[middle_name] = req_list
            extras_require['all'].extend(req_list)

        if not install_requires:
            raise RuntimeError("Could not find a requirements.txt")


        toml = open("pyproject.toml", "rb")
        toml_dict = tomli.load(toml)
        toml.close()
        print(toml_dict)
        toml_dict["project"]["dependencies"] = install_requires
        toml_dict["project"]["version"] = get_version(complete=True)
        toml = open("pyproject.toml", "wb")
        tomli_w.dump(toml_dict, toml)
        toml.close()


        # TODO test if this is working for all Projects
        cmd = f"{sys.executable} -m build"
        exit_code = subprocess.call(cmd.split())

        if exit_code != 0:
            logging.error("Building library  failed with exit code %s", str(exit_code))
            raise typer.Exit(exit_code)
        return

    setup_py = os.path.join(context.library_setup_py_dir, 'setup.py')
    if not os.path.isfile(setup_py):
        logging.warning("Can not build library without a `setup.py` in project root dir. Exiting.")
        return

    for style in styles:
        cmd = f"{sys.executable} {setup_py} {command_args.get(style)}"
        exit_code = subprocess.call(cmd.split(), env=env, cwd=context.project_root_dir)

        try:
            for file in glob(os.path.join(context.project_root_dir, 'src', '*.egg-info')):
                rmtree(file)
        except FileNotFoundError:
            pass

        if exit_code != 0:
            logging.error("Building library with style %s failed with exit code %s", str(style.value), str(exit_code))
            raise typer.Exit(exit_code)
