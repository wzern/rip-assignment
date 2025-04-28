import sys

if len(sys.argv) <2:
    print("Not enough arguments")
    exit()

config = open(sys.argv[1], "r").readlines()

def port_validator(port, current_ports):
    """Validates a port number for RIP configuration"""
    if not isinstance(port, int):
        raise ValueError(f"Invalid port '{port}': Must be an integer.")

    if not (1024 <= port <= 64000):
        raise ValueError(f"Port {port} is out of bounds! Must be between 1024 and 64000.")

    if port in current_ports:
        raise ValueError(f"Port {port} is already in use!")

    return True

def id_validator(router_id):
    """Validates a router ID"""
    if not isinstance(router_id, int):
        raise ValueError(f"Invalid router ID '{router_id}': Must be an integer.")

    if not (1 <= router_id <= 64000):
        raise ValueError(f"Router ID {router_id} is out of valid range! Must be between 1 and 64000.")

    return True

def get_router_id():
    router_id = 0
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

    return router_id

def get_router_inputs():
    input_ports = []
    try:
        if not config[1].startswith("input-ports "):
            raise ValueError("Invalid format: 'input-ports' line is missing or incorrectly formatted.")
        
        input_ports_str = config[1].split("input-ports ")[1].strip()
        if not input_ports_str:
            raise ValueError("Invalid format: No ports specified after 'input-ports'.")

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

    return input_ports

def get_router_outputs():
    outputs = {}
    try:
        if not config[2].startswith("outputs "):
            raise ValueError("Invalid format: 'outputs' line is missing or incorrectly formatted.")

        outputs_str = config[2].split("outputs ")[1].strip()
        if not outputs_str:
            raise ValueError("Invalid format: No outputs specified after 'outputs'.")

        outputs_list = outputs_str.split(",")
        
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

            outputs[router_id] = (port, metric)

    except (IndexError, ValueError) as e:
        print(f"Error processing config file: {e}")
        exit()

    return outputs