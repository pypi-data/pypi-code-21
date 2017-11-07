def setattr_from_dict(obj, dictObj, *args):
    for key in args:
        if key in dictObj:
            setattr(obj, key, dictObj[key])
