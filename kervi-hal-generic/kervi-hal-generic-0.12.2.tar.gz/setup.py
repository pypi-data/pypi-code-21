import distutils
from setuptools import setup
from kervi_hal_generic.version import VERSION

try:
    distutils.dir_util.remove_tree("dist")
except:
    pass

setup(
    name='kervi-hal-generic',
    version=VERSION,
    description="""
    Generic platform driver for the Kervi automation framework.
    """,
    packages=[
        "kervi_hal_generic",
    ],
    install_requires=[
        'psutil'
    ],

)