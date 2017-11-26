from NodeDefender.mqtt.message.respond.icpe import sys, zwave

def event(topic, payload):
    if topic['node'] == '0':
        zwave.event(topic, payload)
    elif topic['node'] == 'sys':
        sys.event(topic, payload)
