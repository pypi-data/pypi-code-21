import argparse
import asyncio
from sys import modules
from importlib import import_module, util
from puer.settings import Settings
from .scripts import scripts

from puer.application import Application
from puer.route import routes


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
        self._create_application()
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

    def _create_application(self):
        # Setting middlewares for app
        middlewares = []
        for middleware in self.settings.middlewares:
            middleware_path = middleware.split('.')
            package_name = '.'.join(middleware_path[:-1])
            middleware_name = middleware_path[-1:][0]
            import_module(package_name)
            middlewares.append(getattr(modules[package_name], middleware_name))

        app = Application(
            middlewares=middlewares
        )
        app["settings"] = self.settings
        for m in self.settings.modules:
            module_splitted = m.split('.')
            package_name = '.'.join(module_splitted[0:-1])
            module_cls = module_splitted[-1]
            if util.find_spec(package_name) is not None:
                import_module(package_name)
                c = getattr(modules[package_name], module_cls)
                if c is not None:
                    mod = c(self, app)
                    app[mod.name] = mod.value

        # Setting signals for app
        for signal in self.settings.signals:
            app_signals = getattr(app, signal)
            for app_signal in self.settings.signals[signal]:
                app_signal_path = app_signal.split('.')
                package_name = '.'.join(app_signal_path[:-1])
                app_signal_name = app_signal_path[-1:][0]
                import_module(package_name)
                app_signals.append(getattr(modules[package_name], app_signal_name))

        # Setting routes for app
        for res in routes:
            name = res[3]
            app.router.add_route(res[0], res[1], res[2], name=name)

        self.application = app
