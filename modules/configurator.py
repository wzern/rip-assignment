import sys

from modules.input_validator import port_validator, id_validator

if len(sys.argv) <2:
    print("Not enough arguments")
    exit()

config = open(sys.argv[1], "r").readlines()

# Set Router ID
router_id = int(config[0].split("router-id ")[1])
id_validator(router_id)

# Set Router Input Ports
input_ports_str = config[1].split("input-ports ")[1].split(",")
input_ports = []
for port in input_ports_str:
    port = int(port.strip())
    port_validator(port, input_ports)
    input_ports.append(port)
    
# Set Router Connections
outputs_list = config[2].split("outputs ")[1].split(",")
outputs = dict()
for output_str in outputs_list:
    output = [int(output) for output in output_str.split("-")]

    port_validator(output[0], [])
    id_validator(output[2])

    if outputs.get(output[0]):
        print("Already connected")
        exit()
    outputs[output[0]] = output[1:3]

ROUTERID = router_id
INPUTS = input_ports
OUTPUTS = outputs