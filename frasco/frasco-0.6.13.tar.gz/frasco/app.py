from flask import Flask, request
from flask.config import ConfigAttribute, Config as FlaskConfig
from flask.ctx import AppContext, has_request_context
from flask.helpers import locked_cached_property
from jinja2 import ChoiceLoader, FileSystemLoader
from .utils import AttrDict, RequirementMissingError, JSONEncoder, deep_update_dict
from .actions import (ActionList, ActionRegistry, action_resolver, request_context,\
                     current_context, ContextExitException, common_actions, ensure_context)
from .views import ViewContainerMixin
from .decorators import register_hooks
from .templating import JinjaLoader, configure_environment
from .features import FeatureRegistry
from .request_params import auto_inject_request_params
from .marshaller import marshaller_context
import inspect
import os
import yaml
import errno
import sys


class Config(FlaskConfig):
    """Subclass of Flask's Config class to add support to load from YAML file
    """

    def from_json(self, filename, silent=False, deep_update=False):
        filename = os.path.join(self.root_path, filename)

        try:
            with open(filename) as json_file:
                obj = json.loads(json_file.read())
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        return self.from_mapping(obj, _deep_update=deep_update)

    def from_yaml(self, filename, silent=False, deep_update=False):
        filename = os.path.join(self.root_path, filename)

        try:
            with open(filename) as yaml_file:
                obj = yaml.load(yaml_file.read())
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        return self.from_mapping(obj, _deep_update=deep_update)

    def from_mapping(self, *mapping, **kwargs):
        mappings = []
        if len(mapping) == 1:
            if hasattr(mapping[0], 'items'):
                mappings.append(mapping[0].items())
            else:
                mappings.append(mapping[0])
        elif len(mapping) > 1:
            raise TypeError(
                'expected at most 1 positional argument, got %d' % len(mapping)
            )
        deep_update = kwargs.pop('_deep_update', False)
        mappings.append(kwargs.items())
        for mapping in mappings:
            if deep_update:
                deep_update_dict(self, dict((k.upper(), v) for (k, v) in mapping))
            else:
                for (key, value) in mapping:
                    self[key.upper()] = value
        return True

    def from_file(self, filename, silent=False, deep_update=False):
        if filename.endswith(".py"):
            self.from_pyfile(filename, silent=silent)
        elif filename.endswith(".js") or filename.endswith(".json"):
            self.from_json(filename, silent=silent, deep_update=deep_update)
        elif filename.endswith(".yml"):
            self.from_yaml(filename, silent=silent, deep_update=deep_update)
        else:
            raise RuntimeError("Unknown config file extension")

    def resolve_includes(self, relative_to=".", key="INCLUDE_FILES"):
        for spec in self.pop(key, []):
            if not isinstance(spec, dict):
                spec = {"filename": spec}
            filename = os.path.join(relative_to, spec["filename"])
            self.from_file(filename, silent=spec.get("silent", False),
                deep_update=spec.get("deep_update", False))


class FrascoAppContext(AppContext):
    def push(self):
        action_resolver.push(self.app.actions)
        super(FrascoAppContext, self).push()

    def pop(self, exc=None):
        super(FrascoAppContext, self).pop(exc)
        action_resolver.pop()


class Frasco(ViewContainerMixin, Flask):
    """Flask subclass that adds support to register feature and actions
    """
    config_class = Config
    json_encoder = JSONEncoder

    processes = ConfigAttribute('PROCESSES')
    services_url_prefix = ConfigAttribute('SERVICES_URL_PREFIX')
    services_subdomain = ConfigAttribute('SERVICES_SUBDOMAIN')

    def __init__(self, import_name, **kwargs):
        self.feature_blueprint_names = set()
        with_common_actions = kwargs.pop('with_common_actions', True)
        super(Frasco, self).__init__(import_name, **kwargs)
        self.features = FeatureRegistry()
        self.actions = ActionRegistry()
        self.services = AttrDict()
        self.views = AttrDict()
        self.request_actions = ActionList()
        self.before_request(self.execute_before_request_actions)
        self.after_request(self.execute_after_request_actions)
        if with_common_actions:
            self.actions.register(common_actions)

    def make_config(self, instance_relative=False):
        root_path = self.root_path
        if instance_relative:
            root_path = self.instance_path
        return self.config_class(root_path, dict(self.default_config,
            PROCESSES=[],
            SERVICES_URL_PREFIX='/api',
            SERVICES_SUBDOMAIN=None))

    def update_template_context(self, context):
        context["current_context"] = current_context
        super(Frasco, self).update_template_context(context)

    def full_dispatch_request(self):
        with request_context(self, request), marshaller_context.once(), auto_inject_request_params.once():
            return super(Frasco, self).full_dispatch_request()

    def preprocess_request(self):
        try:
            return super(Frasco, self).preprocess_request()
        except ContextExitException as e:
            return e.result

    def process_response(self, response):
        # ensure_context() is needed because process_response() can be called outside
        # of full_dispatch_request in case of error
        with ensure_context():
            try:
                return super(Frasco, self).process_response(response)
            except ContextExitException as e:
                return self.make_response(e.result)

    def app_context(self):
        return FrascoAppContext(self)

    def log_exception(self, exc_info):
        if not isinstance(exc_info, tuple):
            exc_info = sys.exc_info()
        if has_request_context():
            super(Frasco, self).log_exception(exc_info)
        else:
            self.logger.error('Exception [outside of request context]', exc_info=exc_info)

    def create_jinja_environment(self):
        env = super(Frasco, self).create_jinja_environment()
        env.globals.update(app=self)
        configure_environment(env)
        macro_file = os.path.join(self.root_path, "macros.html")
        if os.path.exists(macro_file):
            env.macros.register_file(macro_file)
        macro_dir = os.path.join(self.root_path, "macros")
        if os.path.exists(macro_dir):
            env.macros.register_directory(macro_dir)
        return env

    def create_global_jinja_loader(self):
        return JinjaLoader(self)

    @locked_cached_property
    def jinja_loader(self):
        loader = ChoiceLoader([])
        if self.template_folder is not None:
            loader.loaders.append(FileSystemLoader(os.path.join(self.root_path,
                                                 self.template_folder)))
        return loader

    def register_blueprint(self, blueprint, **options):
        with self.app_context(), self.actions:
            return super(Frasco, self).register_blueprint(blueprint, **options)

    def register_feature(self, feature, with_blueprints=True):
        if feature.requires is not None:
            for r in feature.requires:
                if r not in self.features:
                    raise RequirementMissingError("Feature '%s' requires '%s'" % (feature.name, r))
        self.features.register(feature)
        self.actions.register_many(feature.actions, feature.name)
        feature.init_app(self)
        if feature.commands:
            for cmd in feature.commands:
                self.cli.add_command(cmd)
        if feature.hooks is not None:
            for func, hooks in feature.hooks:
                register_hooks(func, hooks, self)
        if with_blueprints:
            feature.init_blueprints(self)
        return feature

    def init_feature_blueprints(self):
        for feature in self.features:
            feature.init_blueprints(self)

    def execute_before_request_actions(self):
        self.request_actions.execute(limit_groups=('before', None))

    def execute_after_request_actions(self, response):
        current_context["response"] = response
        self.request_actions.execute(limit_groups='after')
        return response

    def add_view(self, view):
        if inspect.isclass(view):
            view = view(self_var=self)
        self.views[view.name] = view
        with self.app_context(), self.actions:
            view.register(self)

    def register_service(self, service):
        self.services[service.name] = service
        self.actions.register_many(service.actions, service.name)
        if service.exposed:
            self.register_service_blueprint(service.as_blueprint())
        return service

    def register_service_blueprint(self, blueprint):
        self.register_blueprint(blueprint,
            url_prefix=self.services_url_prefix,
            subdomain=self.services_subdomain)

    @property
    def action(self):
        return self.actions.action

    def service(self, cls):
        self.register_service(cls())
        return cls