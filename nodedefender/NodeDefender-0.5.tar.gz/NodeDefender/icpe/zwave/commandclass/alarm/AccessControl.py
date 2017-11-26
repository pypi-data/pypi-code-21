import NodeDefender

icons = {'16' : 'fa fa-bell', '17' : 'fa fa-bell-slash-o',\
         '1' : 'fa fa-bell', '0' : 'fa fa-bell-slash-o'}

fields = {'type' : "bool", 'readonly' : True, 'name' : 'Door/Window', 'web_field'
          : True}

info = {'number' : '06', 'name' : 'AccessControl', 'commandclass' : 'alarm'}

def event(payload):
    data = {'commandclass' : NodeDefender.icpe.zwave.commandclass.alarm.info,
            'commandclasstype' : info, 'fields' : fields}
    data['value'] = payload['evt']
    data['state'] = True if data['value'] == '16' else False
    data['icon'] = icons[data['value']]
    return data

def icon(value):
    return icons[value]
