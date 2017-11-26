from NodeDefender.mqtt.message.report.icpe.zwave import info
import NodeDefender

def event(topic, payload):
    try:
        eval(topic['commandClass'] + '.' + topic['action'])(topic, payload)
    except (NameError, AttributeError):
        NodeDefender.mqtt.logger.warning("Unsupported action {}, {}".\
                                         format(topic['commandClass'],
                                                topic['action']))
        return False
