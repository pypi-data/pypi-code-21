import json

def json_parse(path):
    with open(path) as json_file:
        data = json.load(json_file)

    return data
