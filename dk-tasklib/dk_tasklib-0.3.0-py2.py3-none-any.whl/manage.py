# -*- coding: utf-8 -*-
import sys
import os

from dkfileutils.path import Path
from dkfileutils.pfind import pfind
from dkfileutils.changed import changed, Directory
from dktasklib.wintask import task
from invoke import run
from .utils import cd, env, find_pymodule
from .package import Package


DEFAULT_SETTINGS_MODULE = 'settings'


@task
def manage(ctx, cmd, settings=None, manage_path=None, venv=None):
    """Run manage.py with `settings` in a separate process.
    """
    settings = settings or DEFAULT_SETTINGS_MODULE
    with env(DJANGO_SETTINGS_MODULE=settings):
        if manage_path is None:
            settings_dir = find_pymodule(settings)
            manage_path = Path(pfind(settings_dir, 'manage.py')).dirname()

        with cd(manage_path):
            # print "MANAGE_PATH:", manage_path
            # print "CWD:", os.getcwd()
            # run('python -c "import sys;print sys.path"')
            # run('vex dev python -c "import sys;print chr(10).join(sys.path)"')
            # run("python -c \"import sys;print '\n'.join(sys.path)\"")

            call = "python manage.py {cmd}"
            if venv:
                call = "vex {venv} python manage.py {cmd} --traceback"

            run(call.format(venv=venv, cmd=cmd))


@task
def collectstatic(ctx, settings=None, venv=None, clobber=False, force=False):
    "Run collectstatic with settings from package.json ('django_settings_module')"
    if not hasattr(ctx, 'pkg'):
        ctx.pkg = Package()

    if not (force or Directory(ctx.pkg.django_static).changed()):
        print "Skipping collectstic: no changes to static dir."
        return

    if not clobber:
        # check that we don't overwrite versioned resources
        changed_versioned_resources = False
        static = Path(os.environ['SRV']) / 'data' / 'static'
        for fname in ctx.pkg.django_static.glob('**/*\d+.min.*'):
            pubname = static / fname.relpath(ctx.pkg.django_static)
            if pubname.exists():
                # print 'checking:', pubname
                if pubname.open('rb').read() != fname.open('rb').read():
                    changed_versioned_resources = True
                    print
                    print "ERROR: versioned file has changes:"
                    print "  contents of:      ", fname
                    print "  is different from:", pubname
                    print
        if changed_versioned_resources:
            print "Exiting due to changes in versioned resources. " \
                  "You should probably revert the changes and create " \
                  "a new version."
            sys.exit(1)

    try:
        settings = settings or ctx.pkg.django_settings_module
    except AttributeError:
        settings = DEFAULT_SETTINGS_MODULE
    print "using settings:", settings, 'venv:', venv
    manage(ctx, "collectstatic --noinput", settings=settings, venv=venv)
    # record changes made by collectstatic
    changed(ctx.pkg.django_static)
