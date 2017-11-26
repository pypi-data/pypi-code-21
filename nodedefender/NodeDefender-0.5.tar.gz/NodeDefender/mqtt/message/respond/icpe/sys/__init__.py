from NodeDefender.mqtt.message.respond.icpe.sys import info, net, svc

def event(topic, payload):
    try:
        eval(topic['commandClass'] + '.' + topic['action'])(topic, payload)
    except NameError:
        NodeDefender.mqtt.logger.warning("Unsupported action {}, {}".\
                                         format(topic['commandClass'],
                                                topic['action']))
        return False
