import socket
import time
import select

from modules.rip_routing_table import RoutingTable
from modules.configurator import get_router_id, get_router_inputs, get_router_outputs

class RIPRouter:
    def __init__(self, router_id, input_ports, outputs, timeout=10):
        self.router_id = router_id
        self.input_ports = input_ports
        self.outputs = outputs  # {router_id: (port, metric)}
        self.routing_table = RoutingTable()
        self.sockets = []  # List to hold all input sockets

        # Create server sockets for each input port
        for port in self.input_ports:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.bind(('localhost', port))
            server_socket.setblocking(False)  # Set socket to non-blocking mode
            self.sockets.append(server_socket)

    def initialize_with_neighbors(self):
        self.routing_table.add_or_update_route(dest_id=self.router_id, next_hop=self.router_id, metric=1, port=0)

    def listen_for_messages(self):
        """Listen for incoming RIP messages on input ports."""
        # Use select to wait for any input sockets to be ready for reading
        readable, _, _ = select.select(self.sockets, [], [], 1)
        for sock in readable:
            data, _ = sock.recvfrom(1024)
            self.handle_incoming_message(data)

    def handle_incoming_message(self, data):
        """Process incoming RIP response messages and update the routing table."""
        if len(data) < 4:
            print("Received malformed RIP packet (too short), dropping...")
            return
        
        rip_packet = bytearray(data)
        
        # Parse RIP header
        command = rip_packet[0]
        version = rip_packet[1]
        sender_id = (rip_packet[2] << 8) | rip_packet[3]  # Router ID
        
        if command != 2 or version != 2:
            print(f"Invalid RIP packet: Command={command}, Version={version}. Dropping packet.")
            return

        self.routing_table.__repr__()

        # Process each entry, 13 bytes per entry)
        num_entries = (len(rip_packet) - 4) // 13
        offset = 4

        for _ in range(num_entries):
            afi = (rip_packet[offset] << 8) | rip_packet[offset + 1]
            dest_id = (rip_packet[offset + 2] << 8) | rip_packet[offset + 3]
            metric = (rip_packet[offset + 12])
            offset += 13  # Move to the next entry
            
            if afi != 2:
                print("error3")

                continue

            if metric < 1 or metric > 16:
                print("error4")

                continue

            # Get the port from sender's known outputs
            peer_port = self.outputs.get(sender_id, (None,))[0]
            if peer_port is None:
                print(f"Unknown sender {sender_id}, ignoring.")
                continue

            # Split-horizon with poisoned reverse: Ignore routes that loop back
            if dest_id == self.router_id:
                continue

            # If route metric is 16 (unreachable), mark for garbage collection
            if metric == 16:
                # self.routing_table.mark_unreachable(dest_id)
                continue

            link_metric = self.outputs.get(sender_id, (None, 1))[1]  # Get the correct link metric
            new_metric = min(metric + link_metric, 16)

            # Update the routing table if necessary
            self.routing_table.add_or_update_route(dest_id, sender_id, new_metric, peer_port)

            # Reset sender's timeout
            print(f"Setting RID: {dest_id} to timeout {time.time()}")
            self.routing_table.routes[dest_id]["timeout"] = time.time()


    def send_rip_message(self, peer_router_id):
        """Send a RIP message to a peer router."""
        peer_port, _ = self.outputs[peer_router_id]
        message = self.routing_table.rip_response(self.router_id, peer_router_id)
        # message = message.encode('utf-8')


        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(message, ('localhost', peer_port))

    def send_periodic_updates(self):
        """Send periodic RIP updates to neighbors."""
        for peer_router_id, _ in self.outputs.items():
            self.send_rip_message(peer_router_id)

    def check_for_dead_routers(self):
        """Check if any routers have timed out."""
        current_time = time.time()
        dead_routers = []

        for router_id, _ in list(self.routing_table.routes.items()):
            last_time = self.routing_table.routes[router_id]["timeout"]
            if current_time - last_time > self.routing_table.timeout:
                # If the router hasn't sent a message within the timeout period, mark it as dead
                print(f"Router {router_id} is considered dead due to timeout.")
                dead_routers.append(router_id)
                self.remove_dead_router(router_id)

        return dead_routers

    def remove_dead_router(self, router_id):
        """Remove the router from the routing table and last_received dictionary."""
        if router_id in self.routing_table.routes:
            del self.routing_table.routes[router_id]
            print(f"Removed dead router {router_id} from routing table.")


def main():
    router = RIPRouter(get_router_id(), get_router_inputs(), get_router_outputs())
    router.initialize_with_neighbors()
    last_update_time = time.time()

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
    try:
        main()
    except(KeyboardInterrupt):
        print("\nExiting Gracefully")
        exit()