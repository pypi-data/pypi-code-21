from NodeDefender.mqtt.message.respond import icpe, sensor

def event(topic, payload):
    if topic['node'] == '0' or topic['node'] == 'sys':
        icpe.event(topic, payload)
    else:
        sensor.event(topic, payload)
