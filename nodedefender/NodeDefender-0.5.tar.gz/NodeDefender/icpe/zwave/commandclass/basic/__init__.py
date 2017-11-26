icons = {True : 'fa fa-toggle-on', False : 'fa fa-toggle-off'}

info = {'name' : 'basic', 'number' : '20', 'types' : False}

fields = {'type' : "bool", 'readonly' : True, 'name' : 'Basic', 'web_field' :
          False}

def icon(value):
    return icons[eval(value)]

def event(payload):
    data = {'commandclass' : info, 'commandclasstype' : None,
            'fields' : fields}
    data['value'] = int(payload['value'], 16)
    data['state'] = True if payload['value'] else False
    data['icon'] = icons[data['state']]
    return data
