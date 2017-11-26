from NodeDefender.mqtt.command import fire, topic_format

def qry(mac_address, sensor_id):
    topic = topic_format.format(mac_address, sensor_id, "info", "qry")
    return fire(topic, icpe = mac_address)
