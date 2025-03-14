import socket
import select
import time

from modules.configurator import INPUTS, OUTPUTS
from modules.router_table import RouterTable

active_sockets = []
routing_table = RouterTable()
periodic_update_interval = 30
timeout_interval = 180
garbage_collection_interval = 240
last_update_time = time.monotonic()

def router_init():
    for router_input in INPUTS:
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_addr = ('127.0.0.1', router_input)
        new_socket.bind(socket_addr)
        active_sockets.append(new_socket)
        print(f"[INIT] Bound to port {router_input}")

    for destination, direct_link in OUTPUTS.items():
        metric, next_hop = direct_link
        routing_table.add_or_update_route(destination, next_hop, metric)

    routing_table.print_routing_table()


def send():
    global last_update_time
    current_time = time.monotonic()
    if current_time - last_update_time >= periodic_update_interval:
        for destination, (metric, router_id) in OUTPUTS.items():  # Corrected
            message = f"{destination},{router_id},{metric}" #corrected
            for sock in active_sockets:
                sock.sendto(message.encode(), ('127.0.0.1', destination))  # Corrected: Send to port
                print(f"[SEND] Sent update to {destination}: {message}") #corrected
        last_update_time = current_time



def fetch():
    sockets, _, _ = select.select(active_sockets, [], [], 30)  
    for sock in sockets:
        update_routing_table(sock)
    

    routing_table.garbage_collect()
    routing_table.print_routing_table()

def update_routing_table(sock):
    data, addr = sock.recvfrom(1024)
    try:
        destination, next_hop, metric = map(int, data.decode().split(','))
        metric += 1 # Added metric increment.
        routing_table.add_or_update_route(destination, next_hop, metric)
        print(f"[RECEIVE] Update from {addr}: Destination={destination}, Next Hop={next_hop}, Metric={metric}")
    except ValueError:
        print(f"[ERROR] Malformed update received: {data.decode()} from {addr}")
