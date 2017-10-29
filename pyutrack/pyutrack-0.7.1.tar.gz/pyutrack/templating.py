import collections

import six
from jinja2 import Environment, meta
import colors
import asciitree


def safelist(value, sep=',', padding=0,  quote=False):
    if isinstance(value, six.string_types):
        return value
    elif isinstance(value, collections.Iterable):
        return "".join([sep + " "*padding + k for k in value])
    return value

class ProxyTemplate(object):
    env = Environment()
    # add handy filters for formatting text on console
    env.filters['red'] = colors.red
    env.filters['green'] = colors.green
    env.filters['yellow'] = colors.yellow
    env.filters['bold'] = colors.bold
    env.filters['italic'] = colors.italic
    env.filters['white'] = colors.white
    env.filters['color'] = colors.color
    env.filters['safelist'] = safelist

    def __init__(self, template_source):
        ast = self.env.parse(template_source)
        self.template_requirements = meta.find_undeclared_variables(ast)
        self.compiled_template = self.env.from_string(template_source)

    def render(self, object):
        return self.compiled_template.render(
            {k: object.attribute(k) for k in self.template_requirements}
        )


class BuiltinTemplate(ProxyTemplate):
    __render_field__ = '__render__'

    def __init__(self, resource_type):
        self.fields = getattr(resource_type, self.__render_field__)
        super(BuiltinTemplate, self).__init__(
            self.header() + self.field_sep.join([self.field_template(field) for field in self.fields]) + self.footer()
        )

    def field_template(self, field):
        return "{{%s|safelist(sep=',')}}" % field

    def header(self):
        return ""

    def footer(self):
        return ""


class CSVTemplate(BuiltinTemplate):
    field_sep = ','
    def field_template(self, field):
        return "{{%s|safelist(sep=',', quote=True)}}" % field

class TSVTemplate(CSVTemplate):
    field_sep = '\t'


class Defaultemplate(BuiltinTemplate):
    field_sep = ''

    def field_template(self, field):
        return """{%% if %s %%}%s:{{%s|safelist(sep='\n-', padding=20)}}\n{%% endif %%}""" % (
            field, field.title().ljust(20), field
        )

    def footer(self):
        return '\n'


class TreeTemplate(BuiltinTemplate):
    field_sep = ''

    def render(self, object):
        tree = {}
        cur = tree[colors.blue(str(object))] = {}
        for key in self.template_requirements:
            item = object.attribute(key)
            if isinstance(item, six.string_types) or not isinstance(item, collections.Iterable):
                cur[colors.bold(key)] = {item: {}}
            else:
                cur[colors.bold(key)] = {i: {} for i in item}

        la = asciitree.LeftAligned()
        return la(tree)

BUILTIN_TEMPLATES = {
    'csv': CSVTemplate,
    'tsv': TSVTemplate,
    'oneline': CSVTemplate,
    'tree': TreeTemplate,
    'default': Defaultemplate
}
