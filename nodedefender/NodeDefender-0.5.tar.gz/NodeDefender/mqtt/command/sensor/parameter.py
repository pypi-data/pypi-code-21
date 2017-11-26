import NodeDefender

def get(mac_address, sensor_id, number):
    topic = NodeDefender.mqtt.command.\
            topic_format.format(mac_address, sensor_id, "config", "get")
    NodeDefender.mqtt.command.fire(topic, icpe = mac_address,
                                   payload = number)
    return True

def set(mac_address, sensor_id, number, size, value):
    topic = NodeDefender.mqtt.command.\
            topic_format.format(mac_address, sensor_id, "config", "set")
    payload = number
    for x in range(int(size)):
        payload += ' 0 '
    payload += value
    NodeDefender.mqtt.command.fire(topic, icpe = mac_address,
                                   payload = payload)
    return True
