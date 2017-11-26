from NodeDefender.db.sql import SQL, EventModel, GroupModel, NodeModel
from sqlalchemy import or_

def average(*groups, time_ago = None):
    if time_ago is None:
        time_ago = (datetime.now() - timedelta(days=1))

    groups = SQL.session.query(GroupModel).\
            filter(GroupModel.name.in_(*[groups])).first()

    ret_data = []
    for group in groups:
        group_data = {}

        icpes = [node.icpe.mac_address for node in group.nodes if node.icpe]

        total_events = SQL.session.query(EventModel).\
                join(EventModel.icpe).\
                filter(iCPEModel.mac_address.in_(*[icpes])).\
                filter(EventModel.date > time_ago).all()

        group_data['group'] = group.name
        group_data['total'] = len(total_events)
        group_data['critical'] = len([event for event in total_events if
                                event.critical])
        group_data['normal'] = len([event for event in total_events if
                              event.normal])
        ret_data.append(group_data)

    return group_data

def latest(group):
    return EventModel.query.join(NodeModel).\
            filter(NodeModel.groups.any(GroupModel.name == group)).first()

def get(group, limit = 20):
    group = GroupModel.query.filter(GroupModel.name == group).first()
    if not group:
        return False
    return EventModel.query.join(NodeModel).\
            filter(NodeModel.name.in_([node.name for node in group.nodes])).\
            order_by(EventModel.date.desc()).limit(int(limit)).all()

