from flask_socketio import emit, send
import NodeDefender

@NodeDefender.socketio.on('create', namespace='/mqtt')
def create(host, port, group):
    try:
        NodeDefender.db.mqtt.create(host, port)
    except AttributeError as e:
        emit('error', e, namespace='/general')
    NodeDefender.db.group.add_mqtt(group, host, port)
    NodeDefender.mail.group.new_mqtt(group.name, mqtt.host, mqtt.port)
    LoadMQTT([mqtt])
    emit('reload', namespace='/general')
    return True

@NodeDefender.socketio.on('list', namespace='/mqtt')
def list(group):
    emit('list', NodeDefender.db.mqtt.list(group))
    return True

@NodeDefender.socketio.on('info', namespace='/mqtt')
def info(host, port):
    emit('info', NodeDefender.db.mqtt.get_redis(host, port))
    return True
