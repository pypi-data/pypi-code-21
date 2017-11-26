from NodeDefender.mqtt.command import fire, topic_format

def sup(mac_address, sensor_id, classname):
    topic = topic_format.format(mac_address, sensor_id, classname + ':sup', 'get')
    return fire(topic, icpe = mac_address)
