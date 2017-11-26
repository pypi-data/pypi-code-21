from NodeDefender.mqtt.command import fire, topic_format

def save(mac_address):
    topic = topic_format.format(mac_address, 'sys', 'config', 'save')
    return fire(topic, icpe = mac_address)

def default(mac_address):
    topic = topic_format.format(mac_address, 'sys', 'config', 'default')
    return fire(topic, icpe = mac_address)

def backup(mac_address, *args):
    payload = list(args)
    topic = topic_format.format(mac_address, 'sys', 'config', 'backup')
    return fire(topic, payload = payload, icpe = mac_address)

def restore(mac_address, *args):
    payload = list(args)
    topic = topic_format.format(mac_address, 'sys', 'config', 'restore')
    return fire(topic, payload = payload, icpe = mac_address)
