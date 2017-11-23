"""influxdbpusher - Minimal and smart pusher of samples to InfluxDB for
asyncio programs"""

__version__ = '0.1.0'
__author__ = 'Gustavo Carneiro <gjcarneiro@gmail.com>'
__all__ = ['InfluxDbPusher']

from .influxdbpusher import InfluxDbPusher, NullInfluxDbPusher
