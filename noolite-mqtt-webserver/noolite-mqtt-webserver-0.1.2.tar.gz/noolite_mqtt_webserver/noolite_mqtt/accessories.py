import json

import asyncio
import motor.motor_asyncio

COMMON_CHARACTERISTICS = {
    'Name': {'value': None},
    'Manufacturer': {'value': 'NooLite'},
    'Model': {'value': 'NooLite'},
    'SerialNumber': {'value': '0.0.1'},
}


ACCESSORY_MAP = {
    'MotionSensor': {
        'MotionDetected': {'value': False},
        'StatusLowBattery': {'value': False},
    },
    'TemperatureSensor': {
        'CurrentTemperature': {'maxValue': 100, 'minValue': -50, 'minStep': 0.1, 'value': 0},
        'StatusLowBattery': {'value': False},
    },
    'HumiditySensor': {
        'CurrentRelativeHumidity': {'maxValue': 100, 'minValue': 0, 'minStep': 1, 'value': 0},
        'StatusLowBattery': {'value': False},
    },
    'Switch': {
        "On": {'value': False},
    },
    'Lightbulb': {
        "On": {'value': False},
        "Hue": {"minValue": 0, "maxValue": 360, "minStep": 1, 'value': 0},
        "Saturation": {"minValue": 0, "maxValue": 100, "minStep": 1, 'value': 0},
        "Brightness": {"minValue": 0, "maxValue": 100, "minStep": 1, 'value': 0}
    },
    'Lightbulb_b': {
        "On": {'value': False},
        "Brightness": {"minValue": 0, "maxValue": 100, "minStep": 1, 'value': 0}
    }
}


class Accessory:
    def __init__(self, name, service, noolite):
        self.name = name
        self.service = service
        self.noolite = noolite
        self.characteristics = []


class AcessoryManager:
    def __init__(self, loop=None, db_ip=None, db_port=None):
        self.loop = loop or asyncio.get_event_loop()
        self.db_client = motor.motor_asyncio.AsyncIOMotorClient(db_ip, db_port)
        self.db = self.db_client['noolite']

        self.accessories = {}

    # CREATE
    async def accessory_create(self, accessory_data):
        result = await self.db.accessories.insert_one(dict(accessory_data))
        print('result %s' % repr(result.inserted_id))

    # DELETE
    async def accessory_delete(self, name):
        result = await self.db.accessories.delete_many({'name': name})
        print('Delete result %s' % repr(result.raw_result))

    # GET
    async def accessory_get(self, query):
        accessory = await self.db.accessories.find_one(query)
        if not accessory:
            print('Accessory "{}" not exist'.format(query))
        return accessory

    # SEARCH
    async def accessory_search(self, query=None):
        cursor = self.db.accessories.find(query or {})
        accessories = await cursor.to_list(length=None)
        return accessories

    async def characteristic(self, accessory_name, characteristic_name, value=None):
        accessory_data = await self.accessory_get({'name': accessory_name})
        if accessory_data:
            characteristic = accessory_data['characteristics'].get(characteristic_name) or {'value': 0}

            # SET
            if value is not None:
                # Сохраняем новое значение в базе
                characteristic['value'] = value
                await self.db.accessories.replace_one({'_id': accessory_data['_id']}, accessory_data)

            # GET
            else:
                return characteristic.get('value', 0)
