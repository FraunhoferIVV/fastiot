from socket import socket


def get_local_random_port() -> int:
    with socket() as temp_socket:
        temp_socket.bind(('', 0))
        return temp_socket.getsockname()[1]
