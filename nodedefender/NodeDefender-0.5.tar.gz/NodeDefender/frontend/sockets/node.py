from flask_socketio import emit, send, disconnect, join_room, leave_room, \
        close_room, rooms
from NodeDefender import socketio, serializer
import NodeDefender
from flask import jsonify, url_for
from geopy.geocoders import Nominatim

@socketio.on('create', namespace='/node')
def create(name, group, location):
    NodeDefender.db.node.create(name)
    NodeDefender.db.group.add_node(group, name)
    NodeDefender.db.node.location(name, **location)
    NodeDefender.mail.node.new_node(group, name)
    url = url_for('node_view.nodes_node', name = serializer.dumps(name))
    emit('redirect', (url), namespace='/general')
    return True

@socketio.on('delete', namespace='/node')
def delete(name):
    NodeDefender.db.node.delete(name)
    url = url_for('node_view.nodes_list')
    emit('redirect', (url), namespace='/general')
    return True

@socketio.on('info', namespace='/node')
def info(name):
    node = NodeDefender.db.node.get_sql(name)
    node = node.to_json()
    return emit('info', node)

@socketio.on('list', namespace='/node')
def list(groups):
    if type(groups) is str:
        groups = [groups]
    nodes = NodeDefender.db.node.list(*groups)
    return emit('list', [node.to_json() for node in nodes])

@socketio.on('addiCPE', namespace='/node')
def add_icpe(node_name, icpe_mac_address):
    try:
        NodeDefender.db.node.add_icpe(node_name, icpe_mac_address)
        emit('reload', namespace='/general')
    except KeyError as e:
        emit('error', e, namespace='/general')
    return True

@socketio.on('removeiCPE', namespace='/node')
def remove_icpe(node, mac_address):
    try:
        NodeDefender.db.node.remove_icpe(node_name, icpe_mac_address)
        emit('reload', namespace='/general')
    except KeyError as e:
        emit('error', e, namespace='/general')
    return True

@socketio.on('location', namespace='/node')
def location(name):
    return emit('location', NodeDefender.db.node.get(name).location.to_json())

@socketio.on('update', namespace='/node')
def update(name, kwargs):
    node = NodeDefender.db.node.update(name, **kwargs)
    url = url_for('node_view.nodes_node', name = serializer.dumps(node.name))
    emit('redirect', (url), namespace='/general')
    return True

@socketio.on('updateLocation', namespace='/node')
def update_location(name, location):
    NodeDefender.db.node.location(name, **location)
    return emit('reload', namespace='/general')

@socketio.on('coordinates', namespace='/node')
def coordinates(street, city):
    geo = Nominatim()
    geocords = geo.geocode(street + ' ' + city)
    if geocords:
        emit('coordinates', (geocords.latitude, geocords.longitude))
    else:
        emit("warning", "Coordinated no found", namespace='/general')
    return True
