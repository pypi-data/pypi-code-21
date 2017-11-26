from datetime import datetime, timedelta
from NodeDefender.db.sql import SQL, EventModel, NodeModel
from sqlalchemy import or_, desc

def average(node, time_ago = None):
    if time_ago is None:
        time_ago = (datetime.now() - timedelta(days=1))

    node = SQL.session.query(NodeModel).filter(NodeModel.name == node).first()
    if node is None or not node.icpe or not node.icpe.sensors:
        return False

    total_events = SQL.session.query(EventModel).\
            join(EventModel.icpe).\
            filter(iCPEModel.mac_address == node.icpe.mac_address).\
            filter(EventModel.date > time_ago).all()

    ret_data = {}
    ret_data['node'] = node.name
    ret_data['total'] = len(total_events)
    ret_data['critical'] = len([event for event in total_events if
                                event.critical])
    ret_data['normal'] = len([event for event in total_events if
                              event.normal])
    return ret_data



def latest(node):
    return EventModel.query.filter_by(name = node).first()

def get(node, from_date = None, to_date = None, limit = None):

    if from_date == None:
        from_date = (datetime.now() - timedelta(days = 7))
    
    if to_date == None:
        to_date = datetime.now()

    if limit == None:
        limit = 10

    return SQL.session.query(EventModel).join(EventModel.node).\
            filter(NodeModel.name == node).\
            filter(EventModel.date > from_date, EventModel.date < to_date).\
            order_by(EventModel.date.desc()).limit(limit).all()
