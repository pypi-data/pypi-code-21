from NodeDefender.db.sql import SQL, GroupModel, UserModel, LocationModel
import NodeDefender
from geopy.geocoders import Nominatim

def get_sql(name):
    try:
        return GroupModel.query.filter_by(name = name).first()
    except Exception:
        return None

def update_sql(group_name, **kwargs):
    group = get_sql(group_name)
    if group is None:
        return False
    for key, value in kwargs.items():
        if key not in group.columns():
            continue
        setattr(group, key, value)
    SQL.session.add(group)
    SQL.session.commit()
    return group

def create_sql(name, email):
    if get_sql(name):
        return get_sql(name)
    group = GroupModel(name, email)
    SQL.session.add(group)
    SQL.session.commit()
    return group

def delete_sql(name):
    if not get_sql(name):
        return False
    SQL.session.delete(get_sql(name))
    SQL.session.commit()
    return True

def get(name):
    return get_sql(name)

def list(user_mail = None):
    if not user_mail:
        return [group for group in GroupModel.query.all()]
    
    user = NodeDefender.db.user.get(user_mail)
    if user.superuser:
        return [group for group in GroupModel.query.all()]
    return [group for group in user.groups]

def create(name, email = None):
    group = create_sql(name, email)
    NodeDefender.db.message.group_created(group)
    return group

def update(group_name, **kwargs):
    return update_sql(group_name, **kwargs)

def location(name, street, city, latitude = None, longitude = None):
    group = get_sql(name)
    if group is None:
        return False
    
    if not latitude and not longitude:
        geo = Nominatim()
        coord = geo.geocode(street + ' ' + city, timeout = 10)
        if coord:
            latitude = coord.latitude
            longitude = coord.longitude
        else:
            longitude = 0.0
            longitude = 0.0

    group.location = LocationModel(street, city, latitude, longitude)
    SQL.session.add(group)
    SQL.session.commit()
    return group

def delete(name):
    return delete_sql(name)

def add_user(group_name, user_mail):
    group = get_sql(group_name)
    user = NodeDefender.db.user.get(user_mail)
    if user is None or group is None:
        return False

    group.users.append(user)
    SQL.session.add(group)
    SQL.session.commit()
    return group

def remove_user(group_name, user_mail):
    group = get_sql(group_name)
    user = NodeDefender.db.user.get(user_mail)
    if user is None or group is None:
        return False

    group.users.remove(user)
    SQL.session.add(group)
    SQL.session.commit()
    return group

def add_mqtt(group_name, mqtt_host, mqtt_port):
    group = get_sql(group_name)
    mqtt = NodeDefender.db.mqtt.get_sql(mqtt_host, mqtt_port)
    if mqtt is None or group is None:
        return False

    group.mqtts.append(mqtt)
    SQL.session.add(group)
    SQL.session.commit()
    return group

def remove_mqtt(group_name, mqtt_host, mqtt_port):
    group = get_sql(group_name)
    mqtt = NodeDefender.db.mqtt.get_sql(mqtt_host, mqtt_port)
    if mqtt is None or group is None:
        return False

    group.mqtts.remove(mqtt)
    SQL.session.add(group)
    SQL.session.commit()
    return group

def add_node(group_name, node_name):
    group = get_sql(group_name)
    node = NodeDefender.db.node.get(node_name)
    if node is None or group is None:
        return False

    group.nodes.append(node)
    SQL.session.add(group)
    SQL.session.commit()
    return group

def remove_node(group_name, node_name):
    group = get_sql(group_name)
    node = NodeDefender.db.node.get(node_name)
    if node is None or group is None:
        return False

    group.nodes.remove(node)
    SQL.session.add(group)
    SQL.session.commit()
    return group
