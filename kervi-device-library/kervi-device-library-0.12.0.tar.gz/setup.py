import distutils
from setuptools import setup
from kervi_devices.version import VERSION

try:
    distutils.dir_util.remove_tree("dist")
except:
    pass

setup(
    name='kervi-device-library',
    version=VERSION,
    author='Tim Wentzlau',
    author_email='tim.wentzlau@gmail.com',
    url='https://github.com/kervi/kervi-components',
    description="""Hardware component library for the Kervi automation framework""",
    packages=[
        "kervi_devices",
        "kervi_devices/displays",
        "kervi_devices/gpio",
        "kervi_devices/motors",
        "kervi_devices/platforms",
        "kervi_devices/platforms/common",
        "kervi_devices/platforms/common/sensors",
        "kervi_devices/pwm",
        "kervi_devices/sensors"
    ],
    install_requires=[
        'psutil'
    ]
)
