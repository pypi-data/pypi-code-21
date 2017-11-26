from NodeDefender.mqtt.command import fire, topic_format

def qry(mac_address):
    topic = topic_format.format(mac_address, "sys", "svc", "qry")
    return fire(topic, icpe = mac_address)

def telnet(mac_address, enabled):
    topic = topic_format.format(mac_address, "sys", "svc:cli", "set")
    return fire(topic, payload = str(int(enabled)), icpe = mac_address)

def ssh(mac_address, enabled):
    topic = topic_format.format(mac_address, "sys", "svc:ssh", "set")
    return fire(topic, payload = str(int(enabled)), icpe = mac_address)

def web(mac_address, enabled):
    topic = topic_format.format(mac_address, "sys", "svc:web", "st")
    return fire(topic, payload = str(int(enabled)), icpe = mac_address)

def snmp(mac_address, enabled):
    topic = topic_format.format(mac_address, "sys", "svc:snmp", "set")
    return fire(topic, payload = str(int(enabled)), icpe = mac_address)
