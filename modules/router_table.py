import time

class RouteEntry:
    def __init__(self, destination, next_hop, metric, timeout=180):
        self.destination = destination
        self.next_hop = next_hop
        self.metric = metric
        self.timeout = timeout
        self.last_updated = time.time()

    def is_expired(self):
        return (time.time() - self.last_updated) > self.timeout

    def update(self, next_hop, metric):
        if metric < self.metric or self.next_hop == next_hop:
            self.next_hop = next_hop
            self.metric = metric
            self.last_updated = time.time()

class RouterTable:
    def __init__(self):
        self.routes = {}

    def add_or_update_route(self, destination, next_hop, metric):
        if destination in self.routes:
            self.routes[destination].update(next_hop, metric)
        else:
            self.routes[destination] = RouteEntry(destination, next_hop, metric)

    def remove_route(self, destination):
        if destination in self.routes:
            del self.routes[destination]

    def get_best_route(self, destination):
        return self.routes.get(destination, None)

    def garbage_collect(self):
        expired_routes = [dest for dest, entry in self.routes.items() if entry.is_expired()]
        for dest in expired_routes:
            del self.routes[dest]

    def print_routing_table(self):
        print("Routing Table:")
        print("Destination | Next Hop | Metric | Last Updated")
        for dest, entry in self.routes.items():
            print(f"{dest:^11} | {entry.next_hop:^8} | {entry.metric:^6} | {time.strftime('%H:%M:%S', time.localtime(entry.last_updated))}")
        print("\n")
