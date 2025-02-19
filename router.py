from modules.configurator import ROUTERID, INPUTS, OUTPUTS
from modules.socket_server import router_init, fetch, send

router_init()

while True:
    fetch()
    send()