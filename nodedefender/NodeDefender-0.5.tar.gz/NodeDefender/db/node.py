from NodeDefender.db.sql import SQL, GroupModel, NodeModel, LocationModel, UserModel
import NodeDefender
from geopy.geocoders import Nominatim

def get_sql(name):
    return NodeModel.query.filter_by(name = name).first()

def update_sql(original_name, **kwargs):
    node = get_sql(original_name)
    if node is None:
        return False
    for key, value in kwargs.items():
        if key not in node.columns():
            continue
        setattr(node, key, value)
    SQL.session.add(node)
    SQL.session.commit()
    return node

def create_sql(name):
    if get_sql(name):
        return get_sql(name)
    node = NodeModel(name)
    SQL.session.add(node)
    SQL.session.commit()
    return node

def save_sql(node):
    SQL.session.add(node)
    return SQL.session.commit()

def delete_sql(name):
    if not get_sql(name):
        return False
    SQL.session.delete(get_sql(name))
    SQL.session.commit()
    return True

def get(name):
    return get_sql(name)

def list(*groups):
    return SQL.session.query(NodeModel).join(NodeModel.groups).\
            filter(GroupModel.name.in_(groups)).all()

def unassigned():
    return SQL.session.query(NodeModel).filter(NodeModel.groups == None).all()

def create(name):
    node = create_sql(name)
    NodeDefender.db.message.node_created(node)
    return node

def update(original_name, **kwargs):
    return update_sql(original_name, **kwargs)

def location(name, street, city, latitude = None, longitude = None):
    node = get_sql(name)
    if node is None:
        return False

    if not latitude and not longitude:
        geo = Nominatim()
        coord = geo.geocode(street + ' ' + city, timeout = 10)
        if coord:
            latitude = coord.latitude
            longitude = coord.longitude
        else:
            latitude = 0.0
            longitude = 0.0
    
    node.location = LocationModel(street, city, latitude, longitude)
    SQL.session.add(node)
    SQL.session.commit()
    return node


def delete(name):
    return delete_sql(name)

def add_icpe(nodeName, icpeMac):
    node = get_sql(nodeName)
    icpe = NodeDefender.db.icpe.get_sql(icpeMac)
    if icpe is None or node is None:
        return False

    node.icpe = icpe
    SQL.session.add(node)
    SQL.session.commit()
    return node

def remove_icpe(nodeName, icpeMac):
    node = get_sql(nodeName)
    icpe = NodeDefender.db.icpe.get(icpeMAc)
    if icpe is None or node is None:
        return False

    node.icpe = None
    SQL.session.add(node)
    SQL.session.commit()
    return node
