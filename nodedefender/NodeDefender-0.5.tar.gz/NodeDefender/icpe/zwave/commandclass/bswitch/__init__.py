icons = {True : 'fa fa-toggle-on', False : 'fa fa-toggle-off'}

info = {'number' : '25', 'name' : 'bswitch', 'types' : False}

fields = {'type' : "bool", 'readonly' : False, 'name' : 'Switch',
          "web_field" : True}
 
def icon(value):
    return icons[bool(eval(value))]

def event(payload):
    data = {'commandclass' : info, 'commandclasstype' : False,
            'fields' : fields}
    data['value'] = payload['value']
    data['state'] = True if int(data['value']) else False
    data['icon'] = icons[data['state']]
    return data
