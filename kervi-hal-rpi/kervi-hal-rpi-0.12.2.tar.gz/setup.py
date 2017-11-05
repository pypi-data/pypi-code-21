import distutils
from setuptools import setup
from kervi_hal_rpi.version import VERSION

try:
    distutils.dir_util.remove_tree("dist")
except:
    pass

setup(
    name='kervi-hal-rpi',
    version=VERSION,
    description="""Raspberry pi hardware abstraction layer for the Kervi automation framework""",
    packages=[
        "kervi_hal_rpi",
    ],
    install_requires=[
        'Adafruit_GPIO'
    ],

)
