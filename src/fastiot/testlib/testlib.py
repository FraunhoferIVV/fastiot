""" Helpers to make writing tests easier """
import os

from fastiot.cli.infrastructure_service_fn import set_infrastructure_service_port_environment
from fastiot.env.env_constants import FASTIOT_NATS_HOST
from fastiot.testlib.cli import init_default_context


def populate_test_env():
    """ TODO: This is mostly still a stub """

    os.environ[FASTIOT_NATS_HOST] = 'localhost'
    init_default_context()
    set_infrastructure_service_port_environment()
