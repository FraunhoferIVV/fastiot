""" Helpers to make writing tests easier """
import os

from fastiot.cli.external_service_helper import set_external_service_port_environment
from fastiot.env import FASTIOT_BROKER_HOST
from fastiot.testlib.cli import init_default_context


def populate_test_env():
    """ TODO: This is mostly still a stub """

    os.environ[FASTIOT_BROKER_HOST] = 'localhost'
    init_default_context()
    set_external_service_port_environment()
