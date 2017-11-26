from NodeDefender.db.sql import SQL, MessageModel, UserModel, GroupModel, \
        NodeModel, iCPEModel, SensorModel
from sqlalchemy import or_

def messages(user, limit = 10):
    if type(user) is str:
        user = SQL.session.query(UserModel).filter(UserModel.email ==
                                                  user).first()
    
    if user is None:
        return False

    if user.has_role('superuser'):
        return SQL.session.query(MessageModel).\
                order_by(MessageModel.date.desc()).limit(int(limit)).all()
     
    groups = [group for group in user.groups]
    if len(groups) < 1:
        return user.messages
    
    nodes = [node for node in group.nodes for group in groups]
    icpes = [icpe for icpe in node.icpe for icpe in nodes]

    # Revert from list of models to a list of string
    groups = [group.name for group in groups]
    nodes = [node.name for node in nodes]
    icpes = [icpe.mac_address for icpe in icpes]

    gq = SQL.session.query(MessageModel).join(MessageModel.group).\
            filter(GroupModel.name.in_(groups))
    nq = SQL.session.query(MessageModel).join(MessageModel.node).\
            filter(NodeModel.name.in_(nodes))
    iq = SQL.session.query(MessageModel).join(MessageModel.icpe).\
            filter(iCPEModel.mac_address.in_(icpes))

    return gq.union(nq).union(iq).order_by(MessageModel.date.desc()).\
            limit(int(limit)).all()

def group_messages(group, limit = 10):
    if type(group) is str:
        group = SQL.session.query(GroupModel).filter(GroupModel.name ==
                                                    group).first()
    if group is None:
        return False
    return group.messages

    nodes = [node for node in group.nodes]
    icpes = [node.icpe for node in nodes if node.icpe]
    sensors = [sensor.id for sensor in [icpe.sensors for icpe in icpes][0]]

    # Revert from list for models to a list for strings
    nodes = [node.name for node in nodes]
    icpes = [icpe.mac_address for icpe in icpes]

    return SQL.session.query(MessageModel).\
            join(MessageModel.group).\
            join(MessageModel.node).\
            join(MessageModel.icpe).\
            join(MessageModel.sensor).\
            filter(GroupModel.name == group.name,\
                       NodeModel.name.in_(*[nodes]),\
                       iCPEModel.mac_address.in_(*[icpes]),\
                       SensorModel.id.in_(*[sensors])\
                      ).order_by(MessageModel.date.desc()).limit(int(limit)).all()

def user_messages(user, limit = 10):
    if type(user) is str:
        user = SQL.session.query(UserModel).\
                filter(UserModel.email == user).first()

    if user is None:
        return False

    return SQL.session.query(MessageModel).\
            filter(MessageModel.user.email == user.email).\
            order_by(MessageModel.date.desc()).limit(int(limit)).all()

def node_messages(node, limit = 10):
    if type(node) is str:
        node = SQL.session.query(NodeModel).filter(NodeModel.name == node).first()

    if node is None:
        return False
    node_query = SQL.session.query(MessageModel).join(MessageModel.node).\
            filter(NodeModel.name == node.name)
    icpe_query = SQL.session.query(MessageModel).join(MessageModel.icpe).\
            filter(iCPEModel.mac_address == node.icpe.mac_address)
    sensor_query = SQL.session.query(MessageModel).join(MessageModel.sensor).\
            filter(SensorModel.sensor_id.\
                   in_([sensor.sensor_id for sensor in node.icpe.sensors]))
    
    return node_query.union(icpe_query).union(sensor_query).order_by(MessageModel.date.desc()).\
            limit(int(limit)).all()

def group_created(group):
    subject = "Group Created"
    body = _group_created_template.format(group.name, group.email)
    message = MessageModel(subject, body)
    group.messages.append(message)
    SQL.session.add(group)
    SQL.session.commit()
    return True

def user_created(user):
    subject = "User Created"
    body = _user_created_template.format(user.email)
    message = MessageModel(subject, body)
    user.messages.append(message)
    SQL.session.add(user)
    SQL.session.commit()
    return True

def node_created(node):
    subject = "Node Created"
    body = _node_created_template.format(node.name)
    message = MessageModel(subject, body)
    node.messages.append(message)
    SQL.session.add(node)
    SQL.session.commit()
    return True

def icpe_created(icpe):
    subject = "iCPE Created"
    body = _icpe_created_template.format(icpe.mac_address)
    message = MessageModel(subject, body)
    icpe.messages.append(message)
    SQL.session.add(icpe)
    SQL.session.commit()
    return True

def icpe_online(icpe):
    subject = "iCPE Online"
    body = "iCPE {} became Online".format(icpe.mac_address)
    message = MessageModel(subject, body)
    icpes.messages.append(message)
    SQL.session.add(icpe)
    SQL.session.commit()
    return True

def icpe_offline(icpe):
    subject = "iCPE Offline"
    body = "iCPE {} became Offline".format(icpe.mac_address)
    message = MessageModel(subject, body)
    icpes.messages.append(message)
    SQL.session.add(icpe)
    SQL.session.commit()
    return True

def sensor_created(sensor):
    subject = "Sensor Created"
    body = _sensor_created_template.format(sensor.name,
                                              sensor.icpe.mac_address)
    message = MessageModel(subject, body)
    sensor.messages.append(message)
    SQL.session.add(message)
    SQL.session.commit()
    return True

_group_created_template = "Group {} created. Mail Address: {}."
_user_created_template = "User {} created"
_node_created_template = "Node {} created"
_icpe_created_template = "iCPE {} created"
_sensor_created_template = "Sensor {} created. Connected to iCPE {}"
