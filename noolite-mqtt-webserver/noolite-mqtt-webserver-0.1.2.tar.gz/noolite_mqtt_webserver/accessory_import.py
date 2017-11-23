"""
Импорт аксессуаров через MQTT
Аксессуары нужно добавить в переменную ACCESSORIES_TO_CREATE в виде словаря:

    {
        'name': 'slr_1', 
        'service_type': 'Switch', 
        'noolite_ch': 0, 
        'noolite_id': '00:00:00:09': # если есть
    }
    
service_type - один из слеудщих:

    MotionSensor        - датчик движения
    TemperatureSensor   - датчик температуры
    HumiditySensor      - датчик влажности
    Switch              - выключатель
    Lightbulb           - светодиодная лента
    Lightbulb_b         - диммируемый выключатель

"""
import asyncio
from noolite_mqtt_webserver.noolite_mqtt import NooLiteMqtt


ACCESSORIES_TO_CREATE = [

]


async def add_accessories():
    nl_mqtt = NooLiteMqtt()

    for accessory in ACCESSORIES_TO_CREATE:
        await nl_mqtt.accessory_create(**accessory)

loop = asyncio.get_event_loop()

loop.run_until_complete(add_accessories())
loop.close()
