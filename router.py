from modules.configurator import ROUTERID, INPUTS, OUTPUTS
from modules.socket_server import router_init, fetch, send
from modules.router_table import RouterTable

def main():
    router_init()
    while True:
        fetch()
        send()

if __name__ == "__main__":
    main()