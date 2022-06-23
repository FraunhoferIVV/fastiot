""" Some helpers to work with external services: importing, port handling, … """
import importlib
import logging
import os
from socket import socket
from typing import Optional, Dict, List, Union

from fastiot.cli.configuration import external_services  # noqa  # pylint: disable=unused-import
from fastiot.cli.model import ExternalService

_services_imported = False


def get_services_list() -> Dict[str, ExternalService]:
    """ Method to get a list of all available services as instantiated
    :class:`fastiot.cli.model.service.ExternalService`.

    To append own services you simply have to inherit from :class:`fastiot.cli.model.service.ExternalService` and put
    them into your project. Then import those parts using :attr:`fastiot.cli.model.project.ProjectConfig.extensions`.
    This method will try to import anything from there and for services.
    """
    global _services_imported

    if not _services_imported:
        from fastiot.cli.model.context import get_default_context  # pylint: disable=import-outside-toplevel

        project_config = get_default_context().project_config

        for extension in project_config.extensions:
            try:
                importlib.import_module(f'{extension}')
            except ImportError:  # Extension does not provide any services
                logging.debug("Could not import external service from extension %s", extension)
        _services_imported = True

    service_classes = ExternalService.__subclasses__()
    services = [s() for s in service_classes]
    return {s.name: s for s in services}


def set_external_service_port_environment(offset: int = 1024, random: bool = False,
                                          services: Optional[List[Union[str, ExternalService]]] = None) -> \
        Dict[str, int]:
    """
    Sets up the local environment with environment variables for all ports.

    :param offset: Port number for the first service, will be monotonically increasing for all further services.
    :param random: Set to random to find a free service for each port. On very busy machines this may to reuse of ports,
                   if another service takes the port betweening determining its free status and acutally starting the
                   service.
    :param services:  List of services as service name or instance of :class:`fastiot.cli.model.service.ExternalService`
    :return: dict with the environment variables set and the corresponding port numbers
    """

    open_ports = {}

    for service_nr, service in enumerate(get_services_list().values()):

        if services is not None and service.name not in services and service in services:
            continue

        if not random:
            os.environ[service.port_env_var] = str(offset + service_nr)
        else:
            with socket() as temp_socket:
                temp_socket.bind(('', 0))
                os.environ[service.port_env_var] = temp_socket.getsockname()[1]

        open_ports[service.port_env_var] = int(os.environ.get(service.port_env_var))

    return open_ports
