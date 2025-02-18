import socket

from modules.configurator import INPUTS

def router_init():
    active_sockets = []

    for router_input in INPUTS:
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_addr = ('127.0.0.1', router_input)  # Localhost and port 5000
        new_socket.bind(socket_addr)
        active_sockets.append(new_socket)

    print(active_sockets)
