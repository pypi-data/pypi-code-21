from NodeDefender.mqtt.message import report, respond, command, error
from functools import wraps
import NodeDefender

def mqtt_to_dict(func):
    @wraps(func)
    def wrapper(topic, payload, mqtt):
        topic = topic.split('/')
        NewTopic = {'mac_address' : topic[1][2:]}
        NewTopic['messageType'] = topic[2]
        NewTopic['node'] = topic[4].split(':')[0]
        try:
            NewTopic['endPoint'] = topic[4].split(':')[1]
        except IndexError:
            NewTopic['endPoint'] = None
        NewTopic['commandClass'] = topic[6].split(':')[0]
        try:
            NewTopic['subFunction'] = topic[6].split(':')[1]
        except IndexError:
            NewTopic['subFunction'] = None
        NewTopic['action'] = topic[8]
        
        if '=' not in payload and ',' in payload:
            payload = payload.split(',')
            return func(NewTopic, payload, mqtt)

        NewPayload = {}
        for part in payload.split(' '):
            try:
                key, value = part.split('=')
                NewPayload[key] = value
            except ValueError:
                pass
        return func(NewTopic, NewPayload, mqtt)
    return wrapper

@mqtt_to_dict
def event(topic, payload, mqtt):
    if not NodeDefender.db.icpe.get(topic['mac_address']):
        NodeDefender.db.icpe.create(topic['mac_address'], mqtt)
    if topic['messageType'] == 'cmd':
        return command.event(topic, payload)
    
    NodeDefender.db.mqtt.message_recieved(mqtt['host'], mqtt['port'],
                                          topic['mac_address'])
    if topic['messageType'] == 'rpt':
        NodeDefender.mqtt.logger.debug("Processing Report {}:{} for iCPE {}".\
                                       format(topic['commandClass'],
                                                  topic['action'],
                                                  topic['mac_address']))
        return report.event(topic, payload)
    elif topic['messageType'] == 'rsp':
        NodeDefender.mqtt.logger.debug("Processing Respond {}:{} for iCPE {}".\
                                       format(topic['commandClass'],
                                                  topic['action'],
                                                  topic['mac_address']))

        return respond.event(topic, payload)
    elif topic['messageType'] == 'err':
        NodeDefender.mqtt.logger.debug("Processing Error {}:{} for iCPE {}".\
                                       format(topic['commandClass'],
                                                  topic['action'],
                                                  topic['mac_address']))
        return error.event(topic, payload)
