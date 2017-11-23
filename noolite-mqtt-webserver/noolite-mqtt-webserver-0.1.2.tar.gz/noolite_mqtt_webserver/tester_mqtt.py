import json
import time

import asyncio
from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_0, QOS_1, QOS_2


before = time.time()
mqtt_client = MQTTClient(config={'auto_reconnect': True})


async def run(topic, commands, repeat=1):
    await mqtt_client.connect('mqtt://127.0.0.1/')

    for command in commands:
        for index in range(repeat):
            await mqtt_client.publish(
                topic,
                json.dumps({"ch": 0, "mode": 2, "ctr": 8, "id0": 0, "id1": 0, "id2": 2, "id3": 112, "cmd": 2 if index % 2 else 0}).encode(),
            )





total_before = time.time()
loop = asyncio.get_event_loop()
future = asyncio.ensure_future(run(
    'noolite/mtrf/send',
    [{"ch": 0, "mode": 2, "ctr": 8, "id0": 0, "id1": 0, "id2": 2, "id3": 112, "cmd": 2}],
    10
))
loop.run_until_complete(future)
print('Total time: {}'.format(time.time() - total_before))
