"""
Help info

"""

from typing import List

from fastiot.cli.configuration.command import Command
from fastiot.cli.configuration.context import CliContext
from fastiot.cli.configuration.plugin import Plugin


class MyPrintCommand(Command):
    def execute(self, context: CliContext, vargs: List[str]):
        pass

    def print_help(self, context: CliContext):
        print(__file__.__doc__)


def provide_plugin() -> Plugin:
    return Plugin(
        commands={
            'print': MyPrintCommand()
        }
    )
