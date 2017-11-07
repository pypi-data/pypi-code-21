from flask import render_template_string, url_for, json
from flask._compat import iteritems
from jinja2 import (BaseLoader, FileSystemLoader, ChoiceLoader, PrefixLoader,\
                    Environment as BaseEnvironment, nodes, TemplateNotFound)
from jinja2.ext import ExprStmtExtension
from ..utils import url_for_static, url_for_same, slugify
from jinja_macro_tags import MacroLoader, FileLoader, configure_environment as configure_macro_environment
from jinja_layout import LayoutExtension
import os
from .extensions import *
from helpers import *
from frasco import trans
from ..trans import lazy_translate


class AliasLoader(BaseLoader):
    def __init__(self, aliases=None):
        self.aliases = aliases or {}

    def get_source(self, environment, template):
        if template in self.aliases:
            if isinstance(self.aliases[template], BaseLoader):
                return self.aliases[template].get_source(environment, template)
            return environment.loader.get_source(environment, self.aliases[template])
        raise TemplateNotFound(template)

    def list_templates(self):
        return self.aliases.keys()


class JinjaLoader(MacroLoader):
    """This Jinja loader replaces Flask's DispatchingJinjaLoader and adds
    multiple overriding points. Loaders can be added as a top level loader
    (first in the search path) using append() or to the lists feature_loaders
    and bottom_loaders. Loaders will be searched in the following order:
    top level loaders, the application's loader, loaders from blueprints
    added by the user, feature_loaders, loaders from blueprints provided
    by features, bottom_loaders.
    """
    def __init__(self, app):
        self.app = app
        self._loaders = []
        self.layout_loader = None
        self.feature_loaders = []
        self.macro_loaders = []
        self.bottom_loaders = []
        self.prefix_loader = PrefixLoader({
            # because we don't call MacroLoader's constructor to provide
            # our own loaders property, we define the prefix_loader with the
            # __macros__ entry
            "__macros__": ChoiceLoader(self.macro_loaders),
            # these prefixes allow for direct access to templates
            # defined by features
            "__super__": ChoiceLoader([
                ChoiceLoader(self.feature_loaders),
                ChoiceLoader(self._iter_feature_blueprint_loaders()),
                ChoiceLoader(self.bottom_loaders)])})

    def append(self, loader):
        self._loaders.append(loader)

    def add_path(self, path):
        self.append(FileSystemLoader(path))

    def add_prefix(self, prefix, loader):
        self.prefix_loader.mapping[prefix] = loader

    def add_super(self, loader):
        self.prefix_loader.mapping["__super__"].loaders.insert(0, loader)

    def set_layout_alias(self, template):
        if not self.layout_loader:
            self.layout_loader = AliasLoader()
        self.layout_loader.aliases["layout.html"] = template

    @property
    def loaders(self):
        # loaders added directly on this loader
        for loader in self._loaders:
            yield loader

        # app loader
        loader = self.app.jinja_loader
        if loader is not None:
            yield loader

        # loaders for blueprints added by the user
        for loader in self._iter_app_blueprint_loaders():
            yield loader

        if self.layout_loader:
            yield self.layout_loader

        # loaders that overrides blueprints provided by features
        for loader in self.feature_loaders:
            yield loader

        # loaders for blueprints provided by features
        for loader in self._iter_feature_blueprint_loaders():
            yield loader

        # loaders that are at the bottom
        for loader in self.bottom_loaders:
            yield loader

        yield self.prefix_loader

    def _iter_app_blueprint_loaders(self):
        for name, blueprint in iteritems(self.app.blueprints):
            if name in self.app.feature_blueprint_names:
                continue
            loader = blueprint.jinja_loader
            if loader is not None:
                yield loader

    def _iter_feature_blueprint_loaders(self):
        for name in self.app.feature_blueprint_names:
            loader = self.app.blueprints[name].jinja_loader
            if loader is not None:
                yield loader


class Environment(BaseEnvironment):
    def __init__(self, app, **options):
        if 'autoescape' not in options:
            options['autoescape'] = app.select_jinja_autoescape
        if 'auto_reload' not in options:
            options['auto_reload'] = app.debug \
                or app.config['TEMPLATES_AUTO_RELOAD']
        super(Environment, self).__init__(**options)
        self.app = app
        configure_environment(self)
        self.globals["config"] = app.config


def configure_environment(env, with_blocks=True, with_macros=True, with_layout=True, with_trans=True):
    env.add_extension(ExprStmtExtension)
    env.add_extension(RemoveYamlFrontMatterExtension)
    configure_macro_environment(env, wrap_loader=False)
    env.add_extension(LayoutExtension)
    env.add_extension(FlashMessagesExtension)
    env.globals.update(real_dict=dict,
                       getattr=getattr,
                       url_for=url_for,
                       url_for_static=url_for_static,
                       url_for_same=url_for_same,
                       html_tag=html_tag,
                       html_attributes=html_attributes,
                       plural=plural)
    env.filters.update(slugify=slugify,
                       tojson=json.tojson_filter,
                       nl2br=nl2br,
                       timeago=timeago)

    if with_trans:
        env.globals.update(translate=trans.translate,
                           ntranslate=trans.ntranslate,
                           _=trans.translate)
        env.filters.update(datetimeformat=trans.format_datetime,
                           dateformat=trans.format_date,
                           timeformat=trans.format_time)

    if with_blocks:
        env.add_extension(jinja_block_as_fragment_extension("content"))
    if with_macros:
        env.macros.register_file(os.path.join(os.path.dirname(__file__), "macros.html"), "frasco.html")
    if with_layout:
        env.loader.bottom_loaders.append(FileLoader(
            os.path.join(os.path.dirname(__file__), "layout.html"), "frasco_layout.html"))
        env.loader.set_layout_alias("frasco_layout.html")
    env.default_layout = "layout.html"


def render_layout(layout_name, content, **context):
    """Uses a jinja template to wrap the content inside a layout.
    Wraps the content inside a block and adds the extend statement before rendering it
    with jinja. The block name can be specified in the layout_name after the filename separated
    by a colon. The default block name is "content".
    """
    layout_block = "content"
    if ":" in layout_name:
        layout_name, layout_block = layout_name.split(":")
    tpl = '{%% extends "%s" %%}{%% block %s %%}%s{%% endblock %%}' % (layout_name, layout_block, content)
    return render_template_string(tpl, **context)


def get_template_source(app, filename):
    (source, _, __) = app.jinja_env.loader.get_source(app.jinja_env, filename)
    return source


def parse_template(app, filename):
    """Parses the given template using the jinja environment of the given app
    and returns the AST. ASTs are cached in parse_template.cache
    """
    if not hasattr(parse_template, "cache"):
        parse_template.cache = {}
    if filename not in parse_template.cache:
        source = get_template_source(app, filename)
        parse_template.cache[filename] = app.jinja_env.parse(source, filename=filename)
    return parse_template.cache[filename]


def jinja_node_to_python(node):
    """Converts a Jinja2 node to its python equivalent
    """
    if isinstance(node, nodes.Const):
        return node.value
    if isinstance(node, nodes.Neg):
        return -jinja_node_to_python(node.node)
    if isinstance(node, nodes.Name):
        return node.name
    if isinstance(node, (nodes.List, nodes.Tuple)):
        value = []
        for i in node.items:
            value.append(jinja_node_to_python(i))
        return value
    if isinstance(node, nodes.Dict):
        value = {}
        for pair in node.items:
            value[pair.key.value] = jinja_node_to_python(pair.value)
        return value
    if isinstance(node, nodes.Call):
        if not isinstance(node.node, nodes.Name) or node.node.name not in ("_", "translate", "gettext"):
            raise FormDefinitionError("Cannot convert function calls from jinja to python other than translation calls")
        return lazy_translate(jinja_node_to_python(node.args[0]))
    raise Exception("Cannot convert jinja nodes to python")