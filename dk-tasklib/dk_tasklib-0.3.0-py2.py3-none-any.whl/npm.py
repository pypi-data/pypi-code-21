# -*- coding: utf-8 -*-
import shlex
import subprocess

# from invoke import run
from dktasklib.executables import exe
from .utils import null, win32


def npm(cmdline):
    npm_exe = exe.find('npm', requires=['nodejs'])
    return subprocess.check_output("npm " + cmdline, shell=True).decode('u8')

#
#
# def cmd2args(cmd):
#     if isinstance(cmd, basestring):
#         return cmd if win32 else shlex.split(cmd)
#         # return cmd.split() if win32 else shlex.split(cmd)
#     return cmd
#
#
# class RunError(Exception):
#     def __init__(self, cmd, errno):
#         self.errno = errno
#         super(RunError, self).__init__(cmd, errno)
#
#
# def _run(cmd):
#     popen = subprocess.Popen(
#         cmd2args(cmd),
#         stdout=subprocess.PIPE,
#         stderr=subprocess.STDOUT,
#         cwd=None,
#         shell=win32
#     )
#
#     for line in iter(popen.stdout.readline, ""):
#         # print ">>", line
#         yield line
#
#     exitcode = popen.wait()
#     if exitcode != 0:
#         raise RunError(cmd, exitcode)
#
#
# class run(object):
#     def __init__(self, cmd):
#         self.return_code = 0
#         try:
#             self.output = '\n'.join(line for line in _run(cmd))
#         except RunError as e:
#             self.return_code = e.errno


def global_package(pkgname):
    """Check if an npm package is installed globally.
    """
    try:
        # this is the 'correct' way, but it's increadably slow (4+ secs)
        npm('ls -g --depth 0 ' + pkgname)
        return True
    except subprocess.CalledProcessError:
        return False
