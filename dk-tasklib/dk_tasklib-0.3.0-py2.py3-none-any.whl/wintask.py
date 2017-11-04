# -*- coding: utf-8 -*-
import os
import sys
import invoke

try:
    from invoke import ctask as _task
except ImportError:
    from invoke import task as _task

if invoke.__version_info__ < (0, 22):
    _should_patch = True
elif invoke.__version_info__ < (0, 22 + 22-13):  # broken since 13..
    from invoke import run as _run
    try:
        _run('rem')
        _should_patch = False
    except WindowsError:
        _should_patch = True


if _should_patch:
    # https://github.com/pyinvoke/invoke/pull/407
    from invoke import Context

    if not getattr(Context, '_patched', False):
        Context._patched = True
        _orig_run = Context.run

        def run(self, command, **kwargs):
            if sys.platform == 'win32':
                kwargs['shell'] = os.environ['COMSPEC']
            return _orig_run(self, command, **kwargs)

        Context.run = run

task = _task


__all__ = ['task']
