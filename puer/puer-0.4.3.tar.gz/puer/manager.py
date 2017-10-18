import argparse
import asyncio
from sys import modules
from importlib import import_module, util
from puer.settings import Settings
from .scripts import scripts


__all__ = ['Manager']


class Manager(object):
    def __init__(self, args: argparse.Namespace, loop=None):
        self.args = args
        self.config_name = "%s.yaml" % self.args.config_name
        self.script_name = self.args.script_name
        self.settings = Settings.from_yaml(self.config_name)
        self.scripts = scripts
        self.loop = loop or asyncio.get_event_loop()
        self._load_apps(self.settings.apps)
        script = self.scripts[self.script_name](self)
        script.main()

    @staticmethod
    def parse_args():
        arg_parser = argparse.ArgumentParser(description='Manage script for Puer framework')
        arg_parser.add_argument('config_name', metavar='config_name', help='configuration file name '
                                                                 '(extension must be ".yaml")')
        arg_parser.add_argument('script_name', metavar='script_name', help='configuration name')
        return arg_parser.parse_args()

    def _load_apps(self, apps: list):
        for app in apps:
            self._load_scripts_from_app(app)
            self._load_urls_from_app(app)

    def _load_scripts_from_app(self, app):
        package_name = "%s.scripts" % app
        if util.find_spec(package_name) is not None:
            import_module(package_name)
            self.scripts.update(modules[package_name].scripts)

    def _load_urls_from_app(self, app):
        package_name = "%s.urls" % app
        if util.find_spec(package_name) is not None:
            import_module(package_name, app)
