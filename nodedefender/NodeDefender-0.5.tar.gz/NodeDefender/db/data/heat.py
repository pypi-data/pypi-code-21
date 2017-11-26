from datetime import datetime, timedelta
from NodeDefender.db.sql import SQL, HeatModel, GroupModel, iCPEModel
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
        latest_heat =  SQL.session.query(HeatModel,\
                    label('sum', func.sum(HeatModel.average)),
                    label('count', func.count(HeatModel.average))).\
                    join(HeatModel.icpe).\
                    filter(iCPEModel.mac_address.in_(*[icpes])).\
                    filter(HeatModel.date > min_ago).first()
        if latest_heat.count:
            group_data['heat'] = latest_heat.sum / latest_heat.count
        else:
            group_data['heat'] = 0.0

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
        
        current_heat = SQL.session.query(HeatModel,\
                    label('sum', func.sum(HeatModel.average)),
                    label('count', func.count(HeatModel.average))).\
                    join(HeatModel.icpe).\
                    filter(iCPEModel.mac_address.in_(*[icpes])).\
                    filter(HeatModel.date > min_ago).first()
        
        daily_heat = SQL.session.query(HeatModel,\
                    label('sum', func.sum(HeatModel.average)),
                    label('count', func.count(HeatModel.average))).\
                    join(HeatModel.icpe).\
                    filter(iCPEModel.mac_address.in_(*[icpes])).\
                    filter(HeatModel.date > day_ago).first()
        
        weekly_heat = SQL.session.query(HeatModel,\
                    label('sum', func.sum(HeatModel.average)),
                    label('count', func.count(HeatModel.average))).\
                    join(HeatModel.icpe).\
                    filter(iCPEModel.mac_address.in_(*[icpes])).\
                    filter(HeatModel.date > week_ago).first()

        monthly_heat = SQL.session.query(HeatModel,\
                    label('sum', func.sum(HeatModel.average)),
                    label('count', func.count(HeatModel.average))).\
                    join(HeatModel.icpe).\
                    filter(iCPEModel.mac_address.in_(*[icpes])).\
                    filter(HeatModel.date > month_ago).first()
        
        if current_heat.count:
            current_heat = (current_heat.sum / current_heat.count)
        else:
            current_heat = 0.0

        if daily_heat.count:
            daily_heat = (daily_heat.sum / daily_heat.count)
        else:
            daily_heat = 0.0

        if weekly_heat.count:
            weekly_heat = (weekly_heat.sum / weekly_heat.count)
        else:
            weekly_heat = 0.0

        if monthly_heat.count:
            monthly_heat = (monthly_heat.sum / monthly_heat.count)
        else:
            monthly_heat = 0.0

        group_data['daily'] = daily_heat
        group_data['weekly'] = weekly_heat
        group_data['monthly'] = monthly_heat
        ret_data.append(group_data)

    return ret_data

def chart(*groups):    
    from_date = (datetime.now() - timedelta(days=30))
    to_date = datetime.now()
    
    groups = GroupModel.query.filter(GroupModel.name.in_(*[groups])).all()
    if not len(groups):
        return False

    ret_data = []
    
    for group in groups:
        icpes = [node.icpe.mac_address for node in group.nodes if node.icpe]
        
        heat_data = SQL.session.query(HeatModel).\
                join(HeatModel.icpe).\
                filter(iCPEModel.mac_address.in_(*[icpes])).\
                filter(HeatModel.date > from_date).\
                filter(HeatModel.date < to_date).all()

        if not heat_data:
            continue
        
        group_data = {}
        group_data['name'] = group.name
        group_data['heat'] = []
        grouped_data = [list(v) for k, v in groupby(heat_data, lambda p:
                                                    p.date)]

        for data in grouped_data:
            entry = {'date' : str(data[0].date)}
            for heat in data:
                try:
                    entry['value'] = (heat.average + entry['heat']) / 2
                except KeyError:
                    entry['value'] = heat.average
            group_data['heat'].append(entry)

        ret_data.append(group_data)
    
    return ret_data
