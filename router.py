from modules.configurator import ROUTERID, INPUTS, OUTPUTS
from modules.socket_server import router_init, fetch, send
from modules.router_table import RouterTable

routing_table = RouterTable()

def main():
    router_init()
    while True:
        fetch()
        send()
        routing_table.garbage_collect()

if __name__ == "__main__":
    main()