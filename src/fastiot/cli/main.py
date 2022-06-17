import importlib
import logging
import os

from fastiot.cli.import_configure import import_configure
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import app


def _import_commands():
    for f in os.listdir(os.path.join(os.path.dirname(__file__), 'common', 'commands')):
        if f.startswith('_'):
            continue
        f, _ = os.path.splitext(f)
        mod = f'fastiot.cli.common.commands.{f}'
        try:
            importlib.import_module(mod)
        except Exception:
            logging.exception(f"Import error raised during import of module {mod}")


if __name__ == '__main__':
    # entry point for fastiot command
    logging.basicConfig(level=logging.INFO)
    default_context = get_default_context()
    default_context.project_config = import_configure()
    _import_commands()
    app()
