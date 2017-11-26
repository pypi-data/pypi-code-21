import NodeDefender

def qry(topic, payload):
    return NodeDefender.icpe.event.system_status(topic['mac_address'], payload)
