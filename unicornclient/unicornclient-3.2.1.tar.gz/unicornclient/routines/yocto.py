import logging

from unicornclient import routine
from unicornclient import message

try:
    from yoctopuce.yocto_api import YAPI
    from yoctopuce.yocto_temperature import YTemperature
except ImportError:
    YAPI, YTemperature = None, None
    logging.warning("No yoctopuce module")

class Routine(routine.Routine):
    def __init__(self):
        routine.Routine.__init__(self)
        self.temp1 = None
        self.temp2 = None

    def run(self):
        while True:
            self.queue.get()

            self.update_temperatures()

            text = str(self.temp1)[:3] + str(self.temp2)[:3]
            payload = {
                'type':'status',
                'status': {
                    'temp1' : self.temp1,
                    'temp2' : self.temp2,
                }
            }

            self.manager.forward('dothat', {'text': text})
            self.manager.send(message.Message(payload))

            self.queue.task_done()

    def update_temperatures(self):
        if not YAPI or not YTemperature:
            raise Exception('no module')

        YAPI.RegisterHub("usb")
        sensor = YTemperature.FirstTemperature()

        if sensor is None:
            raise Exception('no sensor')
        if not (sensor.isOnline()):
            raise Exception('sensor offline')

        serial = sensor.get_module().get_serialNumber()
        channel1 = YTemperature.FindTemperature(serial + '.temperature1')
        channel2 = YTemperature.FindTemperature(serial + '.temperature2')

        if channel1.isOnline() and channel2.isOnline():
            self.temp1 = channel1.get_currentValue()
            self.temp2 = channel2.get_currentValue()

        YAPI.FreeAPI()
