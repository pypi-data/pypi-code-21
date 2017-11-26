from NodeDefender.mqtt.command import fire, topic_format

def include(mac_address):
    topic = topic_format.format(mac_address, "0", "mode", "include")
    return fire(topic, icpe = mac_address)

def exclude(mac_address):
    topic = topic_format.format(mac_address, "0", "mode", "exclude")
    return fire(topic, icpe = mac_address)
