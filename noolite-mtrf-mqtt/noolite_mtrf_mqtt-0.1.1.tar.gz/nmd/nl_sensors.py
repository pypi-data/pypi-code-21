import time
import asyncio

from ..noolite_mqtt import NooLiteMqtt


class NooLiteSensor:
    def __init__(self, channel, loop):
        self.channel = channel
        self.battery_status = None
        self.last_update = time.time()
        self.loop = loop
        self.noolite_mqtt = NooLiteMqtt()


class TempHumSensor(NooLiteSensor):
    def __init__(self, channel, loop):
        super().__init__(channel, loop)
        self.sensor_type = None
        self.temp = None
        self.hum = None
        self.analog_sens = None

    def __str__(self):
        return 'Ch: {}, battery: {}, temp: {}, hum: {}'.format(self.channel, self.battery_status, self.temp, self.hum)

    def to_json(self):
        json_data = {
            'type': self.sensor_type,
            'temperature': self.temp,
            'humidity': self.hum,
            'battery': self.battery_status,
            'analog_sens': self.analog_sens
        }
        return json_data

    async def read_response_data(self, response):
        temp_bits = '{:08b}'.format(response.d1)[4:] + '{:08b}'.format(response.d0)

        # Тип датчика:
        #   000-зарезервировано
        #   001-датчик температуры (PT112)
        #   010-датчик температуры/влажности (PT111)
        self.sensor_type = '{:08b}'.format(response.d1)[1:4]

        # Если первый бит 0 - температура считается выше нуля
        if temp_bits[0] == '0':
            self.temp = int(temp_bits, 2) / 10.
        # Если 1 - ниже нуля. В этом случае необходимо от 4096 отнять полученное значение
        elif temp_bits[0] == '1':
            self.temp = -((4096 - int(temp_bits, 2)) / 10.)

        # Если датчик PT111 (с влажностью), то получаем влажность из 3 байта данных
        if self.sensor_type == '010':
            self.hum = response.d2

        # Состояние батареи: 1-разряжена, 0-заряд батареи в норме
        self.battery_status = int('{:08b}'.format(response.d1)[0])

        # Значение, считываемое с аналогового входа датчика; 8 бит; (по умолчанию = 255)
        self.analog_sens = response.d3

        self.last_update = time.time()

        accessories = self.noolite_mqtt.accessory_filter(channel=self.channel)

        for accessory_name, accessory_data in accessories.items():

            accessory_characteristics = []
            [accessory_characteristics.extend(list(characteristics.keys())) for characteristics in
             accessory_data['characteristics'].values()]

            if self.temp is not None and 'CurrentTemperature' in accessory_characteristics:
                await self.noolite_mqtt.characteristic_set(
                    accessory_name=accessory_name,
                    characteristic='CurrentTemperature',
                    value=self.temp
                )

            if self.hum is not None and 'CurrentRelativeHumidity' in accessory_characteristics:
                await self.noolite_mqtt.characteristic_set(
                    accessory_name=accessory_name,
                    characteristic='CurrentRelativeHumidity',
                    value=self.hum
                )


class MotionSensor(NooLiteSensor):
    def __init__(self, channel, loop):
        super().__init__(channel, loop)
        self.active_time = None

    def __str__(self):
        return 'Ch: {}, battery: {}, active_time: {}'.format(self.channel, self.battery_status, self.active_time)

    async def read_response_data(self, response):
        self.active_time = response.d0 * 5

        # Состояние батареи: 1-разряжена, 0-заряд батареи в норме
        self.battery_status = int('{:08b}'.format(response.d1)[0])

        self.last_update = time.time()
        await self.set_active_state(self.active_time)

    async def set_active_state(self, delay):

        accessory = await self.noolite_mqtt.accessory_get(channel=self.channel)

        for accessory_name, accessory_data in accessory.items():
            await self.noolite_mqtt.characteristic_set(
                accessory_name=accessory_name,
                characteristic='MotionDetected',
                value=True
            )

            # Выключаем активное состояние
            await asyncio.sleep(delay)
            await self.noolite_mqtt.characteristic_set(
                accessory_name=accessory_name,
                characteristic='MotionDetected',
                value=False
            )

    def is_active(self):
        return self.last_update + self.active_time >= time.time()

    def to_json(self):
        json_data = {
            'battery': self.battery_status,
            'state': 1 if self.is_active() else 0
        }
        return json_data


class SensorManager:
    def __init__(self, nl_mqtt):
        self.nl_mqtt = nl_mqtt
        self.sensors = []
        self.sensors_map = {
            'temp': TempHumSensor,
            'hum': TempHumSensor,
            'motion': MotionSensor
        }

    async def new_data(self, response):
        if response.cmd == 21:
            sensor = self.get_sensor(response.ch, 'temp') or TempHumSensor(channel=response.ch, loop=self.loop)
        elif response.cmd == 25:
            sensor = self.get_sensor(response.ch, 'motion') or MotionSensor(channel=response.ch, loop=self.loop)
        else:
            print('Unknown response: {}'.format(response))
            return

        await sensor.read_response_data(response=response)

        if sensor not in self.sensors:
            self.sensors.append(sensor)
        print(sensor)

    def get_sensor(self, channel, sensor_type):
        sensor_type = self.sensors_map[sensor_type]
        for sensor in self.sensors:
            if sensor.channel == channel and isinstance(sensor, sensor_type):
                return sensor
        return None

    def get_multiple_sensors(self, channels, sensor_type):
        sensors = []
        sensor_type = self.sensors_map[sensor_type]
        for sensor in self.sensors:
            if sensor.channel in channels and isinstance(sensor, sensor_type):
                sensors.append(sensor)
        return sensors
