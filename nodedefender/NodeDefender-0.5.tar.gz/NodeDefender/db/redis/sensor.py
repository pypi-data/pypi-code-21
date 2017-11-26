from NodeDefender.db.redis import redisconn
import NodeDefender
from datetime import datetime

@redisconn
def load(sensor, conn):
    if sensor is None:
        return None
    s = {
        'name' : sensor.name,
        'icpe' : sensor.icpe.mac_address,
        'sensor_id' : sensor.sensor_id,
        'vendor_id' : sensor.vendor_id,
        'product_type' : sensor.product_type,
        'product_id' : sensor.product_id,
        'vendor_name' : sensor.vendor_name,
        'product_name' : sensor.product_name,
        'device_type' : sensor.device_type,
        'library_type' : sensor.library_type,
        'sleepable' : sensor.sleepable,
        'wakeup_interval' : sensor.wakeup_interval,
        'date_updated' : datetime.now().timestamp(),
        'date_created' : sensor.date_created.timestamp(),
        'date_loaded' : datetime.now().timestamp()
    }
    conn.sadd(sensor.icpe.mac_address + ':sensors', sensor.sensor_id)
    return conn.hmset(sensor.icpe.mac_address + sensor.sensor_id, s)

@redisconn
def get(mac_address, sensor_id, conn):
    return conn.hgetall(mac_address + sensor_id)

@redisconn
def save(mac_address, sensor_id, conn, **kwargs):
    sensor = conn.hgetall(mac_address + sensor_id)
    for key, value in kwargs.items():
        sensor[key] = value
    sensor['date_updated'] = datetime.now().timestamp()
    NodeDefender.db.redis.icpe.updated(mac_address)
    return conn.hmset(mac_address + sensor_id, sensor)

@redisconn
def list(mac_address, conn):
    return conn.smembers(mac_address + ':sensors')

@redisconn
def updated(mac_address, sensor_id, conn):
    return conn.hmset(mac_address + sensor_id, {'date_updated' : \
                                           datetime.now().timestamp()})

@redisconn
def flush(mac_address, sensor_id, conn):
    if conn.hkeys(mac_address + sensor_id):
        conn.srem(mac_address + ':sensors', sensor_id)
        return conn.hdel(mac_address + sensor_id, *conn.hkeys(mac_address + sensor_id))
    else:
        return True
