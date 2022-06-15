import typer

DEFAULT_CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

app = typer.Typer(
    context_settings=DEFAULT_CONTEXT_SETTINGS
)
