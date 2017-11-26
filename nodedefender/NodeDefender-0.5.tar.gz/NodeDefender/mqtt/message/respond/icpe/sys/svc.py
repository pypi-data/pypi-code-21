import NodeDefender

def qry(topic, payload):
    telnet = bool(eval(payload.pop(0)))
    http = bool(eval(payload.pop(0)))
    snmp = bool(eval(payload.pop(0)))
    ssh = bool(eval(payload.pop(0)))
    return NodeDefender.db.icpe.update(topic['mac_address'],
                                       **{'telnet' : telnet,
                                          'http' : http,
                                          'snmp' : snmp,
                                          'ssh' : ssh})

def cli(topic, payload):
    enabled = bool(eval(payload))
    return NodeDefender.db.icpe.update(topic['mac_address'],
                                       **{'telnet' : telnet})
def web(topic, payload):
    enabled = bool(eval(payload))
    return NodeDefender.db.icpe.update(topic['mac_address'],
                                       **{'http' : telnet})
def snmp(topic, payload):
    enabled = bool(eval(payload))
    return NodeDefender.db.icpe.update(topic['mac_address'],
                                       **{'snmp' : telnet})
def ssh(topic, payload):
    enabled = bool(eval(payload))
    return NodeDefender.db.icpe.update(topic['mac_address'],
                                       **{'ssh' : telnet})
