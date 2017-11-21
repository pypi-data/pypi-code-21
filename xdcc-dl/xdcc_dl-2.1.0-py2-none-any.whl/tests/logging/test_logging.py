u"""
Copyright 2016-2017 Hermann Krumrey

This file is part of xdcc-dl.

xdcc-dl is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

xdcc-dl is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with xdcc-dl.  If not, see <http://www.gnu.org/licenses/>.
"""

# imports
from __future__ import with_statement
from __future__ import absolute_import
import os
import unittest
from xdcc_dl.logging.Logger import Logger
from xdcc_dl.logging.LoggingTypes import LoggingTypes
from io import open


class UnitTests(unittest.TestCase):

    def setUp(self):
        self.logfile = os.path.join(os.getcwdu(), u"logging_log")
        self.messages = [
            (u"Invisible", LoggingTypes.INVISIBLE),
            (u"Default", LoggingTypes.DEFAULT),
            (u"WHOIS_SEND", LoggingTypes.WHOIS_SEND),
            (u"PRIVATE_NOTICE", LoggingTypes.PRIVATE_NOTICE),
            (u"MESSAGE_OF_THE_DAY", LoggingTypes.MESSAGE_OF_THE_DAY),
            (u"EVENT", LoggingTypes.EVENT),
            (u"CHANNEL_KICK", LoggingTypes.CHANNEL_KICK)
        ]

    def tearDown(self):
        if os.path.isfile(self.logfile):
            os.remove(self.logfile)

    def test_verbosity(self, ignore_verbosity=False):

        for verbosity_level in xrange(0, 7):

            logger = Logger(verbosity_level, self.logfile, ignore_verbosity)

            for message in self.messages:
                logger.log(message[0], message[1])

            with open(self.logfile, u'r') as f:
                log = f.read().rstrip().lstrip()

            if ignore_verbosity:
                self.assertEqual(len(log.split(u"\n")), 7)
            else:
                self.assertEqual(len(log.split(u"\n")), verbosity_level + 1)

            os.remove(self.logfile)

    def test_ignore_verbosity(self):
        self.test_verbosity(True)

    def test_logger_with_existing_logfile(self):

        with open(self.logfile, u'w') as f:
            f.write(u"Testing Logger\n")

        logger = Logger(1, self.logfile)
        logger.log(u"Test")

        with open(self.logfile, u'r') as f:
            self.assertEqual(f.read(), u"Testing Logger\nTest\n")
