def port_validator(port, current_ports):
    if not port.is_integer():
        print("NOT INT!!!!")
        exit()
    if not 1024 <= port <= 64000:
        print("out of bounds!!!")
        exit()
    if port in current_ports:
        print("already in use")
        exit()
    return 1

def id_validator(id):
    if id not in range(1,64001):
        print("cry")
        exit()
    return 1