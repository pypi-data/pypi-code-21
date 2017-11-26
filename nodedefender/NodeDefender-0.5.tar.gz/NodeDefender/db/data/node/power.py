from datetime import datetime, timedelta
from NodeDefender.db.sql import SQL, PowerModel, NodeModel, iCPEModel, GroupModel, SensorModel
from sqlalchemy import func
from sqlalchemy.sql import label
from itertools import groupby

def current(node):
    node = SQL.session.query(NodeModel).filter(NodeModel.name ==
                                                node).first()
    if node is None or not node.icpe or not node.icpe.sensors:
        return False
    

    node_data = {}
    node_data['name'] = node.name
    node_data['power'] = 0.0
    node_data['sensors'] = []
    for sensor in node.icpe.sensors:
        if not sensor.power:
            continue
        sensor_data = {}
        if sensor.name:
            sensor_name = sensor.name
        else:
            sensor_name = sensor.sensor_id + ', ' + sensor.product_name
        sensor_data['name'] = sensor_name
        sensor_data['sensor_id'] = sensor.sensor_id
        sensor_data['icpe'] = sensor.icpe.mac_address
        
        min_ago = (datetime.now() - timedelta(hours=1))
        latest_power =  SQL.session.query(PowerModel,\
                    label('sum', func.sum(PowerModel.average)),
                    label('count', func.count(PowerModel.average))).\
                    join(PowerModel.icpe).\
                    join(PowerModel.sensor).\
                    filter(iCPEModel.mac_address == node.icpe.mac_address).\
                    filter(SensorModel.sensor_id == sensor.sensor_id).\
                    filter(PowerModel.date > min_ago).first()
        
        if latest_power.count:
            sensor_data['power'] = latest_power.sum / latest_power.count
            node_data['power'] += sensor_data['power']
        else:
            sensor_data['power'] = 0.0

        node_data['sensors'].append(sensor_data)

    return node_data

def average(node):
    node = SQL.session.query(NodeModel).filter(NodeModel.name ==
                                               node).first()
    if node is None or not node.icpe or not node.icpe.sensors:
        return False

    min_ago = (datetime.now() - timedelta(hours=0.5))
    day_ago = (datetime.now() - timedelta(days=1))
    week_ago = (datetime.now() - timedelta(days=7))
    month_ago = (datetime.now() - timedelta(days=30))
    ret_data = []
    node_data = {}
    node_data['name'] = node.name
    node_data['current'] = 0.0
    node_data['daily'] = 0.0
    node_data['weekly'] = 0.0
    node_data['monthly'] = 0.0 

    current_power = SQL.session.query(PowerModel,\
                label('sum', func.sum(PowerModel.average)),
                label('count', func.count(PowerModel.average))).\
                join(PowerModel.icpe).\
                filter(iCPEModel.mac_address == node.icpe.mac_address).\
                filter(PowerModel.date > min_ago).first()
    
    daily_power = SQL.session.query(PowerModel,\
                label('sum', func.sum(PowerModel.average)),
                label('count', func.count(PowerModel.average))).\
                join(PowerModel.icpe).\
                filter(iCPEModel.mac_address == node.icpe.mac_address).\
                filter(PowerModel.date > day_ago).first()
    
    weekly_power = SQL.session.query(PowerModel,\
                label('sum', func.sum(PowerModel.average)),
                label('count', func.count(PowerModel.average))).\
                join(PowerModel.icpe).\
                filter(iCPEModel.mac_address == node.icpe.mac_address).\
                filter(PowerModel.date > week_ago).first()

    monthly_power = SQL.session.query(PowerModel,\
                label('sum', func.sum(PowerModel.average)),
                label('count', func.count(PowerModel.average))).\
                join(PowerModel.icpe).\
                filter(iCPEModel.mac_address == node.icpe.mac_address).\
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

    node_data['current'] = current_power

    node_data['daily'] = daily_power

    node_data['weekly'] = weekly_power

    node_data['monthly'] = monthly_power

    return node_data

def chart(node):    
    from_date = (datetime.now() - timedelta(days=30))
    to_date = datetime.now()
    
    node = SQL.session.query(NodeModel).filter(NodeModel.name ==
                                                node).first()
    if node is None or not node.icpe or not node.icpe.sensors:
        return False

    ret_data = []
    
    for sensor in node.icpe.sensors:
        if not sensor.power:
            continue
        
        power_data = SQL.session.query(PowerModel).\
                join(PowerModel.icpe).\
                join(PowerModel.sensor).\
                filter(iCPEModel.mac_address == node.icpe.mac_address).\
                filter(SensorModel.sensor_id == sensor.sensor_id).\
                filter(PowerModel.date > from_date).\
                filter(PowerModel.date < to_date).all()

        if not power_data:
            continue
        
        sensor_data = {}
        if sensor.name:
            sensor_name = sensor.name
        else:
            sensor_name = sensor.sensor_id + ', ' + sensor.product_name
        sensor_data['name'] = sensor_name
        sensor_data['sensor_id'] = sensor.sensor_id
        sensor_data['icpe'] = sensor.icpe.mac_address

        sensor_data['power'] = []
        grouped_data = [list(v) for k, v in groupby(power_data, lambda p:
                                                    p.date)]

        for data in grouped_data:
            entry = {'date' : str(data[0].date)}
            for power in data:
                try:
                    entry['value'] = (power.average + entry['power']) / 2
                except KeyError:
                    entry['value'] = power.average
            sensor_data['power'].append(entry)

        ret_data.append(sensor_data)
    
    return ret_data
