from thingy52.thingy52 import Thingy52
from thingy52.delegates import DefaultDelegate
from thingy52.services import AudioSample
import atexit
import requests
from time import sleep, time

t = Thingy52("E2:D9:D5:C6:30:26")


class PicamDelegate(DefaultDelegate):
    def __init__(self, thingy52, handles):
        DefaultDelegate.__init__(self)
        self.thingy52 = thingy52
        self.handles = handles

        self.heading = 0
        self.yaw = 0
        self.roll = 0
        self.yaw_offset = None
        self.pitch = 0
        self.incline = 0
        self.min_elapsed_time = 0.3

        self.time = time()
        url = "http://192.168.1.109:9595"
        self.pan_url = url + '/api/pan/{}'
        self.tilt_url = url + '/api/tilt/{}'
        self.led_url = url + '/api/led/{}'

        self._button_activated = False

    def handleNotification(self, cHandle, data):

        thingy_char = self.handles[cHandle]
        name = thingy_char.common_name

        val = thingy_char.conversion_func(data)
        # print("{}: {}".format(name, val))

        if name is "button" and val is True:
            self.on_button_pressed()

        tick = time()
        if tick - self.time < self.min_elapsed_time:
            # print(tick - self.time)
            return
        else:
            self.time = tick

        if name == "euler":
            # roll: [-180, 180]
            # pitch: [-90, 90]
            # yaw: [-180, 180]

            (roll, pitch, yaw) = val

            # Todo: offsetting heading at start
            if self.yaw_offset is None:
                self.yaw_offset = yaw
            # print("roll {} - pitch {} - yaw {}".format(roll, pitch, yaw))

            if abs(roll - self.roll) + abs(yaw - self.yaw) > 2:
                self.roll = roll
                tilt = roll
                try:
                    req_roll = self.tilt_url.format(int(tilt))
                    requests.get(req_roll, timeout=0.3)
                except Exception as e:
                    pass

                self.yaw = yaw
                if yaw < 0 and roll > 90:
                    pan = 180 - (180 + yaw)
                elif yaw > 0 and roll < 90:
                    pan = 180 - yaw
                else:
                    self.thingy52.ui.rgb_constant(255, 0, 0)
                    return
                self.thingy52.ui.rgb_constant(0, 0, 255)

                # print("PAN: ", pan)
                self.pan_camera(pan)

    def pan_camera(self, pan):
        try:
            req_yaw = self.pan_url.format(int(pan))
            requests.get(req_yaw, timeout=0.3)
        except Exception as e:
            pass

    def on_button_pressed(self):
        self._button_activated = not self._button_activated
        # if self._button_activated:
        #     self.thingy52.sound.play_sample(AudioSample.COIN_1)
        # else:
        #     self.thingy52.sound.play_sample(AudioSample.HIT)
        brightness = 255 if self._button_activated else 0
        try:
            requests.get(self.led_url.format(brightness), timeout=0.3)
        except Exception as e:
            pass


atexit.register(t.disconnect)
t.setDelegate(PicamDelegate(t, t.handles))

# todo: toggle led with button
t.ui.toggle_notifications(characteristic="button", enable=True)

t.motion.toggle_notifications(characteristic="euler", enable=True)
while True:
    t.waitForNotifications(0.1)
