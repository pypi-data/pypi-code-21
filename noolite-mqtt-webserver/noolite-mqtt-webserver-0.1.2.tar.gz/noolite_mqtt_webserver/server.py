import os
import time
import logging
import argparse

import asyncio
import jinja2
import aiohttp_jinja2
from aiohttp import web

from noolite_mqtt_webserver.noolite_mqtt import NooLiteMqtt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Logging config
logging.basicConfig(format='%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


@aiohttp_jinja2.template('request_manager.html')
async def request_manager(request):
    return {'title': 'Менеджер запросов'}


@aiohttp_jinja2.template('accessories.html')
async def accessories(request):
    if request.method == 'POST':
        new_accessory_data = await request.post()
        if all([field_name in new_accessory_data for field_name in ['name', 'channel', 'noolite_type']]):
            await noolite_mqtt.accessory_create(**new_accessory_data)

    all_accessories = await noolite_mqtt.accessory_search()
    return {'title': 'Аксессуары', 'accessories': all_accessories}


async def write(request):
    uart_params = {
        'mode': 0,
        'ctr':  0,
        'res':  0,
        'ch':   0,
        'cmd':  0,
        'fmt':  0,
        'd0':   0,
        'd1':   0,
        'd2':   0,
        'd3':   0,
        'id0':  0,
        'id1':  0,
        'id2':  0,
        'id3':  0,
    }

    for attr_name, attr_value in request.GET.items():
        if attr_name in uart_params:
            uart_params[attr_name] = int(attr_value)

    before = time.time()
    print('> {}'.format(uart_params))
    response_from_usb = await noolite_mqtt.send_command_to_mtrf(uart_params)
    # response_from_usb = [resp.to_list() for resp in response_from_usb]
    # print('< {}'.format(response_from_usb))
    # print('Time fore request: {}\n'.format(time.time() - before))
    return web.json_response({})


# async def sens(request):
#     channels = [int(ch) for ch in request.GET.get('ch').split(',')]
#     sensor_type = request.GET.get('type')
#     if len(channels) == 1:
#         sensor = noolite_manager.get_sensor(channels[0], sensor_type)
#         return web.json_response(sensor.to_json() if sensor else None)
#     else:
#         sensors = noolite_manager.get_multiple_sensors(channels, sensor_type)
#         return web.json_response([sensor.to_json() if sensor else None for sensor in sensors])


async def accessory_create(request):
    new_accessory_data = await request.json()
    if all([field_name in new_accessory_data for field_name in ['name', 'channel', 'noolite_type']]):
        await noolite_mqtt.accessory_create(
            name=new_accessory_data['name'],
            service_type=new_accessory_data['service'],
            noolite_ch=new_accessory_data['channel'],
            noolite_id=new_accessory_data['noolite_id']
        )
        return web.Response(body=b'OK', status=201)


async def accessory_delete(request):
    accessory_name = request.match_info['name']
    if accessory_name:
        await noolite_mqtt.accessory_delete(accessory_name)
        return web.Response(body=b'OK')

loop = asyncio.get_event_loop()

app = web.Application(loop=loop, debug=True)
aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader(os.path.join(BASE_DIR, 'templates'), followlinks=True),
    context_processors=[aiohttp_jinja2.request_processor]
)
noolite_mqtt = None

# Routes
app.router.add_route('POST', '/accessory', accessory_create)
app.router.add_route('DELETE', '/accessory/{name}', accessory_delete)
app.router.add_get('/api.htm', write)
# app.router.add_get('/sens', sens)
app.router.add_get('/', request_manager, name='request_manager')
app.router.add_route('*', '/accessories', accessories, name='accessories')
app.router.add_static('/', path=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static'), name='static')


class NooLiteMqttServer:
    def __init__(self, mqtt_read_topic, mqtt_write_topic, server_ip, server_port, mqtt_uri):
        self.mqtt_read_topic = mqtt_read_topic
        self.mqtt_write_topic = mqtt_write_topic
        self.server_ip = server_ip
        self.server_port = server_port
        self.mqtt_uri = mqtt_uri

    def run(self):
        global noolite_mqtt
        noolite_mqtt = NooLiteMqtt(
            loop=loop,
            mqtt_read_topic=self.mqtt_read_topic,
            mqtt_write_topic=self.mqtt_write_topic,
            mqtt_host=self.mqtt_uri
        )
        loop.create_task(noolite_mqtt.run())
        web.run_app(app, host=self.server_ip, port=self.server_port)
