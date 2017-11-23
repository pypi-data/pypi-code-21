"""
tmpld.cli.main
~~~~~~~~~~~~~~

Cement CLI main app logic for tmpld.

:copyright: (c) 2017 by Joe Black.
:license: Apache2.
"""

import os
import sys
import argparse

from cement.core.foundation import CementApp
from cement.core.controller import CementBaseController, expose

import pyrkube

from ..core import environment
from ..core.util import try_import
from . import handlers, loaders, util


class TmpldController(CementBaseController):
    class Meta:
        label = 'base'
        arguments = [
            (['templates'],
             dict(help='template files to render',
                  action='store',
                  type=loaders.TemplateLoader(),
                  nargs='+')),
            (['-d', '--data'],
             dict(help='file(s) containing context data',
                  action=loaders.DataDict,
                  default={},
                  type=argparse.FileType())),
            (['-s', '--strict'],
             dict(help='Raise an exception if a variable is not defined',
                  action='store_true',
                  default=False))
        ]

    def _get_ext(self, name, config):
        if name == 'kube':
            try:
                kube = pyrkube.KubeAPIClient(
                    config['environment'],
                    config['namespace'],
                    config['domain'])
                self.app.log.debug('Got kubernetes api client: %s', kube)
                return kube
            except pyrkube.KubeConfigNotFound:
                pass
        elif name == 'caps':
            pycaps = try_import('pycaps')
            if not pycaps:
                raise ImportError(
                    'You need to install pycaps to use the caps extension')
            return pycaps.get_caps()

    # def _get_config(self):
    #     config = self.app.config.get_section_dict('tmpld')
    #     self.app.log.debug('Using configuration: %s', config)
    #     return config

    def _get_extensions(self):
        config = self.app.config.get_section_dict('tmpld')
        extensions = {name: self._get_ext(name, config)
                      for name in config['exts']}
        self.app.log.debug('Got extensions: %s', extensions)
        return extensions

    def _get_template_environment(self, extensions):
        strict = self.app.config.get_section_dict('tmpld')['strict']
        template_dirs = util.get_template_dirs(self.app.pargs.templates)
        template_env = environment.TemplateEnvironment(
            self.app.pargs.data, extensions, template_dirs, strict=strict
        )
        self.app.log.debug('Got Jinja environment: %s', template_env)
        return template_env

    def _get_templates(self):
        templates = self.app.pargs.templates
        self.app.log.debug('Got templates: %s', templates)
        return templates

    def render_templates(self, environment, templates):
        for tmpl in templates:
            self.app.log.debug('Rendering: %s > %s', tmpl.file, tmpl.target)
            self.app.render('Rendering: %s > %s\n' % (tmpl.file, tmpl.target))
            environment.render(tmpl)
            self.app.render(tmpl.print(as_string=True))
            tmpl.save()

    @expose(hide=True)
    def default(self):
        self.app.log.debug('CLI arguments: %s', self.app.pargs)
        config = self.app.config.get_section_dict('tmpld')
        self.app.log.debug('Using configuration: %s', config)
        # config = self._get_config()
        extensions = self._get_extensions()
        template_env = self._get_template_environment(extensions)
        templates = self._get_templates()
        self.render_templates(template_env, templates)


class TmpldApp(CementApp):
    class Meta:
        label = 'tmpld'
        description = 'Renders jinja2 templates w/ Kubernetes API objects.'
        base_controller = TmpldController
        log_handler = handlers.KubeWaitLogHandler
        output_handler = handlers.StandardErrorHandler
        config_defaults = {
            'tmpld': dict(
                environment=os.getenv('TMPLD_ENVIRONMENT', 'production'),
                exts=os.getenv('TMPLD_EXTENSIONS', 'kube').split(','),
                namespace=os.getenv('KUBE_NAMESPACE', 'default'),
                domain=os.getenv('KUBE_DOMAIN', 'cluster.local'),
                strict=util.parse_bool(os.getenv('TMPLD_STRICT_CHECK', 'false'))
            ),
            'log.kwlogging': dict(
                level=os.getenv('TMPLD_LOG_LEVEL', 'WARNING')
            )
        }


def main(args=None):
    args = args or sys.argv[1:]
    with TmpldApp(argv=args) as app:
        app.run()
