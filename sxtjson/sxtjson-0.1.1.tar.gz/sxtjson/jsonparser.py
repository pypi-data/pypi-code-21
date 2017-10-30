def tojson(obj,fields=None,isJson=False):
    from  django.core.serializers import  serialize
    try:
        json =  serialize('json',obj,fields=fields)
    except TypeError:
        json =  serialize('json',[obj,],fields=fields)
    d = eval(json.strip('[]'))['fields']
    if isJson:
        return  str(d)
    else:
        return d