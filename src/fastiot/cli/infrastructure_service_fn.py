""" Some helpers to work with external services: importing, port handling, … """
import os
from socket import socket
from typing import Optional, Dict, List, Union

from fastiot.cli.model import InfrastructureService


def get_services_list() -> Dict[str, InfrastructureService]:
    """ Method to get a list of all available services as instantiated
    :class:`fastiot.cli.model.service.ExternalService`.

    To append own services you simply have to inherit from :class:`fastiot.cli.model.service.ExternalService` and put
    them into your project. Then import those parts using :attr:`fastiot.cli.model.project.ProjectConfig.extensions`.
    This method will try to import anything from there and for services.
    """
    service_classes = InfrastructureService.__subclasses__()
    services = [s() for s in service_classes]
    return {s.name: s for s in services}


def set_infrastructure_service_port_environment(offset: int = 0, random: bool = False,
                                                services: Optional[List[Union[str, InfrastructureService]]] = None) -> \
        Dict[str, int]:
    """
    Sets up the local environment with environment variables for all ports.

    :param offset: Port number for the first service, will be monotonically increasing for all further services. Set to
                   ``0`` to not use any alternative ports.
    :param random: Set to random to find a free service for each port. On very busy machines this may to reuse of ports,
                   if another service takes the port betweening determining its free status and acutally starting the
                   service.
    :param services:  List of services as service name or instance of :class:`fastiot.cli.model.service.ExternalService`
    :return: dict with the environment variables set and the corresponding port numbers
    """

    open_ports = {}
    port_counter = 0
    for service in get_services_list().values():

        if services is not None and service.name not in services and service in services:
            continue

        for port in service.ports:
            if offset > 0:
                os.environ[port.env_var] = str(offset + port_counter)
                port_counter += 1
            elif random:
                with socket() as temp_socket:
                    temp_socket.bind(('', 0))
                    os.environ[port.env_var] = str(temp_socket.getsockname()[1])
            else:
                os.environ[port.env_var] = str(port.default_port_mount)

            open_ports[port.env_var] = int(os.environ.get(port.env_var))

    return open_ports
