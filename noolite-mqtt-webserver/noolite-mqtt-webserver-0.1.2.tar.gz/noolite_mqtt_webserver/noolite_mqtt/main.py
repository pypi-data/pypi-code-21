import json
import math
import logging
import asyncio
import colorsys

from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_0, QOS_1, QOS_2

from .noolite_commands import NooLiteResponse
from ..utils import Singleton

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Список всех созданных аксессуаров. Должен быть всегда в актуальном состоянии
ACCESSORIES = {}


NOOLITE_SERVICE_NAME = 'noolite'
HOMEBRIDGE_SUBSCRIBTIONS = [
    ('homebridge/from/get', QOS_0),
    ('homebridge/from/set', QOS_0),
    ('homebridge/from/response', QOS_0),
    ('homebridge/from/identify', QOS_0)
]


STATES = {
    1: True,
    2: True,
    0: False
}


ACCESSORY_MAP = {
    'MotionSensor': {
        'service_name': 'MotionSensor',
        'service_type': 'MotionSensor',
        'characteristics': {
            'MotionDetected': "default",
            'StatusLowBattery': "default",
        }
    },
    'TemperatureSensor': {
        'service_name': 'TemperatureSensor',
        'service_type': 'TemperatureSensor',
        'characteristics': {
            'CurrentTemperature': {'maxValue': 100, 'minValue': -50, 'minStep': 0.1, 'value': 0},
            'StatusLowBattery': "default",
        },
    },
    'HumiditySensor': {
        'service_name': 'HumiditySensor',
        'service_type': 'HumiditySensor',
        'characteristics': {
            'CurrentRelativeHumidity': {'maxValue': 100, 'minValue': 0, 'minStep': 1, 'value': 0},
            'StatusLowBattery': "default",
        },
    },
    'Switch': {
        'service_name': 'Switch',
        'service_type': 'Switch',
        'characteristics': {
            "On": "default",
        },
    },
    'Lightbulb': {
        'service_name': 'Lightbulb',
        'service_type': 'Lightbulb',
        'characteristics': {
            "On": "default",
            "Hue": {"minValue": 0, "maxValue": 360, "minStep": 1, 'value': 0},
            "Saturation": {"minValue": 0, "maxValue": 100, "minStep": 1, 'value': 0},
            "Brightness": {"minValue": 0, "maxValue": 100, "minStep": 1, 'value': 0}
        },
    },
    'Lightbulb_b': {
        'service_name': 'Lightbulb_b',
        'service_type': 'Lightbulb',
        'characteristics': {
            "On": "default",
            "Brightness": {"minValue": 0, "maxValue": 100, "minStep": 1, 'value': 0}
        },
    }
}


class NooLiteMqtt(metaclass=Singleton):
    def __init__(self, loop, mqtt_read_topic, mqtt_write_topic, mqtt_host='mqtt://127.0.0.1/'):
        self.mqtt_client = MQTTClient(config={'auto_reconnect': True})
        self.mqtt_host = mqtt_host
        self.write_topic = mqtt_write_topic
        self.loop = loop
        HOMEBRIDGE_SUBSCRIBTIONS.append((mqtt_read_topic, QOS_0))

        self.handlers = {
            'homebridge/from/get': self._get_handler,
            'homebridge/from/set': self._set_handler,
            mqtt_read_topic: self._mtrf_command_handler,
        }

    async def run(self):
        await self.mqtt_client.connect(self.mqtt_host)
        await self.mqtt_client.subscribe(HOMEBRIDGE_SUBSCRIBTIONS)

        logger.info('First boot run')
        first_run = True

        while True:
            if first_run:
                # Запрашиваем все аксессуары
                await self.mqtt_client.publish('homebridge/to/get', '{"name": "*"}'.encode())

                try:
                    logger.info('Wait all accessories data from homebridge')
                    message = await self.mqtt_client.deliver_message(timeout=10)
                    first_run = False
                except asyncio.TimeoutError as e:
                    logger.exception(e)
                    logger.info('Homebridge did not answer')
                    continue

            else:
                logger.info('Waiting messages from mqtt...')
                message = await self.mqtt_client.deliver_message()

            topic = message.topic
            payload = message.publish_packet.payload.data
            try:
                payload = json.loads(payload.decode())
            except Exception as e:
                logger.exception('Cannot decode payload: {}'.format(e))
                continue

            logger.info('{}\n{}'.format(topic, json.dumps(payload, indent=4, ensure_ascii=False)))

            if all([item not in payload.keys() for item in ['ack', 'name', 'command']]):
                ACCESSORIES.update(payload)

            if topic in self.handlers.keys():
                try:
                    await self.handlers[topic](payload)
                except Exception as e:
                    logger.exception(e)

    async def accessory_search(self, name=None):
        if name:
            return await self.accessory_get(name=name)
        else:
            return ACCESSORIES

    # CREATE
    async def accessory_create(self, name, service_type, noolite_ch, noolite_id=None):
        if service_type not in ACCESSORY_MAP:
            raise Exception('Unknown service type: "{}". Select one of: {}'.format(service_type, ACCESSORY_MAP.keys()))

        # Формируем payload для homebridge
        accessory_profile = ACCESSORY_MAP[service_type]
        payload = {
            'name': name,
            'service': accessory_profile['service_type'],
            'service_name': name,
        }

        payload.update(accessory_profile['characteristics'])

        # Отправляем сообщение
        await self.mqtt_client.publish(topic='homebridge/to/add', message=json.dumps(payload).encode())

        # Добавляем сервис NooLite
        noolite_payload = {
            'name': name,
            'service_name': NOOLITE_SERVICE_NAME,
            'service': 'NooLiteDevice',
        }
        if noolite_id:
            # Если у блока есть id, то это новый протокол, добавляем характеристику
            noolite_payload['NooLiteId'] = 'default'

        await self.mqtt_client.publish(topic='homebridge/to/add/service', message=json.dumps(noolite_payload).encode())

        # Проставляем значения характеристик
        await self.characteristic_set(accessory_name=name, service_name=NOOLITE_SERVICE_NAME,
                                      characteristic='NooLiteChannel', value=noolite_ch)
        if noolite_id:
            await self.characteristic_set(accessory_name=name, service_name=NOOLITE_SERVICE_NAME,
                                          characteristic='NooLiteId', value=noolite_id)

        # Обновляем данные о аксессуарах
        await self.mqtt_client.publish('homebridge/to/get', '{"name": "*"}'.encode())

    # DELETE
    async def accessory_delete(self, name):
        await self.mqtt_client.publish(topic='homebridge/to/remove', message=json.dumps({'name': name}).encode())
        ACCESSORIES.pop(name)

    async def characteristic_set(self, accessory_name, characteristic, value, service_name=None):
        if service_name:
            message = {'name': accessory_name, 'service_name': service_name, 'characteristic': characteristic,
                       'value': value}
        else:
            accessory = await self.accessory_get(name=accessory_name)
            if not accessory:
                return

            for service_name, characteristics in accessory['characteristics'].items():
                if characteristic in characteristics:
                    message = {'name': accessory_name, 'service_name': service_name, 'characteristic': characteristic,
                               'value': value}
                    break
            else:
                logger.info('Cannot find characteristic "{}" in {}'.format(characteristic, accessory))
                return

        topic = 'homebridge/to/set'
        logger.debug('Pub message to homebridge: topic: {}, message: {}'.format(topic, message))
        await self.mqtt_client.publish(topic=topic, message=json.dumps(message).encode())
        await self.update_local_characteristic_value(accessory_name, characteristic, value)

    async def update_local_characteristic_value(self, accessory_name, characteristic, value):
        accessory = await self.accessory_get(name=accessory_name)
        if not accessory:
            return

        for service_name, characteristics in accessory['characteristics'].items():
            if characteristic in characteristics:
                characteristics[characteristic] = value

        ACCESSORIES[accessory_name] = accessory

    def accessory_filter(self, channel):
        accessories = {}

        for acc_name, acc_data in ACCESSORIES.items():
            if NOOLITE_SERVICE_NAME in acc_data.get('characteristics', []) and \
                            acc_data['characteristics'][NOOLITE_SERVICE_NAME]['NooLiteChannel'] == channel:
                accessories[acc_name] = acc_data

        return accessories

    async def accessory_get(self, name=None, channel=None):
        accessory = None

        if name is not None:
            if name in ACCESSORIES:
                accessory = ACCESSORIES[name]

        elif channel is not None:
            for acc_name, acc_data in ACCESSORIES.items():
                if NOOLITE_SERVICE_NAME in acc_data.get('characteristics', []) and \
                                acc_data['characteristics'][NOOLITE_SERVICE_NAME]['NooLiteChannel'] == channel:
                    return {acc_name: acc_data}

        if not accessory:
            logger.info('Accessory "{}" not found'.format(name or channel))
            await self.mqtt_client.publish('homebridge/to/get', '{"name": "*"}'.encode())
            return

        elif NOOLITE_SERVICE_NAME not in accessory.get('characteristics', []):
            logger.info('Accessory "{}" not have {} service: {}'.format(name, NOOLITE_SERVICE_NAME, accessory))
            return

        return accessory

    async def _get_handler(self, payload):
        await self.update_accessory_characteristic_state(payload['name'], payload['characteristic'])

    async def update_accessory_characteristic_state(self, accessory_name, characteristic, attempts_n=2):

        logger.info('Updating characteristic "{}" on accessory "{}"'.format(characteristic, accessory_name))

        accessory = await self.accessory_get(accessory_name)
        if not accessory:
            logger.info('No accessory with name "{}"'.format(accessory_name))
            return

        if accessory['characteristics'][NOOLITE_SERVICE_NAME].get('NooLiteId'):
            # Новый протокол NooLite-F
            # Для устройств нового протокола - запрашиваем состояние через адапрет
            noolite_id = [int(i) for i in accessory['characteristics'][NOOLITE_SERVICE_NAME]['NooLiteId'].split(':')]
            noolite_cmd = {
                'ch': accessory['characteristics'][NOOLITE_SERVICE_NAME]['NooLiteChannel'],
                'mode': 2,
                'ctr': 1,
                'cmd': 128,
                'id0': noolite_id[0],
                'id1': noolite_id[1],
                'id2': noolite_id[2],
                'id3': noolite_id[3],
            }

            await self.send_command_to_mtrf(noolite_cmd)

        else:
            # Старый протокол
            pass

    async def _set_handler(self, payload, attempts_n=2):

        accessory = await self.accessory_get(payload['name'])
        if not accessory:
            return

        if payload['characteristic'] == 'Saturation':
            # TODO: Пока не обрабатываем Saturation, так как аксессуары не поддерживают это
            self.update_local_characteristic_value(
                accessory_name=payload['name'],
                characteristic=payload['characteristic'],
                value=payload['value']
            )

        # Формируем и отправляем команду к noolite
        noolite_cmd = self._characteristic_value_to_noolite_command(
            accessory_data=accessory,
            characteristic_name=payload['characteristic'],
            value=payload['value']
        )

        await self.send_command_to_mtrf(noolite_cmd)

    async def _mtrf_command_handler(self, payload):

        command = NooLiteResponse(*payload['command'])

        channel_accessories = self.accessory_filter(channel=command.ch)
        if not channel_accessories:
            return

        for accessory_name, accessory_data in channel_accessories.items():
            # Ответ от исполнительного устройства
            if command.cmd == 130:
                if command.fmt == 0:
                    # Если формат 0, то значение бит:
                    # d0 - Код типа устройства
                    # d1 - Версия микропрограммы
                    # d2 - Состояние устройства (0 - выключено, 1 - включено, 2 - временное включение)
                    # d3 - Текущая яркость (0-255)
                    await self.characteristic_set(accessory_name=accessory_name, characteristic='On',
                                                  value=STATES[command.d2])
                    await self.characteristic_set(accessory_name=accessory_name, characteristic='Brightness',
                                                  value=command.d3)

            # У устройства, которое передало данную команду, разрядился элемент питания
            elif command.cmd == 20:
                await self.characteristic_set(accessory_name=accessory_name, characteristic='StatusLowBattery', value=1)

            # 25 команду (включить свет на заданное время) может передавать как датчик движения, так и какие-то
            # другие устройства. Если в команде не задан ID, то это команда от датчика движения
            elif command.cmd == 25 and command.is_id():
                await self.characteristic_set(accessory_name=accessory_name, characteristic='On', value=True)

                # Выключаем через заданное время
                await asyncio.sleep(command.d0 * 5)
                await self.characteristic_set(accessory_name=accessory_name, characteristic='On', value=False)

            # Данные с датчиков
            elif command.cmd in [21, 25]:

                sensor_data = self.command_to_sensor_data(command=command)

                # Обновляем статус батареи
                await self.characteristic_set(accessory_name=accessory_name, characteristic='StatusLowBattery',
                                              value=sensor_data['battery'])

                # Данные о температуре и влажности
                if command.cmd == 21:
                    await self.characteristic_set(accessory_name=accessory_name, characteristic='CurrentTemperature',
                                                  value=sensor_data['temp'])
                    await self.characteristic_set(accessory_name=accessory_name, value=sensor_data['hum'],
                                                  characteristic='CurrentRelativeHumidity')

                # Данные датчика движения
                elif command.cmd == 25:
                    await self.characteristic_set(accessory_name=accessory_name, characteristic='MotionDetected',
                                                  value=True)

                    # Выключаем активное состояние
                    await asyncio.sleep(sensor_data['active_time'])
                    await self.characteristic_set(accessory_name=accessory_name, characteristic='MotionDetected',
                                                  value=False)

    async def send_command_to_mtrf(self, command):
        logger.info('Pub command: {}'.format(command))
        await self.mqtt_client.publish(topic=self.write_topic, message=json.dumps(command).encode())

    async def reachability_set(self, accessory_name, reachability):
        await self.mqtt_client.publish(topic='homebridge/to/set/reachability', message=json.dumps({
            'name': accessory_name,
            'reachable': reachability,
        }).encode())

    @staticmethod
    def command_to_sensor_data(command):

        sensor_data = {
            # Состояние батареи: 1-разряжена, 0-заряд батареи в норме
            'battery': int('{:08b}'.format(command.d1)[0]),
            'analog': command.d3,
        }

        if command.cmd == 21:
            temp_bits = '{:08b}'.format(command.d1)[4:] + '{:08b}'.format(command.d0)

            # Тип датчика:
            #   000-зарезервировано
            #   001-датчик температуры (PT112)
            #   010-датчик температуры/влажности (PT111)
            sensor_type = '{:08b}'.format(command.d1)[1:4]

            # Если первый бит 0 - температура считается выше нуля
            if temp_bits[0] == '0':
                temp = int(temp_bits, 2) / 10.
            # Если 1 - ниже нуля. В этом случае необходимо от 4096 отнять полученное значение
            elif temp_bits[0] == '1':
                temp = -((4096 - int(temp_bits, 2)) / 10.)
            else:
                logger.error('Temperature bit 0 must be 0 or 1, get: {}'.format(temp_bits[0]))
                temp = -50

            # Если датчик PT111 (с влажностью), то получаем влажность из 3 байта данных
            hum = command.d2 if sensor_type == '010' else 0

            sensor_data.update({
                'temp': temp,
                'hum': hum,
                'type': sensor_type,
            })

        elif command.cmd == 25:
            sensor_data['active_time'] = command.d0 * 5

        logger.debug('Sensor data: {}'.format(sensor_data))

        return sensor_data

    @staticmethod
    def _characteristic_value_to_noolite_command(accessory_data, characteristic_name, value):
        noolite_data = accessory_data['characteristics'][NOOLITE_SERVICE_NAME]
        cmd = {
            'ch': noolite_data['NooLiteChannel'],
            'mode': 2 if noolite_data.get('NooLiteId') else 0,
            'ctr': 0,
        }

        accessory_characteristics = {}
        [accessory_characteristics.update(characteristics) for characteristics in
         accessory_data['characteristics'].values()]
        logger.info('Accessory characteristics {}'.format(accessory_characteristics))

        if noolite_data.get('NooLiteId'):
            noolite_id_parts = noolite_data['NooLiteId'].split(':')
            cmd.update({
                'ctr': 8,
                'ch': noolite_data['NooLiteChannel'],
                'id0': int(noolite_id_parts[0]),
                'id1': int(noolite_id_parts[1]),
                'id2': int(noolite_id_parts[2]),
                'id3': int(noolite_id_parts[3]),
            })

        if characteristic_name == 'On':
            cmd.update({'cmd': 2 if value is True else 0})

        elif characteristic_name == 'Brightness':
            cmd.update({
                'cmd': 6,
                'fmt': 1,
                'd0': 28 + math.ceil(125 / 100 * value)
            })

        elif characteristic_name == 'Hue':
            hue = accessory_characteristics.get('Hue', 0)
            hue = hue if isinstance(hue, int) else 0

            # Получаем текущиез значения для RGB
            rgb = colorsys.hsv_to_rgb(
                h=(value or hue) / 360,
                s=(100) / 100,
                v=(100) / 100
            )
            logger.info('RGB {} {} {}'.format(rgb[0] * 255, rgb[1] * 255, rgb[2] * 255))
            cmd.update({
                'cmd': 6,
                'fmt': 3,
                'd0': int(rgb[0] * 255),
                'd1': int(rgb[1] * 255),
                'd2': int(rgb[2] * 255),
            })

        return cmd
