
import argparse

import typer

from fastiot.cli.version import get_version
from fastiot.cli.typer_app import DEFAULT_CONTEXT_SETTINGS, extras_cmd

@extras_cmd.command(context_settings=DEFAULT_CONTEXT_SETTINGS)
def version(complete: bool = typer.Option(default=False, help="Show complete version string starting (Used if nothing else is specified)"),
            only_major: bool = typer.Option(default=False, help="Show only the major version as number"),
            minor: bool = typer.Option(default=False, help="Show major.minor version")):
    """
    Shows current version depending on git commits and tags
    """
    print(get_version(
        complete=complete,
        only_major=only_major,
        minor=minor
    ))

