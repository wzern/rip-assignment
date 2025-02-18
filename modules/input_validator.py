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
