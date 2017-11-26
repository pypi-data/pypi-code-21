from NodeDefender.db.sql import SQL, EventModel, GroupModel, NodeModel, iCPEModel
from datetime import datetime, timedelta
from sqlalchemy import or_

def average(group, time_ago = None):
    if time_ago is None:
        time_ago = (datetime.now() - timedelta(days=1))

    group = SQL.session.query(GroupModel).filter(GroupModel.name == group).first()
    if group is None:
        return False

    icpes = [node.icpe.mac_address for node in group.nodes if node.icpe]

    total_events = SQL.session.query(EventModel).\
            join(EventModel.icpe).\
            filter(iCPEModel.mac_address.in_(*[icpes])).\
            filter(EventModel.date > time_ago).all()

    ret_data = {}
    ret_data['name'] = group.name
    ret_data['total'] = len(total_events)
    ret_data['critical'] = len([event for event in total_events if
                                event.critical])
    ret_data['normal'] = len([event for event in total_events if
                              event.normal])
    return ret_data


def latest(group):
    return EventModel.query.join(NodeModel).\
            filter(NodeModel.groups.any(GroupModel.name == group)).first()

def list(groups, limit = 20):
    if type(groups) is str:
        groups = [groups]

    nodes = SQL.session.query(NodeModel).join(NodeModel.groups).\
            filter(GroupModel.name.in_(groups)).all()
    return EventModel.query.join(NodeModel).\
            filter(NodeModel.name.in_([node.name for node in nodes])).\
            order_by(EventModel.date.desc()).limit(int(limit)).all()

