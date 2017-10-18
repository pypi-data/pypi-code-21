##############################################################################
#
# Copyright (c) 2012 Vifib SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import errno
import os
import json
import zc.buildout
from jinja2 import Environment, StrictUndefined, \
    BaseLoader, TemplateNotFound, PrefixLoader

DEFAULT_CONTEXT = {x.__name__: x for x in (
  abs, all, any, bin, bool, callable, chr, complex, dict, divmod,
  enumerate, filter, float, format, frozenset, hex, int,
  isinstance, iter, len, list, map, max, min, next, oct, ord,
  pow, repr, reversed, round, set, sorted, str, sum, tuple, zip)}

def _assert(x, *args):
    if x:
        return ""
    raise AssertionError(*args)
DEFAULT_CONTEXT['assert'] = _assert

_buildout_safe_dumps = getattr(zc.buildout.buildout, 'dumps', None)
DUMPS_KEY = 'dumps'
DEFAULT_IMPORT_DELIMITER = '/'

def getKey(expression, buildout, _, options):
    section, entry = expression.split(':')
    if section:
        return buildout[section][entry]
    else:
        return options[entry]

def getJsonKey(expression, buildout, _, __):
    return json.loads(getKey(expression, buildout, _, __))

EXPRESSION_HANDLER = {
    'raw': (lambda expression, _, __, ___: expression),
    'key': getKey,
    'json': (lambda expression, _, __, ___: json.loads(expression)),
    'jsonkey': getJsonKey,
    'import': (lambda expression, _, __, ___:
        __import__(expression, fromlist=['*'], level=0)),
    'section': (lambda expression, buildout, _, __: dict(
        buildout[expression])),
}

class RelaxedPrefixLoader(PrefixLoader):
    """
    Same as PrefixLoader, but accepts imports lacking separator.
    """
    def get_loader(self, template):
        if self.delimiter not in template:
            template += self.delimiter
        return super(RelaxedPrefixLoader, self).get_loader(template)

class RecipeBaseLoader(BaseLoader):
    """
    Base class for import classes altering import path.
    """
    def __init__(self, path, delimiter, encoding):
        self.base = os.path.normpath(path)
        self.delimiter = delimiter
        self.encoding = encoding

    def get_source(self, environment, template):
        path = self._getPath(template)
        # Code adapted from jinja2's doc on BaseLoader.
        if path is None or not os.path.exists(path):
            raise TemplateNotFound(template)
        mtime = os.path.getmtime(path)
        with open(path, 'rb') as f:
            source = f.read().decode(self.encoding)
        return source, path, lambda: mtime == os.path.getmtime(path)

    def _getPath(self, template):
        raise NotImplementedError

class FileLoader(RecipeBaseLoader):
    """
    Single-path loader.
    """
    def _getPath(self, template):
        if template:
            return None
        return self.base

class FolderLoader(RecipeBaseLoader):
    """
    Multi-path loader (to allow importing a folder's content).
    """
    def _getPath(self, template):
        path = os.path.normpath(os.path.join(
            self.base,
            *template.split(self.delimiter)
        ))
        if path.startswith(self.base):
            return path
        return None

LOADER_TYPE_DICT = {
    'rawfile': (FileLoader, EXPRESSION_HANDLER['raw']),
    'file': (FileLoader, getKey),
    'rawfolder': (FolderLoader, EXPRESSION_HANDLER['raw']),
    'folder': (FolderLoader, getKey),
}

class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.encoding = options.get('encoding', 'utf-8')
        import_delimiter = options.get('import-delimiter',
            DEFAULT_IMPORT_DELIMITER)
        import_dict = {}
        for line in options.get('import-list', '').splitlines(False):
            if not line:
                continue
            expression_type, alias, expression = line.split(None, 2)
            if alias in import_dict:
                raise ValueError('Duplicate import-list entry %r' % alias)
            loader_type, expression_handler = LOADER_TYPE_DICT[
                expression_type]
            import_dict[alias] = loader_type(
                expression_handler(expression, buildout, name, options),
                import_delimiter, self.encoding,
            )
        if import_dict:
            loader = RelaxedPrefixLoader(import_dict,
                delimiter=import_delimiter)
        else:
            loader = None
        self.rendered = options['rendered']
        self.template = options['template']
        self.md5sum = options.get('md5sum')
        extension_list = [x for x in (y.strip()
            for y in options.get('extensions', '').split()) if x]
        self.context = context = DEFAULT_CONTEXT.copy()
        if _buildout_safe_dumps is not None:
            context[DUMPS_KEY] = _buildout_safe_dumps
        for line in options.get('context', '').splitlines(False):
            if not line:
                continue
            expression_type, variable_name, expression = line.split(None, 2)
            if variable_name in context:
                raise ValueError('Duplicate context entry %r' % (
                    variable_name, ))
            context[variable_name] = EXPRESSION_HANDLER[expression_type](
                expression, buildout, name, options)
        mode = options.get('mode')
        self.mode = int(mode, 8) if mode else None
        self.env = Environment(
            extensions=extension_list,
            undefined=StrictUndefined,
            loader=loader)
        self.once = options.get('once')

    def install(self):
        if self.once and os.path.exists(self.once):
            return
        template = self.template
        if template.startswith('inline:'):
            source = template[7:].lstrip('\r\n')
            template = '<inline>'
        else:
            template = zc.buildout.download.Download(
                self.buildout['buildout'],
                hash_name=True,
            )(
                template,
                md5sum=self.md5sum,
            )[0]
            with open(template, 'rb') as f:
                source = f.read().decode(self.encoding)
        env = self.env
        template = env.template_class.from_code(env,
            env.compile(source, filename=template),
            env.make_globals(None), None)
        rendered = template.render(**self.context).encode(self.encoding)
        # Unlink any existing file so that umask applies.
        try:
            os.unlink(self.rendered)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise
            outdir = os.path.dirname(self.rendered)
            if outdir and not os.path.exists(outdir):
                os.makedirs(outdir)
        mode = self.mode
        fd = os.open(self.rendered, os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                     (0o777 if rendered.startswith(b'#!') else 0o666)
                     if mode is None else 0)
        try:
            os.write(fd, rendered)
            if mode is not None:
                os.fchmod(fd, mode)
        finally:
            os.close(fd)
        if self.once:
            open(self.once, 'wb').close()
            return
        return self.rendered

    update = install

