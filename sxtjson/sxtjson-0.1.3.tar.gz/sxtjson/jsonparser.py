def tojson(obj,fields=None,isJson=False):
    from  django.core.serializers import  serialize
    try:
        json =  serialize('json',obj,fields=fields)
        d = []
        for jsonobject in eval(json):
            d.append(jsonobject['fields'])
    except TypeError:
        json =  serialize('json',[obj,],fields=fields)
        d = eval(json[1:-1])['fields']
    if isJson:
        return  str(d)
    else:
        return d