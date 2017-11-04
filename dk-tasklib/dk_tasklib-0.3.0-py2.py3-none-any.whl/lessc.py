# -*- coding: utf-8 -*-
import os
from dktasklib.wintask import task
from .rule import BuildRule
from .commands import Command
from dkfileutils.changed import Directory
from dkfileutils.path import Path
from invoke import Collection
from . import urlinliner
from .concat import copy
from .environment import env
from .utils import fmt, switch_extension, message
from .version import get_version
from .upversion import UpdateTemplateVersion

lessc = Command('lessc', '{opts} {src} {dst}',
                requirements=('nodejs', 'npm', 'lessc'))


BOOTSTRAP = Path(os.environ.get('SRV', '')) / 'lib' / 'bootstrap' / 'less'


@task(
    default=True,
    name='build_less',
    help={
        'version': "one of pkg|hash|svn",
    }
)
class LessRule(BuildRule):
    """Build a ``.less`` file into a versioned and minified ``.css`` file.
    """

    bootstrap_src = BOOTSTRAP

    def __init__(self, *args, **kw):
        self.after = [UpdateTemplateVersion(
            kw.pop('import_fname',
                   '{pkg.source}/templates/{pkg.name}/{pkg.name}-css.html')
        )]
        super(LessRule.body, self).__init__(*args, **kw)

    def __call__(self,
                 src='{pkg.source}/less/{pkg.name}.less',
                 dst='{pkg.source}/static/{pkg.name}/css/{pkg.name}-{version}.min.css',
                 version='pkg',
                 bootstrap=True,
                 force=False,
                 **kw):
        c = env(self.ctx)
        source = Path(fmt(src, c))
        dest = Path(fmt(dst, c))

        if not source.exists():
            print "Missing source:", source, '(skipping)'
            return

        for fname in source.dirname().glob("*.inline"):
            urlinliner.inline(self.ctx, fname)

        if not force and not Directory(source.dirname()).changed(glob='**/*.less'):
            print "No changes: {input_dir}/{glob}, add --force to build.".format(
                input_dir=source.dirname(), glob='**/*.less')
            return

        path = kw.pop('path', [])
        if bootstrap:
            path.append(self.bootstrap_src)

        cssname = dest.relpath().format(version=get_version(self.ctx, source, version))
        lessc(
            self.ctx,
            src=source.relpath(),
            dst=cssname,
            include_path=path,
            strict_imports=True,
            inline_urls=False,
            autoprefix="last 4 versions",
            clean_css="-b --s0 --advanced",
        )

        with message("Creating copy without version number.."):
            copy(  # create a copy without version number too..
                self.ctx,
                cssname,
                Path(cssname).dirname() / switch_extension(source.basename(), '.css'),
                force=True
            )
        return cssname


ns = Collection('lessc', LessRule)
ns.configure({
    'force': False,
    'pkg': {
        'root': '<package-root-directory>',
        'name': '<package-name>',
        'source': '<source-dir>',
        'version': '<version-string>',
    },
    'bootstrap': {
        'src': os.path.join(os.environ.get('BOOTSTRAPSRC', ''), 'less'),
    },
    'lessc': {
        'use_bootstrap': False,
        'build_dir': 'build/css',
        'input_dir': '{pkg.source}/less',
        'input_fname': '{pkg.name}.less',
        'output_dir': '{pkg.source}/static/{pkg.name}/css/',
        'output_fname': '{pkg.name}.css',
    }
})
