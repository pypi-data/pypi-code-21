import NodeDefender.icpe.zwave.commandclass.alarm
import NodeDefender.icpe.zwave.commandclass.basic
import NodeDefender.icpe.zwave.commandclass.bswitch
import NodeDefender.icpe.zwave.commandclass.meter
import NodeDefender.icpe.zwave.commandclass.msensor

classnumbers = {'71': 'alarm', '20' : 'basic', '25' : 'bswitch',
                '31' : 'msensor', '32' : 'meter'}

def to_name(classnumber):
    try:
        return classnumbers[classnumber]
    except KeyError:
        return False

def to_number(classname):
    try:
        return eval(classname + '.number')()
    except NameError:
        return False

def web_field(classnumber = None, classname = None, classtype = None):
    if classnumber and not classname:
        classname = to_name(classnumber)
        if not classname:
            return None
    
    if not classtype:
        try:
            return eval(classname + '.fields')['web_field']
        except (NameError, TypeError):
            return None

    try:
        typename = eval(classname + '.classtypes')[classtype]
    except (KeyError, TypeError):
        return None

    try:
        return eval(classname + '.' + typename + '.fields')['web_field']
    except NameError:
        return None

def info(classnumber = None, classname = None, classtype = None):
    if classnumber and not classname:
        classname = to_name(classnumber)
        if not classname:
            return None
    
    if not classtype:
        try:
            return eval(classname + '.info')
        except NameError:
            return None

    try:
        typename = eval(classname + '.classtypes')[classtype]
    except KeyError:
        return None

    try:
        return eval(classname + '.' + typename + '.info')
    except NameError:
        return None
