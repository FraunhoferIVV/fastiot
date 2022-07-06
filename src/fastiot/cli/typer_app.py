"""
Base of typer app
=================

Here the typer app is initialized. If you want to add own commands you may consult the Typer documentation.
Basically your commands will be decorated with an `@app.command()`. Replace `app` with `create_cmd`, `run_cmd`, or
`stop_cmd` if you want to create subcommands of create, run or stop.
"""
import importlib
import logging
import os

import typer


DEFAULT_CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

# Main typer app to add new commands to.
app = typer.Typer(
    context_settings=DEFAULT_CONTEXT_SETTINGS
)

# Use this command to create any subcommand of create, like `fastiot.cli create my-special-file`
create_cmd = typer.Typer(context_settings=DEFAULT_CONTEXT_SETTINGS)
app.add_typer(create_cmd, name='create', help='')

# Use this command to create any subcommand of `run`, like `fastiot.cli run my_special_test`
run_cmd = typer.Typer(context_settings=DEFAULT_CONTEXT_SETTINGS)
app.add_typer(run_cmd, name='run', help='Run different parts (services, …) of the project.')

# Use this command to create any subcommand of `stop`, like `fastiot.cli stop environment`
stop_cmd = typer.Typer(context_settings=DEFAULT_CONTEXT_SETTINGS)
app.add_typer(stop_cmd, name='stop', help='Stop different parts (services, …) of the project.')


def _import_commands():
    for f in os.listdir(os.path.join(os.path.dirname(__file__), 'commands')):
        if f.startswith('_'):
            continue
        f, _ = os.path.splitext(f)
        mod = f'fastiot.cli.commands.{f}'
        try:
            importlib.import_module(mod)
        except Exception:
            logging.exception(f"Import error raised during import of module {mod}")


def _import_infrastructure_services():
    importlib.import_module('fastiot.cli.common.infrastructure_services')


_import_commands()
_import_infrastructure_services()
