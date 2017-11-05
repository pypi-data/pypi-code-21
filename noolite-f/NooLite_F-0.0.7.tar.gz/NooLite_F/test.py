from NooLite_F.MTRF64 import MTRF64Controller, OutgoingData, Action, Mode, MTRF64USBAdapter
from NooLite_F import Dimmer, Switch, RGBLed, ModuleType, RemoteListener, BrightnessDirection
from time import sleep


controller = MTRF64Controller("COM3")
switch = RGBLed(controller, 62, ModuleType.NOOLITE)


class Listener(RemoteListener):
    def off(self):
        switch.off()

    def roll_rgb_color(self):
        switch.roll_rgb_color()

    def brightness_tune_stop(self):
        switch.brightness_tune_stop()

    def on(self):
        switch.on()

    def temporary_on(self, duration: int):
        pass

    def set_brightness(self, brightness: float):
        switch.set_brightness(brightness)

    def brightness_tune_step(self, direction: BrightnessDirection, step: int = None):
        pass

    def brightness_tune_custom(self, direction: BrightnessDirection, speed: float):
        pass

    def brightness_tune_back(self):
        switch.brightness_tune_back()

    def save_preset(self):
        switch.save_preset()

    def brightness_tune(self, direction: BrightnessDirection):
        switch.brightness_tune(direction)

    def switch_rgb_mode_speed(self):
        switch.switch_rgb_mode_speed()

    def switch_rgb_mode(self):
        switch.switch_rgb_mode()

    def switch(self):
        switch.switch()

    def switch_rgb_color(self):
        switch.switch_rgb_color()

    def load_preset(self):
        switch.load_preset()

    def set_rgb_brightness(self, red: float, green: float, blue: float):
        switch.set_rgb_brightness(red, green, blue)


listener = Listener()
controller.set_listener(63, listener)
sleep(60)
