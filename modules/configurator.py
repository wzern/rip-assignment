import sys

from modules.input_validator import port_validator, id_validator

if len(sys.argv) <2:
    print("Not enough arguments")
    exit()

config = open(sys.argv[1], "r").readlines()

try:
    if not config[0].startswith("router-id "):
        raise ValueError("Invalid format: 'router-id' line is missing or incorrectly formatted.")
    router_id_str = config[0].split("router-id ")[1].strip()
    if not router_id_str:
        raise ValueError("Invalid format: No router ID specified after 'router-id'.")
    try:
        router_id = int(router_id_str)
    except ValueError:
        raise ValueError(f"Invalid format: '{router_id_str}' is not a valid integer.")
    id_validator(router_id)

except (IndexError, ValueError) as e:
    print(f"Error processing config file: {e}")
    exit()

try:
    if not config[1].startswith("input-ports "):
        raise ValueError("Invalid format: 'input-ports' line is missing or incorrectly formatted.")
    
    input_ports_str = config[1].split("input-ports ")[1].strip()
    if not input_ports_str:
        raise ValueError("Invalid format: No ports specified after 'input-ports'.")

    input_ports = []
    for port in input_ports_str.split(","):
        port = port.strip()
        if not port.isdigit():
            raise ValueError(f"Invalid port '{port}': Ports must be integers.")

        port = int(port)
        port_validator(port, input_ports)
        input_ports.append(port)

except (IndexError, ValueError) as e:
    print(f"Error processing config file: {e}")
    exit()

    
try:
    if not config[2].startswith("outputs "):
        raise ValueError("Invalid format: 'outputs' line is missing or incorrectly formatted.")

    outputs_str = config[2].split("outputs ")[1].strip()
    if not outputs_str:
        raise ValueError("Invalid format: No outputs specified after 'outputs'.")

    outputs_list = outputs_str.split(",")
    outputs = {}
    for output_str in outputs_list:
        parts = output_str.strip().split("-")

        if len(parts) != 3:
            raise ValueError(f"Invalid format: '{output_str}' must be in the format 'port-metric-router-id'.")

        try:
            port, metric, router_id = map(int, parts)
        except ValueError:
            raise ValueError(f"Invalid format: '{output_str}' contains non-integer values.")

        port_validator(port, [])
        id_validator(router_id)

        if port in outputs:
            raise ValueError(f"Duplicate output port detected: {port} is already connected.")
        
        if metric not in range(1,16):
            raise ValueError(f"Metric {metric} must be between 1 and 15")

        outputs[port] = (metric, router_id)

except (IndexError, ValueError) as e:
    print(f"Error processing config file: {e}")
    exit()

ROUTERID = router_id
INPUTS = input_ports
OUTPUTS = outputs