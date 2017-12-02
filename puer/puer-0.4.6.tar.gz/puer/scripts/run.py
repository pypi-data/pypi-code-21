import logging
from sys import modules
from importlib import import_module, util

from aiohttp.web import run_app

from ..core import AbstractScript
from ..application import Application
from ..route import routes


class RunServer(AbstractScript):
    def main(self):
        settings = self.manager.settings
        logging.basicConfig(level=logging.DEBUG)

        run_app(
            self.app,
            loop=self.manager.loop,
            host=settings.host["ip"],
            port=settings.host["port"]
        )
