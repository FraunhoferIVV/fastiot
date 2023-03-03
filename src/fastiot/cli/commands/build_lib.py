""" Commands to compile the project library """
import logging
import os
import subprocess
import sys
from enum import Enum
from glob import glob
from shutil import rmtree
from typing import Optional, List, Dict

import tomli
import tomli_w
import typer

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
                                                               "(just for setup.py) compiled, wheel or sdist"),
              noupdate: Optional[bool] = typer.Option(False, '-n', '--noupdate',
                                                    help="Use to not overwrite pyproject.toml ")):
    """ Compile the project library according to the project configuration. """

    context = ProjectContext.default
    if not context.library_package:
        logging.info("No library package configured in configure.py. Exiting.")
        return

    logging.info("Starting to build library.")

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

    pyproject_toml = os.path.join(context.project_root_dir, 'pyproject.toml')
    if not os.path.isfile(pyproject_toml):
        logging.warning("Can not build library without a `pyproject.toml in project root dir.\n"
                        "You may use the command `fiot create pyproject-toml` to create a basic `pyproject.toml` to "
                        "build a library.\n\n"
                        "Now trying to use obsolete setup.py instead.")
        _build_lib_with_setup_py(styles, env)
        return

    if not noupdate:
        update_pyproject_toml()

    command_args = {
        BuildLibStyles.wheel: '-w',
        BuildLibStyles.sdist: '-s',
    }
    for style in styles:
        if style == BuildLibStyles.compiled:
            if noupdate:
                logging.warning("Cannot compile library if flag `--update no` is set. Skipping.")
                continue
            _build_lib_with_nuitka(env=env)
            continue

        cmd = f"{sys.executable} -m build -w {command_args[style]}"
        exit_code = subprocess.call(cmd.split(), env=env, cwd=context.project_root_dir)

        if exit_code != 0:
            logging.error("Building library failed with exit code %s", str(exit_code))
            raise typer.Exit(exit_code)

    # Cleanup some possible left overs from building library
    for directory in [("build", "lib"),
                      ("build", "bdist.linux-x86_64"),
                      ("src", f"{context.project_namespace}.egg-info")]:
        try:
            rmtree(os.path.join(context.project_root_dir, *directory))
        except FileNotFoundError:
            pass

    logging.info("Successfully built library")


def update_pyproject_toml(build_system: Optional[Dict] = None):
    context = ProjectContext.default
    pyproject_toml = os.path.join(context.project_root_dir, 'pyproject.toml')
    packages = [os.path.basename(p) for p in glob(os.path.join(context.project_root_dir, "src", "*"))]
    exclude_from_package = [p + "*" for p in packages if p != context.library_package]
    install_requires, extras_require = read_requirements()

    with open(pyproject_toml, "rb") as toml_file:
        toml_dict = tomli.load(toml_file)

    toml_dict["project"]["dependencies"] = install_requires
    toml_dict["project"]["optional-dependencies"] = extras_require
    if get_version(complete=True) != "git-unspecified":
        toml_dict["project"]["version"] = get_version(complete=True)

    toml_dict["build-system"] = build_system or {"requires": ["setuptools>=67", "setuptools_scm[toml]>=6.2", "wheel"]}

    toml_dict["tool"] = {"setuptools": {"packages": {}}}
    toml_dict["tool"]["setuptools"]["packages"]["find"] = {"where": ["src"],
                                                           "exclude": exclude_from_package}

    toml_dict["nuitka"] = {"show-scons": False,
                           "nofollow-import-to": exclude_from_package}

    with open(pyproject_toml, "wb") as toml_file:
        toml_file.write("# ATTENTION: Parts of this file are managed automatically!\n"
                        "# This refers to build-system, project.dependencies, project.optional-dependencies, "
                        "project.version, tool and nuitka.\n\n".encode())
        tomli_w.dump(toml_dict, toml_file)


def _build_lib_with_nuitka(env):
    context = ProjectContext.default

    build_system = {"requires": ["setuptools>=67", "setuptools_scm[toml]>=6.2", "wheel", "nuitka", "toml"],
                    "build-backend": "nuitka.distutils.Build"}

    update_pyproject_toml(build_system=build_system)

    cmd = f"{sys.executable} -m build"
    exit_code = subprocess.call(cmd.split(), env=env, cwd=context.project_root_dir)

    if exit_code != 0:
        logging.error("Building library failed with exit code %s", str(exit_code))
        update_pyproject_toml()  # Change back to regular file without link to nuitka build system
        raise typer.Exit(exit_code)

    update_pyproject_toml()  # Change back to regular file without link to nuitka build system


def read_requirements():
    requirement_files = glob("requirements*.txt",
                             root_dir=os.path.join(ProjectContext.default.project_root_dir, 'requirements'))
    requirement_files_abs = [os.path.join(ProjectContext.default.project_root_dir, 'requirements', f) for f in
                             requirement_files]
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
    return install_requires, extras_require

def _build_lib_with_setup_py(styles, env):
    context = ProjectContext.default

    command_args = {
        BuildLibStyles.wheel: 'bdist_wheel -q',
        BuildLibStyles.sdist: 'sdist -q',
        BuildLibStyles.compiled: 'bdist_nuitka'
    }

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

    logging.info("Successfully built library using obsolete setup.py")
