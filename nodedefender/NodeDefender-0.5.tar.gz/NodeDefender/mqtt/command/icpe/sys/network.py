from NodeDefender.mqtt.command import fire, topic_format

def set(mac_address, *args):
    topic = topic_format.format(mac_address, "sys", "net", "set")
    payload = list(args)
    return fire(topic, payload = payload, icpe = mac_address)

def qry(mac_address):
    topic = topic_format.format(mac_address, "sys", "net", "qry")
    return fire(topic, icpe = mac_address)

def stat(mac_address):
    topic = topic_format.format(mac_address, "sys", "net", "stat")
    return fire(topic, icpe = mac_address)
