""" Some helpers to work with external services: importing, port handling, … """
from socket import socket
from typing import Dict

from fastiot.cli.model import InfrastructureService


def get_infrastructure_service_ports_randomly() -> Dict[str, int]:
    """
    Get random environment variables for all ports.

    On very busy machines this may to reuse of ports, if another service takes the port betweening determining its free
    status and acutally starting the service.

    :return: dict with the environment variables and the corresponding port numbers
    """
    ports = {}
    for service in InfrastructureService.all.values():
        for port in service.ports:
            with socket() as temp_socket:
                temp_socket.bind(('', 0))
                ports[port.env_var] = temp_socket.getsockname()[1]
    return ports


def get_infrastructure_service_ports_monotonically_increasing(offset: int) -> Dict[str, int]:
    """
    Get environment variables for all ports in a monotonically increasing order with an offset.

    :param offset: Port number for the first service, will be monotonically increasing for all further services.
    :return: dict with the environment variables and the corresponding port numbers
    """
    if offset < 0:
        raise ValueError(f"Expected offset greater or equal than zero. Is {offset} instead.")

    ports = {}
    for service in InfrastructureService.all.values():
        for port in service.ports:
            ports[port.env_var] = offset
            offset += 1
    return ports

