from NooLite_F.MTRF64.MTRF64USBAdapter import MTRF64USBAdapter, Response, Request, Command, Mode, Action
from NooLite_F import Switch, Dimmer, ModuleType
from NooLite_F.MTRF64 import MTRF64Controller

controller = MTRF64Controller("COM3")
dimmer = Dimmer(controller, 62, ModuleType.NOOLITE)
dimmer.off()

switch = Switch(controller, 60, ModuleType.NOOLITE)
switch.off()


#switch.brightness_tune(BrightnessDirection.DOWN)



#noolite = NooLiteService("COM3")

#noolite.bind(62, mode=Mode.TX)

#noolite.on(62, mode=Mode.TX)
#noolite.off(62, mode=Mode.TX)

#noolite.bright_tune(62, BrightnessDirection.DOWN, mode=Mode.TX)
#noolite.bright_tune_back(62, mode=Mode.TX)
#noolite.bright_tune_custom(62, BrightnessDirection.UP, 1.0, mode=Mode.TX)
#noolite.bright_tune_stop(62, mode=Mode.TX)
#noolite.bright_step(62, BrightnessDirection.DOWN, 0, mode=Mode.TX)

#noolite.set_rgb_brightness(62, 0.5, 0.5, 0.5, mode=Mode.TX)

#noolite.roll_rgb_color(62, mode=Mode.TX)
#noolite.switch_rgb_color(62, mode=Mode.TX)
#noolite.switch_rgb_mode(62, mode=Mode.TX)
#noolite.switch_rgb_mode_speed(62, mode=Mode.TX)


#rgb = RGBLed("COM3", 62, ModuleType.NOOLITE)

#rgb.on()
#rgb.set_rgb_brightness(1.0, 0.0, 0.0)
#rgb.off()
