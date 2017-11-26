from flask_socketio import emit, send, disconnect, join_room, leave_room, \
        close_room, rooms
from NodeDefender import socketio
import NodeDefender
from flask_login import current_user
from flask import flash, redirect, url_for

@socketio.on('create', namespace='/user')
def create(email, firstname, lastname, group, role):
    if not NodeDefender.db.group.get(group):
        emit('error', ('Group does not exist'), namespace='/general')
        return False

    if NodeDefender.db.user.get(email):
        emit('error', ('User Exists'), namespace='/general')
        return False

    user = NodeDefender.db.user.create(email, firstname, lastname)
    NodeDefender.db.group.add_user(group, email)
    NodeDefender.db.user.set_role(email, role)
    NodeDefender.mail.user.new_user(user)
    emit('reload', namespace='/general')
    return True

@socketio.on('info', namespace='/user')
def info(email):
    user = NodeDefender.db.user.get(email)
    if user:
        return emit('info', user.to_json())
    else:
        return emit('error', "User {} not found".format(email),
                    namespace='/general')

@socketio.on('groups', namespace='/groups')
def groups(email):
    return emit('groups', NodeDefender.db.user.groups(email))

@socketio.on('update', namespace='/user')
def update(kwargs):
    print(kwargs)
    NodeDefender.db.user.update(current_user.email, **kwargs)
    print("OK")
    emit('reload', namespace='/general')
    return True

@socketio.on('name', namespace='/user')
def name(email, firstname, lastname):
    NodeDefender.db.user.update(email, **{'firstname' : firstname,
                                          'lastname' : lastname})
    emit('reload', namespace='/general')
    return True

@socketio.on('role', namespace='/user')
def role(email, role):
    NodeDefender.db.user.set_role(email, role)
    emit('reload', namespace='/general')
    return True

@socketio.on('freeze', namespace='/user')
def freeze_user(email):
    NodeDefender.db.user.disable(email)
    emit('reload', namespace='/general')
    return True

@socketio.on('enable', namespace='/user')
def enable_user(email):
    NodeDefender.db.user.enable(email)
    emit('reload', namespace='/general')
    return True

@socketio.on('resetPassword', namespace='/user')
def reset_password(email):
    NodeDefender.db.user.reset_password(email)
    emit('reload', namespace='/general')
    return True

@socketio.on('delete', namespace='/user')
def delete_user(email):
    try:
        NodeDefender.db.user.delete(email)
    except LookupError:
        emit('error')
        return
    url = url_for('admin_view.admin_users')
    emit('redirect', (url), namespace='/general')
