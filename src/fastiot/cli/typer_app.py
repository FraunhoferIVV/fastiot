"""
Base of typer app
=================

Here the typer app is initialized. If you want to add own commands you may consult the Typer documentation.
Basically your commands will be decorated with an `@app.command()`. Replace `app` with `create_cmd`, `run_cmd`, or
`stop_cmd` if you want to create subcommands of create, run or stop.
"""
import typer

DEFAULT_CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

app = typer.Typer(
    context_settings=DEFAULT_CONTEXT_SETTINGS
)
# Main typer app to add new commands to.

create_cmd = typer.Typer(context_settings=DEFAULT_CONTEXT_SETTINGS)
# Use this command to create any subcommand of create, like `fastiot.cli create my-special-file`

app.add_typer(create_cmd, name='create')

run_cmd = typer.Typer(context_settings=DEFAULT_CONTEXT_SETTINGS)
# Use this command to create any subcommand of `run`, like `fastiot.cli run my_special_test`
app.add_typer(run_cmd, name='run')

stop_cmd = typer.Typer(context_settings=DEFAULT_CONTEXT_SETTINGS)
# Use this command to create any subcommand of `stop`, like `fastiot.cli stop environment`
app.add_typer(stop_cmd, name='stop')
