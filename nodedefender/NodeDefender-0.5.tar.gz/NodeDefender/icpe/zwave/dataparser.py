import json

data = {}

with open('zwave_products.json') as fr:
    data = json.load(fr)

for device in data:
    try:
        data[device['ManufacturerId']] = {[device['ProductId']] : device}
    except TypeError:
        pass
    except KeyError:
        try:
            data[device['ManufacturerId']] = device
        except KeyError:
            pass
