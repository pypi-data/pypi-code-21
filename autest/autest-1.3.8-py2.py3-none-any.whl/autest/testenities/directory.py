from __future__ import absolute_import, division, print_function
import os

from autest.common.constructor import call_base, smart_init
from autest.core.testenity import TestEnity
import autest.testers as testers
from autest.core.testerset import TesterSet


@smart_init
class Directory(TestEnity):
    '''
    Allows us to test for a file. We can test for existance
    '''

    @call_base(TestEnity=("runable", ))
    def __init__(self, runable, name, exists=True, runtime=True):
        self.__name = name
        self.__runtime = runtime

        # setup testables
        # exists
        self._Register(
            "Directory.{0}.Exists".format(self.__name),
            TesterSet(
                testers.DirectoryExists,
                self,
                self._Runable.FinishedEvent,
                converter=bool,
                description_group="{0} {1}".format("directory", self.__name)),
            ["Exists"])

        self.Exists = exists

    def __str__(self):
        return self.Name

    def GetContent(self, eventinfo):
        return self.AbsPath, ""

    @property
    def AbsPath(self):
        '''
        The absolute path of the file, runtime value
        '''
        if self.__runtime:
            return self.AbsRunTimePath
        return self.AbsTestPath

    @property
    def AbsRunTimePath(self):
        '''
        The absolute path of the file, based on Runtime sandbox location
        '''
        return os.path.normpath(
            os.path.join(self._RootRunable.RunDirectory, self.Name))

    @property
    def AbsTestPath(self):
        '''
        The absolute path of the file, based on directory relative form the test file location
        '''
        return os.path.normpath(
            os.path.join(self._RootRunable.TestDirectory, self.Name))

    @property
    def Name(self):
        return self.__name
