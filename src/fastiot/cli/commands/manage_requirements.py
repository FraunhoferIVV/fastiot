import logging
import os
import subprocess

import tomli
import typer

from fastiot.cli.model import ProjectContext
from fastiot.cli.typer_app import extras_cmd, DEFAULT_CONTEXT_SETTINGS


@extras_cmd.command(context_settings=DEFAULT_CONTEXT_SETTINGS)
def set_requirements(
        update_requirements: bool = typer.Option(False, '-u', '--update-requirements',
                                                 help="Update all requirements files to latest versions matching the "
                                                      "dependencies listed in your `pyproject.toml`.")):
    """
    Updates :file:`requirements.txt` and files in path :file:`requirements` according to the settings in your
    :file:`pyproject.toml`.
    """

    logging.info("Starting to create fixed requirements.txt files based on pyproject.toml…")
    context = ProjectContext.default

    pyproject_toml = os.path.join(context.project_root_dir, 'pyproject.toml')
    if not os.path.isfile(pyproject_toml):
        logging.warning("Can not automatically create fixed requirements without `pyproject.toml`")
        logging.warning("Use `fiot create pyproject-toml` to create one!")
        return

    # Base
    _run_pip_compile(file_name=os.path.join(context.project_root_dir, 'requirements.txt'),
                     upgrade=update_requirements, name='base')

    with open(pyproject_toml, "rb") as toml_file:
        toml_dict = tomli.load(toml_file)

    if 'optional-dependencies' in toml_dict['project']:
        os.makedirs(os.path.join(context.project_root_dir, 'requirements'), exist_ok=True)
        for extra_dep in toml_dict['project']['optional-dependencies'].keys():
            target_file = os.path.join(context.project_root_dir, 'requirements', f"requirements.{extra_dep}.txt")
            _run_pip_compile(file_name=target_file, cmd_extras=f"--extra={extra_dep}",
                             upgrade=update_requirements, name=extra_dep)

        target_file = os.path.join(context.project_root_dir, 'requirements', "requirements.all.txt")
        _run_pip_compile(file_name=target_file, cmd_extras="--all-extras", upgrade=update_requirements, name="all")

    logging.info("Don’t forget to add the changed requirements to git!")


def _run_pip_compile(file_name: str, cmd_extras: str = "", upgrade: bool = False, name: str = ""):
    logging.info("    Building %s requirements", name)

    cmd = f"pip-compile --annotation-style=line --resolver=backtracking --output-file={file_name} "
    if upgrade:
        cmd += "--upgrade "
    if cmd_extras:
        cmd += cmd_extras

    # Popen seems to be more stable than subprocess.call
    process = subprocess.Popen(cmd.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    _, stderr = process.communicate()
    if process.returncode != 0:
        logging.warning("Building requirements for %s failed with return code %d. Command used was `%s`",
                        name, process.returncode, cmd)
        logging.warning("The message was `%s`", stderr.decode().strip())
        logging.info("Leaving file untouched.")
        return

    # Do some cleanup on the generated requirements file to avoid information leakage
    with open(file_name, 'r') as file:
        text = file.readlines()

    with open(file_name, "w") as file:
        for line in text:
            if "pip-compile --" in line or "pip-compile -" in line:
                file.write("#    fiot config" + " --update-requirements\n" if upgrade else "\n")
            elif "extra-index-url" in line or "trusted-host" in line:
                continue
            else:
                file.write(line)
