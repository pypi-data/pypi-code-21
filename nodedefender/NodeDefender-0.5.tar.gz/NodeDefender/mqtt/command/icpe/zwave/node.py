from NodeDefender.mqtt.command import fire, topic_format

def list(mac_address):
    topic = topic_format.format(mac_address, "0", "node", "list")
    return fire(topic, icpe = mac_address)
