#-*- coding: utf-8 -*-
"""
@file
@brief Module *pyense*.
Recurrent needs for teachings
turned into functions.
"""
import sys


__version__ = "1.2"
__author__ = "Xavier Dupré"
__github__ = "https://github.com/sdpython/pyenbc"
__url__ = "http://www.xavierdupre.fr/app/pyenbc/helpsphinx/index.html"
__license__ = "MIT License"


def _setup_hook(add_print=False, unit_test=False):
    """
    if this function is added to the module,
    the help automation and unit tests call it first before
    anything goes on as an initialization step.
    It should be run in a separate process.

    @param      add_print       print *Success: _setup_hook*
    @param      unit_test       used only for unit testing purpose
    """
    # we can check many things, needed module
    # any others things before unit tests are started
    if add_print:
        print("Success: _setup_hook")


def check(log=False):
    """
    Checks the library is working.
    It raises an exception.

    @param      log     if True, display information, otherwise
    @return             0 or exception
    """
    return True


def load_ipython_extension(ip):
    """
    to allow the call ``%load_ext pyensae``

    @param      ip      from ``get_ipython()``
    """
    from .remote.magic_remote_ssh import register_magics_ssh
    try:
        from .remote.magic_azure import register_azure_magics
        az = True
    except ImportError as e:
        if "azure" in str(e):
            az = False
        else:
            raise e

    register_magics_ssh(ip)
    if az:
        register_azure_magics(ip)
