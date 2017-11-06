import re

def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def set_or_add(obj, name, value):
    if hasattr(obj, name):
        if isinstance(obj[name], list):
            obj[name].append(value)
        else:
            obj[name] = [obj[name], value]
    obj[name] = value

def xml_to_dict(element):
    obj = {}
    for child in element:
        name = convert(child.tag.split('}', 1)[1])
        if len(child) == 0:
            set_or_add(obj, name, child.text)
        else:
            set_or_add(obj, name, xml_to_dict(child))
    return obj
