from flask_socketio import emit, send
import NodeDefender

@NodeDefender.socketio.on('general', namespace='/admin')
def general_info():
    info = {'hostname' : NodeDefender.hostname,
            'release' : NodeDefender.release,
            'date_loaded' : str(NodeDefender.date_loaded),
            'run_mode' : NodeDefender.config.general.run_mode()}
    emit('general', info)
    return True

@NodeDefender.socketio.on('logging', namespace='/admin')
def logging():
    info = {'enabled' : NodeDefender.config.logging.enabled(),
            'type' : NodeDefender.config.logging.type(),
            'name' : NodeDefender.config.logging.name(),
            'server' : NodeDefender.config.logging.server(),
            'port' : NodeDefender.config.logging.port()}
    return emit('logging', info)

@NodeDefender.socketio.on('database', namespace='/admin')
def database():
    info = {'enabled' : NodeDefender.config.database.enabled(),
            'engine' : NodeDefender.config.database.engine(),
            'server' : NodeDefender.config.database.server(),
            'port' : NodeDefender.config.database.port(),
            'database' : NodeDefender.config.database.db(),
            'file' : NodeDefender.config.database.file()}
    return emit('database', info)

@NodeDefender.socketio.on('celery', namespace='/admin')
def celery():
    info = {'enabled' : NodeDefender.config.celery.enabled(),
            'broker' : NodeDefender.config.celery.broker(),
            'server' : NodeDefender.config.celery.server(),
            'port' : NodeDefender.config.celery.port(),
            'database' : NodeDefender.config.celery.database()}
    return emit('celery', info)

@NodeDefender.socketio.on('mail', namespace='/admin')
def mail():
    info = {'enabled' : NodeDefender.config.mail.enabled(),
            'server' : NodeDefender.config.mail.server(),
            'port' : NodeDefender.config.mail.port(),
            'tls' : NodeDefender.config.mail.tls(),
            'ssl' : NodeDefender.config.mail.ssl(),
            'username' : NodeDefender.config.mail.username(),
            'password' : NodeDefender.config.mail.password()}
    return emit('mail', info)

@NodeDefender.socketio.on('mqttCreate', namespace='/admin')
def create(host, port, group):
    try:
        NodeDefender.db.mqtt.create(host, port)
    except AttributeError as e:
        emit('error', e, namespace='/general')
    NodeDefender.db.group.add_mqtt(group, host, port)
    NodeDefender.mail.group.new_mqtt(group, host, port)
    NodeDefender.mqtt.connection.add(host, port)
    emit('reload', namespace='/general')
    return True

@NodeDefender.socketio.on('mqttList', namespace='/admin')
def list(group):
    emit('list', NodeDefender.db.mqtt.list(group))
    return True

@NodeDefender.socketio.on('mqttInfo', namespace='/admin')
def info(host, port):
    mqtt = NodeDefender.db.mqtt.get_redis(host, port)
    sql_mqtt = NodeDefender.db.mqtt.get_sql(host, port)
    mqtt['icpes'] = [icpe.mac_address for icpe in sql_mqtt.icpes]
    mqtt['groups'] = [group.name for group in sql_mqtt.groups]
    emit('mqttInfo', mqtt)
    return True

@NodeDefender.socketio.on('mqttUpdateHost', namespace='/admin')
def update_mqtt(current_host, new_host):
    mqtt = NodeDefender.db.mqtt.get_sql(current_host['host'],
                                        current_host['port'])
    mqtt.host = new_host['host']
    mqtt.port = new_host['port']
    NodeDefender.db.mqtt.save_sql(mqtt)
    emit('reload', namespace='/general')
    return True

@NodeDefender.socketio.on('mqttDeleteHost', namespace='/admin')
def delete_mqtt(host, port):
    NodeDefender.db.mqtt.delete(host, port)
    emit('reload', namespace='/general')
    return True

