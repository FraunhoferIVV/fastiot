import importlib
import logging
from typing import List, Dict

from fastiot.cli.configuration.command import Command
from fastiot.cli.configuration.context import Context


def main():
    context = _import_configuration()
    commands = _import_extensions(context=context)
    # execute command


def _import_configuration() -> Context:
    config = {}
    try:
        m = importlib.import_module('configure')
        for key in dir(m):
            if key.startswith('_'):
                # skip hidden vars
                continue
            config[key] = getattr(m, key)
    except ImportError:
        logging.warning('Trying to import configure.py failed')
    return Context(config=config)


def _import_extensions(context: Context) -> Dict[str, Command]:
    plugins = []
    for ext in context.extensions:
        try:
            importlib.import_module(ext)
            #plugins.append(a.provide_plugin())
        except ImportError:
            pass

    commands = {}
    for plugin in plugins:
        commands.update(plugin.commands)
    return commands


if __name__ == '__main__':
    # entry point for fastiot command
    logging.basicConfig(level=logging.INFO)
    main()
