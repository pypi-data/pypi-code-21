from NodeDefender.icpe.zwave.commandclass.meter import Electric

classtypes = {'1' : 'Electric'}
info = {'number' : '32', 'name' : 'meter', 'types' : True}
fields = None

def icon(value):
    return None

def event(payload):
    try:
        return eval(classtypes[payload['type']] + '.event')(payload)
    except KeyError as e:
        return False
