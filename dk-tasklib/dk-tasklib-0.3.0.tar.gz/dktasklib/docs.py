# -*- coding: utf-8 -*-

import os
import textwrap
import webbrowser
from os.path import join

from dkfileutils.changed import changed
from dkfileutils.path import Path
from dktasklib.wintask import task
from invoke import Collection

from dktasklib import concat
from dktasklib import Package


@task(name='clean')
def _clean(ctx):  # Underscored func name to avoid shadowing kwargs in build()
    """Nuke docs build target directory so next build is clean.
    """
    if 'pkg' not in ctx:
        ctx.pkg = Package()
    builddir = ctx.pkg.root / 'build' / 'docs'
    if os.path.exists(builddir) and len(os.listdir(builddir)) > 0:
        ctx.run("rm -rf {0}/*".format(builddir))


# Ditto
@task(name='browse')
def _browse(ctx):  # pragma: nocover
    """Open build target's index.html in a browser (using the :py:mod:`webbrowser` module).
    """
    index = join(ctx.pkg.root / 'build' / 'docs' / 'index.html')
    webbrowser.open_new(index)


@task
def make_api_docs(ctx, prefix='', force=False):
    """Run sphinx-apidoc to write autodoc documentation to `docs/api/*`
    """
    ctx.run("rm -rf {pkg.docs}/api".format(pkg=ctx.pkg))
    ctx.run("sphinx-apidoc -o {pkg.docs}/api {pkg.source} {pkg.source}/migrations {pkg.source}/models {pkg.source}/models.py".format(pkg=ctx.pkg))
    if prefix:
        for fname in (ctx.pkg.docs / 'api').glob('*.rst'):
            f = Path(fname)
            lines = f.read().split('\n')
            for i, line in enumerate(lines):
                lines[i] = line.replace(ctx.pkg.name, prefix + ctx.pkg.name)
                if i > 0 and len(set(line)) == 1 and len(line) < len(lines[i-1]):
                    lines[i] = line[0] * len(lines[i-1])
            f.write('\n'.join(lines))
            pre, pkgname, post = fname.rpartition(ctx.pkg.name)
            if pkgname and os.path.sep not in post:
                f.rename(pre + prefix + pkgname + post)

    concat.copy(ctx, ctx.pkg.docs / 'api' / '*', ctx.pkg.docs)
    ctx.run("rm -rf {pkg.docs}/api".format(pkg=ctx.pkg))

    if ".. include:: modules.rst" not in open(ctx.pkg.docs / 'index.rst').read():
        print textwrap.dedent("""\
        WARNING: you need to include the following in docs/index.rst

            .. include:: modules.rst

        """)


@task(default=True, help={
    'opts': "Extra sphinx-build options/args",
    'prefix': "Module prefix, for submodules",
    'clean': "Remove build tree before building",
    'browse': "Open docs index in browser after building",
    'warn': "Build with stricter warnings/errors enabled",
    'builder': "Builder to use, defaults to html",
    'force': "Force re-reading of all files (ignore cache)",
})
def build(ctx, clean=False, browse=False, warn=False,
          builder='html',
          force=False,
          opts="", prefix=''):
    """
    Build the project's Sphinx docs.
    """
    # import pdb;pdb.set_trace()
    if not force and not changed(ctx.pkg.docs):
        print """
        No changes detected in {}, add --force to build docs anyway.
        """.format(ctx.pkg.docs)
        return  # should perhaps check if code has changed too? (autodoc)

    if clean:
        _clean(ctx)
    make_api_docs(ctx, force=force, prefix=prefix)

    if opts is None:  # pragma: nocover
        opts = ""
    opts += " -b %s" % builder
    if warn:
        opts += " -n -W"
    if force:
        opts += " -a -E"
    cmd = "sphinx-build {opts} {ctx.pkg.docs} {ctx.pkg.root}/build/docs".format(opts=opts, ctx=ctx)
    dj_settings = ctx.pkg.get('django_settings_module', "")
    if dj_settings:
        os.environ['DJANGO_SETTINGS_MODULE'] = dj_settings
    ctx.run(cmd)
    if browse:  # pragma: nocover
        _browse(ctx)


@task
def tree(ctx):
    """Display the docs tree.
    """
    ignore = ".git|*.pyc|*.swp|dist|*.egg-info|_static|_build|_templates"
    ctx.run('tree -Ca -I "{0}" {1}'.format(ignore, ctx.pkg.docs))


# Vanilla/default/parameterized collection for normal use
ns = Collection('docs', _clean, _browse, build, tree)
ns.configure({
    'docs': {
        'source': 'docs',
        'builddir': join('build', 'docs'),
        'target_file': 'index.html',
    }
})
