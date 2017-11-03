from __future__ import absolute_import, division, print_function

import autest.testers as testers
from autest.common.constructor import call_base, smart_init
from autest.core.testenity import TestEnity
from autest.core.testerset import TesterSet

from .file import File


@smart_init
class Streams(TestEnity):
    @call_base(TestEnity=("runable", ))
    def __init__(self, runable):
        # setup testers
        STREAMS = (  # std streams
            ('stdout', 'Streams.{0}.stdout', 'StdOutFile'),
            ('stderr', 'Streams.{0}.stderr', 'StdErrFile'),
            # filtered streams
            ('All', 'Streams.{0}.All', 'AllFile'),
            #('Message', 'Streams.{0).Message', 'MessageFile'), Not sure
            # how to filter this our from stdout
            ('Warning', 'Streams.{0}.Warning', 'WarningFile'),
            ('Error', 'Streams.{0}.Error', 'ErrorFile'),
            ('Debug', 'Streams.{0}.Debug', 'DebugFile'),
            ('Verbose', 'Streams.{0}.Verbose', 'VerboseFile'), )

        for name, eventname, testValue in STREAMS:
            # tweak to add property for all testable events
            self._Register(
                eventname.format(self._Runable.Name),
                TesterSet(
                    testers.GoldFile,
                    testValue,
                    self._Runable.FinishedEvent,
                    converter=lambda x: File(self._Runable, x, runtime=False),
                    description_group="{0} {1}".format("Stream", name)
                ),
                name
            )


import autest.api
from .process import Process
autest.api.AddTestEnityMember(Streams, classes=[Process])
