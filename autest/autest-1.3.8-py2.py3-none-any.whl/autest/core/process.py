from __future__ import absolute_import, division, print_function
from autest.common.constructor import call_base, smart_init
import hosts.output as host

from .runable import Runable
from .order import Order
from .item import Item
from . import setup

import os


@smart_init
class Process(Runable, Order, Item):
    __slots__ = []

    @call_base(Runable=("runable",), Order=(), Item=(None, "name"))
    def __init__(self, runable, name, cmdstr=None, use_shell=None):
        self.__cmdstr = cmdstr
        self.__use_shell = use_shell
        self.__streams = object()

        # will want to refactor setup later
        self.__setup = setup.Setup(self)

    @property
    def Setup(self):
        return self.__setup

    @property
    def Name(self):
        return self._ID

    @property
    def StreamOutputDirectory(self):
        return os.path.join(self._RootRunable.RunDirectory, "_tmp_{0}_{1}_{2}".format(self._RootRunable._ID,
                                                                                      self._ParentRunable._ID,
                                                                                      self._ID))

    @property
    def Command(self):
        return self.__cmdstr

    @Command.setter
    def Command(self, value):
        value = value.replace('/', os.sep)
        self.__cmdstr = value

    # need to remember if this case is needed
    # ///////////////////////
    @property
    def RawCommand(self):
        return self.__cmdstr

    @RawCommand.setter
    def RawCommand(self, value):
        self.__cmdstr = value
    # ////////////////////////

    @property
    def ForceUseShell(self):
        return self.__use_shell

    @ForceUseShell.setter
    def ForceUseShell(self, val):
        self.__use_shell = bool(val)

    @property
    def StartupTimeout(self):
        return self.__startup_timeout

    @StartupTimeout.setter
    def StartupTimeout(self, val):
        self.__startup_timeout = float(val)

    @property
    def _ChildRunables(self):
        return self.Setup._Items

    @property
    def TestDirectory(self):
        return self._RootRunable.TestDirectory

    @property
    def TestFile(self):
        return self._RootRunable.TestFile

    @property
    def TestRoot(self):
        return self._RootRunable.TestRoot

    @property
    def RunDirectory(self):
        return self._RootRunable.RunDirectory
