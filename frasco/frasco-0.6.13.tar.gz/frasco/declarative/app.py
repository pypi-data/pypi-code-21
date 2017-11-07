import os
import sys
import yaml
from ..app import Frasco
from ..actions import load_actions, load_grouped_actions, Context
from ..utils import import_string, logger, deep_update_dict
from ..signals import create_listeners_from_config
from ..views import Blueprint
from .loaders import FeaturesLoader, ActionsLoader, ViewsLoader, ServicesLoader
from flask.helpers import get_root_path
from flask import render_template
from jinja2 import FileSystemLoader
from werkzeug.local import LocalProxy


_decl_app = None

def get_current_decl_app():
    return _decl_app

decl_app = LocalProxy(get_current_decl_app)


def create_app_from_cwd(import_name="__main__", **kwargs):
    return DeclarativeFrasco(import_name, root_path=os.getcwd(),
        set_as_current=True, **kwargs)


class DeclarativeFrasco(Frasco):
    def __new__(cls, import_name, **kwargs):
        decl_kwargs = {k: kwargs.pop(k) for k in kwargs.keys() if k in
                        ('config_filename', 'view_folder', 'feature_folder',
                         'action_folder')}
        factory = DeclarativeFrascoFactory(**decl_kwargs)
        return factory.create_app(import_name, **kwargs)


class DeclarativeFrascoFactory(object):
    """Creates an app from the given configuration file. Will load features, actions
    and blueprints relative to the configuration file
    """

    def __init__(self, config_filename="app.yml", view_folder="views",
                 feature_folder="features", action_folder="actions"):
        self.config_filename = config_filename
        self.view_folder = view_folder
        self.feature_folder = feature_folder
        self.action_folder = action_folder

    def create_app(self, import_name, set_as_current=False, load_all=True, with_feature_blueprints=False, **kwargs):
        app = Frasco(import_name, **kwargs)
        app.factory = self
        if set_as_current:
            global _decl_app
            _decl_app = app
        if load_all:
            self.setup_app(app)
        else:
            self.configure_app(app, with_feature_blueprints)
        return app

    def setup_app(self, app):
        self.configure_app(app, False)
        self.load_all(app)

    def configure_app(self, app, with_feature_blueprints=True, env=None):
        config_path = os.path.join(app.root_path, self.config_filename)
        view_path = os.path.join(app.root_path, self.view_folder)
        feature_path = os.path.join(app.root_path, self.feature_folder)

        app.jinja_loader.loaders.insert(0, FileSystemLoader(view_path))
        app.view_folder = self.view_folder
        app.config.from_yaml(config_path, silent=True)

        env = env or os.environ.get("FRASCO_ENV") or "prod"
        filename, ext = os.path.splitext(config_path)
        env_filename = filename + "-" + env + ext
        app.config['ENV'] = env
        app.config.from_yaml(env_filename, silent=True, deep_update=True)
        app.config.resolve_includes(os.path.dirname(config_path))

        for feature in FeaturesLoader().load(app.config.get('FEATURES', [])):
            app.register_feature(feature, with_blueprints=with_feature_blueprints)
            feature.init_declarative(app)

        if "ERROR_HANDLERS" in app.config:
            for code, template in app.config["ERROR_HANDLERS"].iteritems():
                self.register_error_handler(app, code, template)
        if "BEFORE_REQUEST_ACTIONS" in app.config:
            app.request_actions.extend(load_actions(app.config["BEFORE_REQUEST_ACTIONS"], 'before'))
        if "AFTER_REQUEST_ACTIONS" in app.config:
            app.request_actions.extend(load_actions(app.config["AFTER_REQUEST_ACTIONS"], 'after'))

        create_listeners_from_config(app.config.get("SIGNAL_LISTENERS", []))

    def register_error_handler(self, app, code, template):
        @app.errorhandler(code)
        def func(error):
            return render_template(template, error=error), code

    def load_all(self, app):
        self.load_actions((app))
        self.load_services(app)
        self.load_blueprints(app)

    def load_actions(self, app):
        action_path = os.path.join(app.root_path, self.action_folder)
        action_package = self.action_folder.replace("/", ".")
        if os.path.exists(action_path):
            loader = ActionsLoader(action_path, pypath=action_package)
            for action in loader.load(app):
                app.actions.register(action)

    def load_services(self, app):
        loader = ServicesLoader(os.path.join(app.root_path, "services"))
        for service in loader.load(app):
            app.register_service(service)

    def load_blueprints(self, app):
        view_path = os.path.join(app.root_path, self.view_folder)
        view_package = self.view_folder.replace("/", ".")
        if os.path.exists(view_path):
            loader = ViewsLoader(view_path, pypath=view_package)
            for obj in loader.load(app):
                if isinstance(obj, Blueprint):
                    app.register_blueprint(obj)
                else:
                    app.add_view(obj)

        for feature in app.features:
            feature.init_blueprints(app)