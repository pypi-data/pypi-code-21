"""
tmpld.core.environment
~~~~~~~~~~~~~~

Jinja2 environment for tmpld.

:copyright: (c) 2017 by Joe Black.
:license: Apache2.
"""

import os
import re
import json
import yaml

import jinja2
from jinja2 import FileSystemLoader

from . import util, tags, filters


class TmpldEnvironment(jinja2.environment.Environment):
    def from_string(self, source, relpath=None, globals=None,
                    template_class=None):
        globals = self.make_globals(globals)
        globals['paths'] = util.Path(relpath)
        filename = globals['paths'].filename

        if relpath and relpath not in ('-', '/dev/stdin'):
            mtime = os.path.getmtime(relpath)
            def uptodate():
                try:
                    return os.path.getmtime(relpath) == mtime
                except OSError:
                    return False
        else:
            uptodate = lambda x: True

        cls = template_class or self.template_class
        return cls.from_code(
            self, self.compile(source, filename, relpath), globals, uptodate)


class TemplateEnvironment:
    defaults = dict(
        options=dict(
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,
            keep_trailing_newline=True,
            extensions=[tags.FileTag]
        ),
        glbls=dict(
            cwd=os.getcwd(),
            env=os.environ,
            shell=util.shell,
            file=util.ctx_get_file,
            json=json,
            re=re,
            yaml=yaml,
            xpath=util.xpath,
            jsonpath=util.jsonpath,
            gen_user=util.gen_user,
            gen_pass=util.gen_pass,
            gen_token=util.gen_token
        )
    )

    def __init__(self, data=None, glbls=None, paths=None, options=None,
                 strict=False, **kwargs):
        self.options = util.set_defaults(options, self.defaults['options'])
        self.options['loader'] = FileSystemLoader(paths, followlinks=True)
        self.glbls = util.set_defaults(glbls, self.defaults['glbls'])
        self.glbls['data'] = data or {}
        self.env = TmpldEnvironment(**self.options)
        if strict:
            self.env.undefined = jinja2.StrictUndefined
        self.env.globals.update(self.glbls)
        self.env.filters.update(filters.FilterModule.filters())

    def render(self, template):
        if not template.rendered:
            template.original = template.content
            template.template = self.env.from_string(
                template.content, template.file
            )
            template.content = template.template.render()
            template.rendered = True
        return template
