from datetime import datetime
import NodeDefender
from NodeDefender.db.redis import redisconn

@redisconn
def load(commandclass, conn, **kwargs):
    if commandclass is None:
        return None
    mac_address = commandclass.sensor.icpe.mac_address
    sensor_id = commandclass.sensor.sensor_id
    name = kwargs['name']
    currently_loaded = get(mac_address, sensor_id, name)
    if currently_loaded:
        if datetime.now().timestamp() - float(currently_loaded['date_updated']) > 180:
            return currently_loaded

    kwargs['mac_address'] = mac_address
    kwargs['sensor_id'] = sensor_id
    kwargs['commandclass_name'] = commandclass.name
    kwargs['value'] = None
    kwargs['date_updated'] = datetime.now().timestamp()
    kwargs['date_loaded'] = datetime.now().timestamp()
    conn.sadd(commandclass.sensor.icpe.mac_address +\
              commandclass.sensor.sensor_id +':fields', kwargs['name'])
    for key, value in kwargs.items():
        kwargs[key] = str(value)
    conn.hmset(kwargs['mac_address']+kwargs['sensor_id']+kwargs['name'], kwargs)
    return kwargs

@redisconn
def save(mac_address, sensor_id, field_name, conn, **kwargs):
    field  = conn.hgetall(mac_address + sensor_id + field_name)
    for key, value in kwargs.items():
        field[key] = str(value)
    field['date_updated'] = datetime.now().timestamp()
    NodeDefender.db.redis.icpe.updated(mac_address)
    NodeDefender.db.redis.sensor.updated(mac_address, sensor_id)
    return conn.hmset(mac_address + sensor_id + field_name, field)

@redisconn
def list(mac_address, sensor_id, conn):
    return conn.smembers(mac_address + sensor_id + ":fields")

@redisconn
def get(mac_address, sensor_id, name, conn):
    return conn.hgetall(mac_address + sensor_id + name)

@redisconn
def flush(mac_address, sensor_id, name, conn):
    if conn.hkeys(mac_address+ sensor_id + name):
        conn.srem(mac_address + sensor_id + ':fields', name)
        return conn.hdel(mac_address + sensor_id + name, \
                         *conn.hkeys(mac_address+ sensor_id + name))
    else:
        return True
