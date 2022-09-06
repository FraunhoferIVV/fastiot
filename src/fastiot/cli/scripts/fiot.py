#!/usr/bin/env python3
""" Basic script to start the fiot command line program """
import logging
import os

from fastiot.cli import typer_app
from fastiot.cli.commands import *  # noqa  # pylint: disable=wildcard-import,unused-wildcard-import
from fastiot.cli.infrastructure_service_fn import get_services_list
from fastiot.cli.import_configure import import_configure
from fastiot.cli.model.context import get_default_context

if __name__ == '__main__':
    # entry point for fastiot command
    LOGLEVEL = os.environ.get('FASTIOT_LOGLEVEL', 'INFO').upper()

    logging.basicConfig(level=LOGLEVEL)
    default_context = get_default_context()
    default_context.project_config = import_configure(os.environ.get('FASTIOT_CONFIGURE_FILE'))

    default_context.external_services = get_services_list()

    typer_app.app()
