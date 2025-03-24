import socket
import time
import select
from modules.configurator import get_router_id, get_router_inputs, get_router_outputs

INFINITY = 16  # RIP uses 16 to indicate an unreachable route.

class RIPRouter:
    def __init__(self, router_id, input_ports, outputs, timeout=10):
        self.router_id = router_id
        self.input_ports = input_ports
        self.outputs = outputs  # {router_id: (port, metric)}
        self.routing_table = {}  # {router_id: (port, metric)}
        self.last_received = {}  # {router_id: last_received_timestamp}
        self.timeout = timeout  # Timeout in seconds for detecting dead routers
        self.sockets = []  # List to hold all input sockets

        # Create server sockets for each input port
        for port in self.input_ports:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.bind(('localhost', port))
            server_socket.setblocking(False)  # Set socket to non-blocking mode
            self.sockets.append(server_socket)

    def listen_for_messages(self):
        """Listen for incoming RIP messages on input ports."""
        # Use select to wait for any input sockets to be ready for reading
        readable, _, _ = select.select(self.sockets, [], [], 1)
        for sock in readable:
            data, _ = sock.recvfrom(1024)
            self.handle_incoming_message(data)

    def handle_incoming_message(self, data):
        """Handle the incoming RIP message."""
        # Assuming the message contains the router ID, port, and metric
        message = data.decode('utf-8').split(',')
        print(message)
        peer_router_id, port, metric = int(message[0]), int(message[1]), int(message[2])

        # Update routing table based on received message
        if peer_router_id not in self.routing_table or self.routing_table[peer_router_id][1] > metric:
            self.routing_table[peer_router_id] = (port, metric)
            print(f"Updated routing table: {self.routing_table}")

        # Update the last received timestamp for the peer router
        self.last_received[peer_router_id] = time.time()

    def send_rip_message(self, peer_router_id, metric):
        """Send a RIP message to a peer router."""
        peer_port, _ = self.outputs[peer_router_id]
        message = f"{self.router_id},{peer_port},{metric}"
        message = message.encode('utf-8')

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(message, ('localhost', peer_port))
        print(f"Sent RIP message: {message.decode('utf-8')}")

    def send_periodic_updates(self):
        """Send periodic RIP updates to neighbors."""
        for peer_router_id, (peer_port, metric) in self.outputs.items():
            # Implement Split Horizon: Don't send routes back to the router that provided them
            if peer_router_id in self.routing_table:
                # Poisoned Reverse: If a route is learned through a peer, send it with an "infinity" metric
                for router_id, (port, route_metric) in self.routing_table.items():
                    if port == peer_port:  # This route was learned from this peer
                        self.send_rip_message(peer_router_id, INFINITY)
                    else:
                        self.send_rip_message(peer_router_id, route_metric)

            else:
                self.send_rip_message(peer_router_id, metric)

    def check_for_dead_routers(self):
        """Check if any routers have timed out."""
        current_time = time.time()
        dead_routers = []

        for router_id, last_time in list(self.last_received.items()):
            if current_time - last_time > self.timeout:
                # If the router hasn't sent a message within the timeout period, mark it as dead
                print(f"Router {router_id} is considered dead due to timeout.")
                dead_routers.append(router_id)
                self.remove_dead_router(router_id)

        return dead_routers

    def remove_dead_router(self, router_id):
        """Remove the router from the routing table and last_received dictionary."""
        if router_id in self.routing_table:
            del self.routing_table[router_id]
            print(f"Removed dead router {router_id} from routing table.")

        if router_id in self.last_received:
            del self.last_received[router_id]
            print(f"Removed router {router_id} from last received timestamps.")

def main():
    router = RIPRouter(get_router_id(), get_router_inputs(), get_router_outputs())

    last_update_time = time.time()

    print(router.router_id)

    while True:
        # Listen for incoming messages
        router.listen_for_messages()

        # Check if it's time to send periodic updates
        current_time = time.time()
        if current_time - last_update_time >= 5:
            router.send_periodic_updates()
            last_update_time = current_time

        # Check for any dead routers and remove them from the routing table
        router.check_for_dead_routers()

if __name__ == "__main__":
    main()