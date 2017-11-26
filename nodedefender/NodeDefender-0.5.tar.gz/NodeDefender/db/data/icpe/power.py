from datetime import datetime, timedelta
from NodeDefender.db.sql import SQL, PowerModel, iCPEModel
from sqlalchemy import func
from sqlalchemy.sql import label

def latest(icpe):
    power_data = SQL.session.query(PowerModel, \
                                  label('low', func.min(PowerModel.low)),
                                  label('high', func.max(PowerModel.high)),
                                  label('total', func.sum(PowerModel.average)),
                                  label('date', PowerModel.date)).\
            join(iCPEModel).\
            filter(iCPEModel.mac_address == icpe).\
            order_by(PowerModel.date.desc()).\
            group_by(PowerModel.date).first()

    if not power_data:
        return False
    
    return {'icpe' : icpe, 'date' : str(power_data.date), 'low' : power_data.low,\
            'high' : power_data.high, 'total' : power_data.total}

def Get(icpe, from_date = (datetime.now() - timedelta(days=7)), to_date =
        datetime.now()):
    power_data = SQL.session.query(PowerModel, \
                                  label('low', func.min(PowerModel.low)),
                                  label('high', func.max(PowerModel.high)),
                                  label('total', func.sum(PowerModel.average)),
                                  label('date', PowerModel.date)).\
            join(iCPEModel).\
            filter(iCPEModel.mac_address == icpe).\
            filter(PowerModel.date > from_date).\
            filter(PowerModel.date < to_date).\
            group_by(PowerModel.date).all()

    if not power_data:
        return False

    ret_json = {'icpe' : icpe}
    ret_json['power'] = []
    for data in power_data:
        ret_json['power'].append({'date' : str(data.date), 'low' : data.low, 'high' : data.high,
                                    'total' : data.total})
    return ret_json
