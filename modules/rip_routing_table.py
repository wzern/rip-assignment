# routing_table = {
#     destination_router_id: {
#         "next_hop": next_hop_router_id,  # Who to forward packets to
#         "metric": metric,                # Distance to the destination (1-16)
#         "port": outgoing_port,            # The port to use to reach next_hop
#         "timeout": timer_value,           # Used for route invalidation
#         "garbage_collection": None        # If expired, scheduled for removal
#     }
# }


import time, datetime

class RoutingTable:
    def __init__(self, timeout=18, garbage_collection_time=6):
        self.routes = {}  # {destination_router_id: route_entry}
        self.timeout = timeout
        self.gc_time = garbage_collection_time

    def add_or_update_route(self, dest_id, next_hop, metric, port):
        if metric > 15:
            return

        if dest_id not in self.routes or self.routes[dest_id]["metric"] > metric:
            self.routes[dest_id] = {
                "next_hop": next_hop,
                "metric": metric,
                "port": port,
                "timeout": time.time() + self.timeout,
                "garbage_collection": 0
            }
        
        


    def __repr__(self):
        """Detailed, structured representation of the routing table."""
        header = (
            "\n=========================== ROUTING TABLE ===========================\n"
            " PEER ROUTER | NEXT HOP | DISTANCE | PORT | ROUTE TIMEOUT | GC TIMER \n"
            "---------------------------------------------------------------------"
        )

        rows = []
        for dest, entry in self.routes.items():
            route_timeout = int(round(entry['timeout'] - time.time()))
            if route_timeout < 0:
                route_timeout = -1
            gc_timer = int(round(entry['garbage_collection']) - time.time())
            if gc_timer < 0:
                gc_timer = 0

            rows.append(
                f" {dest:<11} | {entry['next_hop']:<8} | {entry['metric']:^8} | {entry['port']:^4} "
                f"| {route_timeout:^13} | {gc_timer:^8}"
            )

        return f"{header}\n" + "\n".join(rows) + "\n"

    def __str__(self):
        """User-friendly string representation."""
        return f"<RIPRouter: {len(self.routes)} routes, last updated {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}>"

    def rip_response(self, sender_id, neighbor_id):
        rip_packet = bytearray()
        rip_packet.append(2)  # Command (2 = Response)
        rip_packet.append(2)  # Version (always 2)
        rip_packet.append((sender_id >> 8) & 0xFF)  # Router ID high byte
        rip_packet.append(sender_id & 0xFF)  # Router ID low byte


        # Append route entries
        for dest_id, entry in self.routes.items():
            # Apply split-horizon with poisoned reverse
            if entry["next_hop"] == neighbor_id:
                metric = 16  # Poisoned reverse
            else:
                metric = entry["metric"]

            rip_packet.append(0)  # AFI high byte
            rip_packet.append(2)  # AFI low byte
            rip_packet.append((dest_id >> 8) & 0xFF)  # Destination high byte
            rip_packet.append(dest_id & 0xFF)  # Destination low byte
            rip_packet.extend([0, 0, 0, 0])  # Must be zero (4 bytes)
            rip_packet.extend([0, 0, 0, 0])  # Must be zero (4 bytes)
            rip_packet.append(metric & 0xFF)

        return rip_packet