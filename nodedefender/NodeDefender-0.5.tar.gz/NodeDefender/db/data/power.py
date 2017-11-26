from datetime import datetime, timedelta
from NodeDefender.db.sql import SQL, PowerModel, GroupModel, iCPEModel
from sqlalchemy import func
from sqlalchemy.sql import label
from itertools import groupby

def current(*groups):
    groups = GroupModel.query.filter(GroupModel.name.in_(*[groups])).all()
    if not len(groups):
        return False
    
    ret_data = []
    for group in groups:
        group_data = {}
        group_data['name'] = group.name
        icpes = [node.icpe.mac_address for node in group.nodes if node.icpe]
        min_ago = (datetime.now() - timedelta(hours=0.5))
        latest_power =  SQL.session.query(PowerModel,\
                    label('sum', func.sum(PowerModel.average)),
                    label('count', func.count(PowerModel.average))).\
                    join(PowerModel.icpe).\
                    filter(iCPEModel.mac_address.in_(*[icpes])).\
                    filter(PowerModel.date > min_ago).first()
        if latest_power.count:
            group_data['power'] = latest_power.sum / latest_power.count
        else:
            group_data['power'] = 0.0

        ret_data.append(group_data)

    return ret_data

def average(*groups):
    groups = GroupModel.query.filter(GroupModel.name.in_(*[groups])).all()
    if not len(groups):
        return False

    min_ago = (datetime.now() - timedelta(hours=0.5))
    day_ago = (datetime.now() - timedelta(days=1))
    week_ago = (datetime.now() - timedelta(days=7))
    month_ago = (datetime.now() - timedelta(days=30))
    ret_data = []
    for group in groups:
        group_data = {}
        group_data['name'] = group.name
        icpes = [node.icpe.mac_address for node in group.nodes if node.icpe]
        
        current_power = SQL.session.query(PowerModel,\
                    label('sum', func.sum(PowerModel.average)),
                    label('count', func.count(PowerModel.average))).\
                    join(PowerModel.icpe).\
                    filter(iCPEModel.mac_address.in_(*[icpes])).\
                    filter(PowerModel.date > min_ago).first()
        
        daily_power = SQL.session.query(PowerModel,\
                    label('sum', func.sum(PowerModel.average)),
                    label('count', func.count(PowerModel.average))).\
                    join(PowerModel.icpe).\
                    filter(iCPEModel.mac_address.in_(*[icpes])).\
                    filter(PowerModel.date > day_ago).first()
        
        weekly_power = SQL.session.query(PowerModel,\
                    label('sum', func.sum(PowerModel.average)),
                    label('count', func.count(PowerModel.average))).\
                    join(PowerModel.icpe).\
                    filter(iCPEModel.mac_address.in_(*[icpes])).\
                    filter(PowerModel.date > week_ago).first()

        monthly_power = SQL.session.query(PowerModel,\
                    label('sum', func.sum(PowerModel.average)),
                    label('count', func.count(PowerModel.average))).\
                    join(PowerModel.icpe).\
                    filter(iCPEModel.mac_address.in_(*[icpes])).\
                    filter(PowerModel.date > month_ago).first()
        
        if current_power.count:
            current_power = (current_power.sum / current_power.count)
        else:
            current_power = 0.0

        if daily_power.count:
            daily_power = (daily_power.sum / daily_power.count)
        else:
            daily_power = 0.0

        if weekly_power.count:
            weekly_power = (weekly_power.sum / weekly_power.count)
        else:
            weekly_power = 0.0

        if monthly_power.count:
            monthly_power = (monthly_power.sum / monthly_power.count)
        else:
            monthly_power = 0.0

        group_data['daily'] = daily_power
        group_data['weekly'] = weekly_power
        group_data['monthly'] = monthly_power
        ret_data.append(group_data)

    return ret_data

def chart(*groups):    
    from_date = (datetime.now() - timedelta(days=30))
    to_date = datetime.now()
    groups = SQL.session.query(GroupModel).filter(GroupModel.name.in_(groups)).all()
    if not len(groups):
        return False

    ret_data = []
    
    for group in groups:
        icpes = [node.icpe.mac_address for node in group.nodes if node.icpe]
        
        power_data = SQL.session.query(PowerModel).\
                join(PowerModel.icpe).\
                filter(iCPEModel.mac_address.in_(*[icpes])).\
                filter(PowerModel.date > from_date).\
                filter(PowerModel.date < to_date).all()

        if not power_data:
            continue
        
        group_data = {}
        group_data['name'] = group.name
        group_data['power'] = []
        grouped_data = [list(v) for k, v in groupby(power_data, lambda p:
                                                    p.date)]

        for data in grouped_data:
            entry = {'date' : str(data[0].date)}
            for power in data:
                try:
                    entry['value'] = (power.average + entry['power']) / 2
                except KeyError:
                    entry['value'] = power.average
            group_data['power'].append(entry)

        ret_data.append(group_data)
    
    return ret_data
