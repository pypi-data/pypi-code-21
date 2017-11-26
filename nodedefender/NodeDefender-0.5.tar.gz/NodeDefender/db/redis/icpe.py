from NodeDefender.db.redis import redisconn
from datetime import datetime

@redisconn
def load(icpe, conn):
    if icpe is None:
        return None
    i = {
        'name' : icpe.name,
        'node' : icpe.node.name if icpe.node else "unassigned",
        'sensors' : len(icpe.sensors),
        'mqtt' : icpe.mqtt[0].host + ':' + str(icpe.mqtt[0].port),
        'mac_address' : icpe.mac_address,
        'serial_number' : icpe.serial_number,
        'firmware' : icpe.firmware,
        'hardware' : icpe.hardware,
        'ip_address' : icpe.ip_address,
        'ip_dhcp' : icpe.ip_dhcp,
        'ip_gateway' : icpe.ip_gateway,
        'ip_subnet' : icpe.ip_subnet,
        'online' : False,
        'telnet' : icpe.telnet,
        'ssh' : icpe.ssh,
        'http' : icpe.http,
        'snmp' : icpe.snmp,
        'battery' : None,
        'date_created' : icpe.date_created.timestamp(),
        'date_updated' : datetime.now().timestamp(),
        'date_loaded' : datetime.now().timestamp()
    }
    return conn.hmset(icpe.mac_address, i)

@redisconn
def get(mac_address, conn):
    return conn.hgetall(mac_address)

@redisconn
def save(mac_address, conn, **kwargs):
    icpe = conn.hgetall(mac_address)
    for key, value in kwargs.items():
        icpe[key] = value
    icpe['date_updated'] = datetime.now().timestamp()
    return conn.hmset(mac_address, icpe)

@redisconn
def list(node, conn):
    return conn.smembers(node + ":icpes")

@redisconn
def updated(mac_address, conn):
    return conn.hmset(mac_address, {'date_updated' : datetime.now().timestamp()})

@redisconn
def flush(mac_address, conn):
    if conn.hkeys(mac_address):
        return conn.hdel(mac_address, *conn.hkeys(mac_address))
    else:
        return True
