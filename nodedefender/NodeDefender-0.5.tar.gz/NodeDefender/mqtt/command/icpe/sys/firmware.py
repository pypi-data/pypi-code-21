from NodeDefender.mqtt.command import fire, topic_format

def upgrade(mac_address, *args):
    topic = topic_format.format(mac_address, "sys", "fw", "upgrade")
    payload = list(args)
    return fire(topic, payload = payload, icpe = mac_address)
