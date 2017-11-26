import NodeDefender

def set(topic, payload):
    enabled = bool(eval(payload.pop(0)))
    interval = payload.pop(0)
    server_1 = payload.pop(0)
    server_2 = payload.pop(0)
    return True

def qry(topic, payload):
    enabled = bool(eval(payload.pop(0)))
    interval = payload.pop(0)
    server_1 = payload.pop(0)
    server_2 = payload.pop(0)
    return True
