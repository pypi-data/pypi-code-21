from wmi import WMI

WMI_CONNECTION = WMI(moniker='root/wmi')

def _set_brightness(brightness):
    WMI_CONNECTION.WmiMonitorBrightnessMethods()[0].WmiSetBrightness(brightness, 0)

def _get_brightness():
    return WMI_CONNECTION.WmiMonitorBrightness()[0].CurrentBrightness

def set(engine, brightness):
    brightness = int(brightness)
    assert 0 <= brightness <= 100, 'Brightness can only be 0 to 100'
    _set_brightness(brightness)

def up(engine, increase):
    increase = int(increase) if increase else 10
    assert increase > 0, 'Brightness increase amount must be a positive integer'
    new_brightness = (_get_brightness() + increase)
    new_brightness = min(new_brightness, 100)
    _set_brightness(new_brightness)

def down(engine, decrease=10):
    decrease = int(decrease) if decrease else 10
    assert decrease > 0, 'Brightness decrease amount must be a positive integer'
    new_brightness = (_get_brightness() - decrease)
    new_brightness = max(new_brightness, 0)
    _set_brightness(new_brightness)
