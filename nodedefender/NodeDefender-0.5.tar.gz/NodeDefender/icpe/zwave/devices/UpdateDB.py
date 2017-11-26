#!/usr/bin/env python3
import json

required = ['Brand', 'Name', 'ManufacturerId', 'ProductId']
expected = ['Brand', 'Name', 'ManufacturerId', 'ProductId', 'ProductTypeId',
            'LibraryType', 'DeviceType']

def CheckExpected(ZWaveDict):
    for x in required:
        if x in ZWaveDict:
            pass
        else:
            return False
    return True
    
def FormatDict(ZWaveDict):
    FDict = {}
    for item in ZWaveDict:
        SensorDict = {}
        for val in expected:
            try:
                SensorDict[val] = item[val]
            except KeyError:
                SensorDict[val] = 'None'
        try:
            FDict[item['ManufacturerId'].lower()][item['ProductId'].lower()] = SensorDict
        except KeyError:
            FDict[item['ManufacturerId'].lower()] = {}
            FDict[item['ManufacturerId'].lower()][item['ProductId'].lower()] = SensorDict
    return FDict

def main():
    with open('zwave_products.json') as fr:
        zdb = json.load(fr)
        x = [d for d in zdb if CheckExpected(d)]
        f = FormatDict(x)
    with open('ZWaveDB.json', 'x+') as fw:
        json.dump(f, fw)
    return True

if __name__ == '__main__':
    main()
