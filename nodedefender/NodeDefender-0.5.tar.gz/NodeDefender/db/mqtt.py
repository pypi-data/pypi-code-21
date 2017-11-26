from NodeDefender.db.sql import SQL, MQTTModel, GroupModel, iCPEModel
from redlock import RedLock
import NodeDefender

def get_sql(host, port = 1883):
    return MQTTModel.query.filter_by(host = host, port = port).first()

def update_sql(host, port = 1883, **kwargs):
    mqtt = get_sql(host, port)
    if mqtt is None:
        return False

    for key, value in kwargs:
        if key not in mqtt.columns():
            continue
        setattr(mqtt, key, value)

    SQL.session.add(mqtt)
    SQL.session.comit()
    return mqtt

def create_sql(host, port = 1883):
    if get_sql(host, port):
        return False
    
    mqtt = MQTTModel(host, port)
    SQL.session.add(mqtt)
    SQL.session.commit()
    return mqtt

def delete_sql(host, port = 1883):
    mqtt = get_sql(host, port)
    if mqtt is None:
        return False
    SQL.session.delete(mqtt)
    return SQL.session.commit()

def save_sql(model):
    SQL.session.add(model)
    SQL.session.commit()
    return model

def get_redis(host, port):
    return NodeDefender.db.redis.mqtt.get(host, port)

def update_redis(host, port, **kwargs):
    return NodeDefender.db.redis.mqtt.save(host, port, **kwargs)

def delete_redis(host, port):
    return NodeDefender.db.redis.mqtt.flush(host, port)

def get(host, port = 1883):
    mqtt = get_redis(host, port)
    if len(mqtt):
        return mqtt
    if NodeDefender.db.redis.mqtt.load(get_sql(host, port)):
        NodeDefender.db.logger.debug("Loaded MQTT: {}:{}".\
                                     format(host, port))
        return get_redis(host, port)
    return False

def online(host, port):
    mqtt = get(host, port)
    return mqtt['online']

def mark_online(host, port):
    mqtt = get_redis(host, port)
    if not mqtt:
        return False
    if eval(mqtt['online']):
        return mqtt
    NodeDefender.db.logger.info("MQTT {}:{} Online".format(host, port))
    return update_redis(host, port, online = True)

def mark_offline(host, port):
    mqtt = get_redis(host, port)
    if not mqtt:
        return False
    if not eval(mqtt['online']):
        return mqtt
    NodeDefender.db.logger.info("MQTT {}:{} Offline".format(host, port))
    return update_redis(host, port, online = False)

def icpe(mac_address):
    return SQL.session.query(MQTTModel).join(MQTTModel.icpes).\
            filter(iCPEModel.mac_address == mac_address).first()

def create(host, port = 1883):
    return create_sql(host, port)

def delete(host, port = 1883):
    delete_sql(host, port)
    delete_redis(host, port)
    return True

def load():
    mqtts = MQTTModel.query.all()
    for mqtt in mqtts:
        NodeDefender.db.redis.mqtt.load(mqtt)
    return len(mqtts)

def message_sent(host, port, mac_address):
    return NodeDefender.db.redis.mqtt.message_sent(host, str(port), mac_address)

def message_recieved(host, port, mac_address):
    return NodeDefender.db.redis.mqtt.message_recieved(host, str(port), mac_address)

def list(group = None, user = None, icpe = None):
    if group:
        return SQL.session.query(MQTTModel).join(MQTTModel.group).\
                filter(GroupModel.name == group).all()
    if icpe:
        return SQL.session.query(MQTTModel).join(MQTTModel.icpe).\
                filter(iCPEModel.mac_address == icpe).all()
    return MQTTModel.query.all()
