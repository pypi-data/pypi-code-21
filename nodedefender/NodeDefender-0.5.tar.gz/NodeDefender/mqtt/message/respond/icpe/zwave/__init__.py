from NodeDefender.mqtt.message.respond.icpe.zwave import info
from NodeDefender.mqtt.message.respond.icpe.zwave import node
import NodeDefender

def event(topic, payload):
    try:
        eval(topic['commandClass'] + '.' + topic['action'])(topic, payload)
    except NameError:
        NodeDefender.mqtt.logger.warning("Unsupported action {}, {}".\
                                         format(topic['commandClass'],
                                                topic['action']))
        return False
