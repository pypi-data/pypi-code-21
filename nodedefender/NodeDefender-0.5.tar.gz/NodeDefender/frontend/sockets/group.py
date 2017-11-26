from flask_socketio import emit, send, disconnect, join_room, leave_room, \
        close_room, rooms
from NodeDefender import socketio, serializer
import NodeDefender
from flask_login import current_user
from flask import url_for
from geopy.geocoders import Nominatim

@socketio.on('create', namespace='/group')
def create(name, email, location):
    if NodeDefender.db.group.get(name):
        emit('error', ('Group exsists'), namespace='/general')
        return False
    group = NodeDefender.db.group.create(name, email)
    NodeDefender.db.group.location(name, **location)
    NodeDefender.mail.group.new_group(name)
    url = url_for('admin_view.admin_group', name = serializer.dumps(name))
    return emit('redirect', (url), namespace='/general')

@socketio.on('list', namespace='/group')
def list(user = None):
    if user is None:
        user = current_user.email
    return emit('list',  [group.name for group in
                      NodeDefender.db.group.list(user_mail = user)])

@socketio.on('delete', namespace='/group')
def delete(name):
    NodeDefender.db.group.delete(name)
    url = url_for('admin_view.admin_groups')
    return emit('redirect', (url), namespace='/general')

@socketio.on('coordinates', namespace='/group')
def coordinates(street, city):
    geo = Nominatim()
    coords = geo.geocode(street + ' ' + city)
    if coords:
        emit('coordinates', (coords.latitude, coords.longitude))
    else:
        emit('error', "Coordinates not found", namespace='/general')

@socketio.on('info', namespace='/group')
def info(name):
    group = NodeDefender.db.group.get(name)
    if group:
        group = group.to_json()
        return emit('info', group)
    else:
        print("Group: ", name)

@socketio.on('update', namespace='/group')
def update(name, kwargs):
    group = NodeDefender.db.group.update(name, **kwargs)
    url = url_for('admin_view.admin_group', name =
                  serializer.dumps(group.name))
    return emit('redirect', (url), namespace='/general')

@socketio.on('updateLocation', namespace='/group')
def update_location(name, address):
    NodeDefender.db.group.location(name, **address)
    return emit('reload', namespace='/general')

@socketio.on('addUser', namespace='/group')
def add_user(group_name, user_mail):
    NodeDefender.db.group.add_user(group_name, user_mail)
    return emit('reload', namespace='/general')

@socketio.on('removeUser', namespace='/group')
def add_user(group_name, user_mail):
    NodeDefender.db.group.remove_user(group_name, user_mail)
    return emit('reload', namespace='/general')
