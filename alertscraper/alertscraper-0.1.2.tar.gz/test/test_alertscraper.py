'''
Tests for `alertscraper` module.
'''
from alertscraper import alertscraper

# TODO add more tests


class TestParseLines:
    def test_parse_lines_simple(self):
        assert alertscraper.parse_lines(['stuff|whatever|thing']) == ['stuff']
