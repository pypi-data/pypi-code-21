from setuptools import setup, find_packages


try:
    from pypandoc import convert
except ImportError:
    import io

    def convert(filename, fmt):
        with io.open(filename, encoding='utf-8') as fd:
            return fd.read()

setup(
    name='noolite-mqtt-webserver',
    description='Web server for NooLite.',
    url='https://bitbucket.org/AlekseevAV/noolite-mqtt-web-server',
    version='0.1.2',
    long_description=convert('README.md', 'rst'),
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'aiohttp',
        'aiodns',
        'Jinja2',
        'aiohttp-jinja2',
        'cchardet',
        'hbmqtt'
    ],
    entry_points={
        'console_scripts': ['noolite_web_server=noolite_mqtt_webserver.main:main'],
    }
)
