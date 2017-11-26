import NodeDefender

fields =  {'type' : 'value', 'readonly' : True, 'name' : 'Celsius', 'web_field'
           : True}
info = {'number' : '1', 'name' : 'AirTemperature', 'commandclass' : 'msensor'}

def event(payload):
    data = {'commandclass' : NodeDefender.icpe.zwave.commandclass.msensor.info,
            'commandclasstype' : info, 'fields' : fields}
    if payload['unit'] == '1':              # Fahrenheit
        return None
    data['value'] = int(payload['data'], 0) / 10
    data['state'] = True if data['value'] else False
    data['icon'] = 'fa fa-thermometer-half'
    return data

def icon(value):
    return 'fa fa-thermometer-half'
