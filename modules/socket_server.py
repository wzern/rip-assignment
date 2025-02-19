import socket
import select
import time

from modules.configurator import INPUTS
active_sockets = []
routing_table = {}
periodic_update_interval = 30
timeout_interval = 180 
garbage_collection_interval = 240
def router_init():
    
    for router_input in INPUTS:
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_addr = ('127.0.0.1', router_input)  # Localhost and port 5000
        new_socket.bind(socket_addr)
        active_sockets.append(new_socket)


    print(active_sockets)

def send():
    for sock in active_sockets:
        sock.sendto()
    time.sleep(periodic_update_interval) 

def fetch():
    sockets, _, _ = select.select(active_sockets, [], [], timeout_interval)   
    if sockets:
        for sock in sockets:
            update_routing_table(sock)
    else:        
        time.sleep(timeout_interval)


def update_routing_table(sock):
    data, addr = sock.recvfrom(1024) 
    routing_update = data.decode() 
    routing_table[addr] = routing_update
    print(routing_table)

        