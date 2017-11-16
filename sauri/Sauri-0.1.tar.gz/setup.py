from setuptools import setup

setup(
    name='Sauri',
    author='Mike Healey',
    author_email='healem@alum.rpi.edu',
    url='https://github.com/healem/sauri',
    version='0.1',
    packages=['sauri',
              'sauri.common',
              'sauri.messaging',
              'sauri.messaging.blocking',
              'sauri.messaging.blocking.test',
              'sauri.sensors',
              'sauri.sensors.test',
              'sauri.sensors.temperature',
              'sauri.sensors.temperature.test',],
    install_requires=['mock',
                      'coverage',
                      'PyYAML',
                      'pika',],
    license='MIT',
    long_description=open('README').read(),
)