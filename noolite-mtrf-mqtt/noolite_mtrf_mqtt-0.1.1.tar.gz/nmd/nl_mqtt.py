import time
import json
import logging
import asyncio

from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_0, QOS_1, QOS_2

from .nl_serial import NooliteSerial
from .utils import Singleton

logger = logging.getLogger(__name__)


INPUT_TOPIC = 'noolite/mtrf/send'
OUTPUT_TOPIC = 'noolite/mtrf/receive'


MQTT_SUBSCRIBTIONS = [
    (INPUT_TOPIC, QOS_0),
]


class MqttDriver(metaclass=Singleton):
    def __init__(self, mtrf_tty_name, loop, mqtt_uri='mqtt://127.0.0.1/', commands_delay=0.1):
        self.mqtt_client = MQTTClient(config={'auto_reconnect': True})
        self.mqtt_uri = mqtt_uri
        self.commands_delay = commands_delay
        self.noolite_serial = NooliteSerial(loop=loop, tty_name=mtrf_tty_name,
                                            input_command_callback_method=self.input_serial_data)
        self.commands_to_send_queue = asyncio.Queue()
        loop.create_task(self.send_command_to_noolite())

    async def run(self):
        await self.mqtt_client.connect(self.mqtt_uri)
        await self.mqtt_client.subscribe(MQTT_SUBSCRIBTIONS)

        while True:
            logger.info('Waiting messages from mqtt...')
            message = await self.mqtt_client.deliver_message()

            topic = message.topic
            payload = message.publish_packet.payload.data

            try:
                payload = json.loads(payload.decode())
            except Exception as e:
                logger.exception(e)
                continue

            logger.info('In message: {}\n{}'.format(topic, json.dumps(payload, indent=4)))

            if topic == 'noolite/mtrf/send':
                await self.commands_to_send_queue.put(payload)

    async def send_command_to_noolite(self):
        last_command_send_time = 0
        while True:
            logger.info('Waiting commands to send...')
            payload = await self.commands_to_send_queue.get()
            logger.info('Get command from queue: {}'.format(payload))

            # Формируем и отправляем команду к noolite
            noolite_cmd = self.payload_to_noolite_command(payload)

            if time.time() - last_command_send_time < self.commands_delay:
                logger.info('Wait before send next command: {}'.format(
                    self.commands_delay - (time.time() - last_command_send_time)))
                await asyncio.sleep(self.commands_delay - (time.time() - last_command_send_time))

            await self.noolite_serial.send_command(**noolite_cmd)
            last_command_send_time = time.time()

    async def input_serial_data(self, command):
        logger.info('Pub command: {}'.format(command))
        await self.mqtt_client.publish(topic=OUTPUT_TOPIC, message=json.dumps({'command': command.to_list()}).encode())

    @staticmethod
    def payload_to_noolite_command(payload):
        return payload
