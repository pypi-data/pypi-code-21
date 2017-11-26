import NodeDefender

fields = {'type' : 'value', 'readonly' : True, 'name' : 'Watt',
          'web_field' : True}

info = {'name' : 'Electric', 'number' : '1', 'commandclass' : 'meter'}

def icon(value):
    return 'fa fa-plug'

def event(payload):
    data = {'commandclass' : NodeDefender.icpe.zwave.commandclass.meter.info,
            'commandclasstype' : info, 'fields' : fields}
    data['value'] = int(payload['data'], 0)
    data['state'] = True if data['value'] > 1.0 else False
    data['icon'] = 'fa fa-plug'
    return data
