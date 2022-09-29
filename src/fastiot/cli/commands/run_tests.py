import logging
import os
import subprocess
import sys
from enum import Enum
from importlib.machinery import PathFinder
from typing import Optional

import typer

from fastiot.cli.commands.start import start
from fastiot.cli.commands.stop import stop
from fastiot.cli.model.project import ProjectContext
from fastiot.cli.typer_app import DEFAULT_CONTEXT_SETTINGS, app


class TestRunner(str, Enum):
    """ Specify the test runner """
    unittest = 'unittest'
    """ Use python's builtin unittest """
    pytest = 'pytest'
    """ Use pytest. This lib must be installed """
    pytest_cov = 'pytest-cov'
    """ Use pytest with test coverage option. Please note, that pytest-cov must be installed """


@app.command(context_settings=DEFAULT_CONTEXT_SETTINGS)
def run_tests(start_deployment: bool = typer.Option(False, help="Also start and stop the test-deployment. "
                                                                "Defaults to false"),
              test_runner: Optional[TestRunner] = typer.Option(None,
                                                               help="Specify the testrunner to use. Will try to use "
                                                                    "pytest if found, otherwise falls back to "
                                                                    "unittest.")
              ):
    """
    This command will trigger all unittests found in the configured test package. You may use the option
    `--start-deployment` to also run your integration test deployment with message broker, ….
    """
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'  # Stop writing an __pycache__ for clean containers afterwards

    context = ProjectContext.default

    if not context.test_package:
        logging.info("No test_package defined in configure.py. Skipping unittests.")
        sys.exit(0)

    if not context.integration_test_deployment:
        logging.info("No test deployment configured, so no need to run configure for the deployment. "
                     "Skipping the step")
        return

    if not os.path.isfile(os.path.join(context.project_root_dir, 'src', context.test_package,
                                       'generated.py')):
        from fastiot.cli.commands.config import config  # pylint: disable=import-outside-toplevel

        logging.warning("No file `generated.py` found in testpackage %s.\n"
                        "\tRunning config command to create one now.", context.test_package)
        config(use_test_deployment=True, port_offset=0)

    if start_deployment:
        start(use_test_deployment=True, detach=True, project_name=None, service_names=None)

    env = os.environ.copy()
    src_dir = os.path.join(context.project_root_dir, 'src')
    env['PYTHONPATH'] = src_dir
    cmd = _get_command_for_test_runner(test_runner=test_runner, src_dir=src_dir)

    exit_code = subprocess.call(cmd.split(),
                                cwd=context.project_root_dir,
                                env=env)

    if start_deployment:
        stop(use_test_deployment=True, project_name=None, service_names=None)

    if exit_code != 0:
        logging.error("Running unittests failed with exit code %s", str(exit_code))
        sys.exit(exit_code)


def _get_command_for_test_runner(test_runner: TestRunner, src_dir: str) -> str:
    test_dir = os.path.join(src_dir, ProjectContext.default.test_package)

    if not test_runner:
        test_runner = TestRunner.pytest if PathFinder.find_spec(TestRunner.pytest) else TestRunner.unittest
    logging.debug("Using %s as test_runner", test_runner)

    if test_runner is TestRunner.unittest:
        return "python3 -m unittest discover " + test_dir
    if test_runner is TestRunner.pytest:
        return f"python3 -m pytest --rootdir={test_dir}/ -p no:cacheprovider"
    if test_runner is TestRunner.pytest_cov:
        return f"python3 -m pytest --rootdir={test_dir} --junitxml=pytest_report.xml " \
               f"--cov={src_dir} --cov-report=xml --cov-branch -p no:cacheprovider"

    raise NotImplementedError()
