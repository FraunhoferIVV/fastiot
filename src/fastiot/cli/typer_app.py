import typer

DEFAULT_CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

app = typer.Typer(
    context_settings=DEFAULT_CONTEXT_SETTINGS
)

create_cmd = typer.Typer(context_settings=DEFAULT_CONTEXT_SETTINGS)
# Use this command to create any subcommand of create, like `fastiot.cli create my-special-file`

app.add_typer(create_cmd, name='create')

run_cmd = typer.Typer(context_settings=DEFAULT_CONTEXT_SETTINGS)
# Use this command to create any subcommand of `run`, like `fastiot.cli run my_special_test`
app.add_typer(run_cmd, name='run')

stop_cmd = typer.Typer(context_settings=DEFAULT_CONTEXT_SETTINGS)
# Use this command to create any subcommand of `stop`, like `fastiot.cli stop environment`
app.add_typer(stop_cmd, name='stop')
