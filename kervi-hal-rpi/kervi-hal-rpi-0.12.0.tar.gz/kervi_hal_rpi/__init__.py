def get_gpio_driver():
    from . import gpio_driver
    return gpio_driver.GPIODriver()

def get_i2c_driver(address, bus):
    from . import i2c_driver
    return i2c_driver.I2CDeviceDriver(address, bus)

def get_one_wire_driver(address):
    from . import one_wire
    return one_wire.OneWireDeviceDriver(address)

def default_i2c_bus():
    return 0

def get_camera_driver(source):
    from . import camera_driver
    return camera_driver.CameraDriver()
