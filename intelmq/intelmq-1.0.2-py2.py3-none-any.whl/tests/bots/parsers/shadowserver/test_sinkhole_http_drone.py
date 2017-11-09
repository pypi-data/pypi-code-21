# -*- coding: utf-8 -*-

import os
import unittest

import intelmq.lib.test as test
import intelmq.lib.utils as utils
from intelmq.bots.parsers.shadowserver.parser import ShadowserverParserBot

with open(os.path.join(os.path.dirname(__file__), 'sinkhole_http_drone.csv')) as handle:
    EXAMPLE_FILE = handle.read()
EXAMPLE_LINES = EXAMPLE_FILE.splitlines()
import sys
print(type(EXAMPLE_LINES[2]), file=sys.stderr)
print(EXAMPLE_LINES[2][51:], file=sys.stderr)

with open(os.path.join(os.path.dirname(__file__),
                       'sinkhole_http_drone_RECONSTRUCTED.csv')) as handle:
    RECONSTRUCTED_FILE = handle.read()
RECONSTRUCTED_LINES = RECONSTRUCTED_FILE.splitlines()

EXAMPLE_REPORT = {"feed.name": "ShadowServer Sinkhole HTTP drone",
                  "raw": utils.base64_encode(EXAMPLE_FILE),
                  "__type": "Report",
                  "time.observation": "2015-01-01T00:00:00+00:00",
                  }
EVENTS = [{'__type': 'Event',
           'feed.name': 'ShadowServer Sinkhole HTTP drone',
           'classification.type': 'botnet drone',
           'classification.identifier': 'botnet',
           'classification.taxonomy': 'malicious code',
           'classification.type': 'botnet drone',
           'destination.asn': 174,
           'destination.geolocation.cc': 'US',
           'destination.ip': '198.51.100.125',
           'destination.port': 80,
           'extra.url': 'GET /search?q=1349 HTTP/1.0',
           'extra.sic': 874899,
           'extra.naics': 541690,
           'extra.http_host': '198.51.100.67',
           'extra.user_agent': 'Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0)',
           'feed.name': 'ShadowServer Sinkhole HTTP drone',
           'malware.name': 'downadup',
           'raw': utils.base64_encode(
               '\n'.join([RECONSTRUCTED_LINES[0],
                          RECONSTRUCTED_LINES[1], ''])),
           'protocol.transport': 'tcp',
           'source.asn': 3320,
           'source.geolocation.cc': 'DE',
           'source.ip': '198.51.100.152',
           'source.port': 57496,
           'source.reverse_dns': '198-51-100-152.example.net',
           'time.source': '2016-07-24T00:00:00+00:00',
           'time.observation': '2015-01-01T00:00:00+00:00'},
          {'__type': 'Event',
           'classification.identifier': 'botnet',
           'classification.taxonomy': 'malicious code',
           'classification.type': 'botnet drone',
           'destination.asn': 28753,
           'destination.geolocation.cc': 'DE',
           'destination.ip': '178.162.217.107',
           'destination.port': 80,
           'extra.url': '\\x16\\x03\\x01\\x00z\\x01\\x00\\x00v\\x03\\x01Y\\x10?\\x08?;??B???]?|i?H?t??.:?\\x07b?????\\x00\\x00\\x1c?\\x14?\\x13\\x009\\x003\\x005\\x00/?',
           'extra.naics': 518210,
           'extra.os.name': 'Windows',
           'extra.os.version': '7 or 8',
           'extra.sic': 737415,
           'feed.name': 'ShadowServer Sinkhole HTTP drone',
           'malware.name': 'sinkhole',
           'protocol.transport': 'tcp',
           'raw': utils.base64_encode(
               '\n'.join([RECONSTRUCTED_LINES[0],
                          RECONSTRUCTED_LINES[2], ''])),
           'source.asn': 1901,
           'source.geolocation.cc': 'AT',
           'source.ip': '193.81.219.120',
           'source.port': 54465,
           'time.source': '2017-05-08T18:50:45+00:00'}]


class TestShadowserverParserBot(test.BotTestCase, unittest.TestCase):
    """
    A TestCase for a ShadowserverParserBot.
    """

    @classmethod
    def set_bot(cls):
        cls.bot_reference = ShadowserverParserBot
        cls.default_input_message = EXAMPLE_REPORT
        cls.sysconfig = {'feedname': 'Sinkhole-HTTP-Drone'}

    def test_event(self):
        """ Test if correct Event has been produced. """
        self.run_bot()
        for i, EVENT in enumerate(EVENTS):
            self.assertMessageEqual(i, EVENT)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
