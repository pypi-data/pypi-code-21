from NodeDefender.mqtt.command import fire, topic_format

def reboot(mac_address):
    topic = topic_format.format(mac_address, "sys", "sys", "reboot")
    return fire(topic, icpe = mac_address)

def battery(mac_address):
    topic = topic_format.format(mac_address, "sys", "sys:battery", "qry")
    return fire(topic, icpe = mac_address)

