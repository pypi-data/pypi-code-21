import json


def to_json(obj):
    return json.dumps(obj, default=lambda o: o.__dict__, sort_keys=True)


def _byteify(input):
    if isinstance(input, dict):
        return {_byteify(key): _byteify(value)
                for key, value in input.items()}
    elif isinstance(input, list):
        return [_byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input