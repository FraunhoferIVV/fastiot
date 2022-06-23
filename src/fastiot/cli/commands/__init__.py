"""
commands
========

This package holds all cli commands defined in the fastiot cli tool """

from fastiot.cli.commands.build import build
from fastiot.cli.commands.build_lib import build_lib
from fastiot.cli.commands.clean import clean
from fastiot.cli.commands.config import config
from fastiot.cli.commands.generate import new_project, new_module
from fastiot.cli.commands.nuitka_compile import nuitka_compile
from fastiot.cli.commands.print import print_cmd  # noqa  # pylint: disable=unused-import
from fastiot.cli.commands.run import environment, tests
from fastiot.cli.commands.stop import environment as stop_environment
