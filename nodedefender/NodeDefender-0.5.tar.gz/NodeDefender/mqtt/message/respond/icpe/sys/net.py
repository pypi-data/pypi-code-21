import NodeDefender

def set(topic, payload):
    return NodeDefender.mqtt.icpe.system_info(topic['mac_address'])

def qry(topic, payload):
    dhcp = bool(eval(payload.pop(0)))
    return NodeDefender.db.icpe.update(topic['mac_address'],
                                       **{'ip_dhcp' : dhcp})

def stat(topic, payload):
    address = payload.pop(0)
    subnet = payload.pop(0)
    gateway = payload.pop(0)
    return NodeDefender.db.icpe.update(topic['mac_address'],
                                       **{'ip_address' : address,
                                          'ip_subnet' : subnet,
                                          'ip_gateway' : gateway})
