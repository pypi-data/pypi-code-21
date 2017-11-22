from setuptools import setup, find_packages


try:
    from pypandoc import convert
except ImportError:
    import io

    def convert(filename, fmt):
        with io.open(filename, encoding='utf-8') as fd:
            return fd.read()


setup(
    name='noolite_mtrf_mqtt',
    description='NooLite MTRF serial port to MQTT messages',
    url='https://bitbucket.org/AlekseevAV/noolite-mtrf-to-mqtt',
    version='0.1.1',
    long_description=convert('README.md', 'rst'),
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'hbmqtt',
        'pyserial',
    ],
    entry_points={
        'console_scripts': ['noolite_mtrf_mqtt=nmd.main:run'],
    }
)
