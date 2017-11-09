# -*- coding: utf-8 -*-
import os
import unittest

import intelmq.lib.utils as utils
import intelmq.lib.test as test
from intelmq.bots.parsers.generic.parser_csv import GenericCsvParserBot


#with open(os.path.join(os.path.dirname(__file__), 'sample_report.csv')) as handle:
#    SAMPLE_FILE = handle.read()
SAMPLE_FILE = "2015-12-14T04:19:00\t\x00"
SAMPLE_SPLIT = SAMPLE_FILE.splitlines()

EXAMPLE_REPORT = {"feed.name": "Sample CSV Feed",
                  "raw": utils.base64_encode(SAMPLE_FILE),
                  "__type": "Report",
                  "time.observation": "2015-01-01T00:00:00+00:00",
                  }
EXAMPLE_EVENT = {"feed.name": "Sample CSV Feed",
                 "__type": "Event",
                 "time.source": "2015-12-14T04:19:00+00:00",
                 "classification.type": "malware",
                 "time.observation": "2015-01-01T00:00:00+00:00",
                 }

class TestGenericCsvParserBot(test.BotTestCase, unittest.TestCase):
    """
    A TestCase for a GenericCsvParserBot.
    """

    @classmethod
    def set_bot(cls):
        cls.bot_reference = GenericCsvParserBot
        cls.default_input_message = EXAMPLE_REPORT
        cls.sysconfig = {"columns": ["time.source",],
                         "delimiter": "\t",
                         "type": "malware",
                         "default_url_protocol": "http://"}

    def test_event(self):
        """ Test if correct Event has been produced. """
        self.run_bot()
#        self.assertMessageEqual(0, EXAMPLE_EVENT)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
