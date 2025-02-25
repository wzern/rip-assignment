import socket
import select
import time

from modules.configurator import INPUTS
from modules.router_table import RouterTable

active_sockets = []
routing_table = RouterTable()
periodic_update_interval = 3
timeout_interval = 18
garbage_collection_interval = 24
last_update_time = time.monotonic()

def router_init():
    for router_input in INPUTS:
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_addr = ('127.0.0.1', router_input)
        new_socket.bind(socket_addr)
        active_sockets.append(new_socket)
        print(f"[INIT] Bound to port {router_input}")

def send():
    global last_update_time
    current_time = time.monotonic()
    if current_time - last_update_time >= periodic_update_interval:
        print("im here")
        for sock in active_sockets:
            for destination, entry in routing_table.routes.items():
                message = f"{destination},{entry.next_hop},{entry.metric}"
                sock.sendto(message.encode(), ('127.0.0.1', destination))
                print(f"[SEND] Sent update to {destination}: {message}")
        last_update_time = current_time

def fetch():
    sockets, _, _ = select.select(active_sockets, [], [], 0.5)  
    for sock in sockets:
        update_routing_table(sock)

def update_routing_table(sock):
    data, addr = sock.recvfrom(1024)
    routing_update = data.decode().split(',')
    if len(routing_update) == 3:
        destination, next_hop, metric = map(int, routing_update)
        routing_table.add_or_update_route(destination, next_hop, metric)
        print(f"[RECEIVE] Update from {addr}: {routing_update}")
    routing_table.print_routing_table()