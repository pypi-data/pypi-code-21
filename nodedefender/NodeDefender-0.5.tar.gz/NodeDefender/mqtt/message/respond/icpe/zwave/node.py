import NodeDefender

def list(topic, payload):
    return NodeDefender.icpe.sensor.verify_list(topic['mac_address'], *payload)
