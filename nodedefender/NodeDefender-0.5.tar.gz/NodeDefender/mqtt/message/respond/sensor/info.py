import NodeDefender

def qry(topic, payload):
    return NodeDefender.icpe.sensor.\
            sensor_info(topic['mac_address'], topic['node'], **payload)

def sup(topic, payload):
    if type(payload) is not dict:
        return True
    return NodeDefender.icpe.sensor.commandclass.\
            commandclass_types(topic['mac_address'], topic['node'],
                               topic['commandClass'], **payload)

def evtsup(topic, payload):
    return True # Add support later
