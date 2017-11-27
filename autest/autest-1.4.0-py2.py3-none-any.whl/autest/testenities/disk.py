from __future__ import absolute_import, division, print_function
import os

import autest.glb as glb
from autest.common.constructor import call_base, smart_init
from autest.core.testenity import TestEnity
from .directory import Directory
from .file import File
import hosts.output as host


@smart_init
class Disk(TestEnity):
    '''
    allows use to define what kind of disk based test we want to do
    '''

    @call_base(TestEnity=("runable", ))
    def __init__(self, runable):
        self.__files = {}
        self.__dirs = {}

    def File(self,
             name,
             exists=None,
             size=None,
             content=None,
             execute=None,
             id=None,
             runtime=True,
             typename=None):
        if typename is None:
            ext = os.path.splitext(name)
            # auto select file based on ext
            cls = glb.FileExtMap.get(ext, File)
        else:
            # select file based on typename
            cls = glb.FileTypeMap.get(typename, File)

        tmp = cls(self._Runable, name, exists, size, content, execute, runtime)

        if name in self.__files:
            host.WriteWarning("Overriding file object {0}".format(name))
        self.__files[name] = tmp
        if id:
            self.__dict__[id] = tmp
        return tmp

    def Directory(self, name, exists=None, id=None, runtime=True):
        tmp = Directory(self._Runable, name, exists, runtime)
        if name in self.__dirs:
            host.WriteWarning("Overriding directory object {0}".format(name))
        self.__dirs[name] = tmp
        if id:
            self.__dict__[id] = tmp
        return tmp


import autest.api
autest.api.AddTestEnityMember(Disk)
