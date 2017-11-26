from NodeDefender.icpe.zwave import commandclass, devices

def event(mac, sensoid, classname, **payload):
    try:
        return eval('commandclass' + '.' + classname + '.event')\
                (payload)
    except NameError:
        return None
