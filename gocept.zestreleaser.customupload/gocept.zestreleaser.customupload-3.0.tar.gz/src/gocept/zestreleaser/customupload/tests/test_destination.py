from six import StringIO
from six.moves import configparser
import gocept.zestreleaser.customupload.upload
import unittest


class DestinationTest(unittest.TestCase):

    def choose(self, package, config_text):
        config = configparser.ConfigParser()
        config.readfp(StringIO(config_text))
        return gocept.zestreleaser.customupload.upload.choose_destination(
            package, config, 'gocept.zestreleaser.customupload')

    def test_no_dest_defined(self):
        self.assertEqual(None, self.choose('my.package', ''))

    def test_no_dest_for_package(self):
        config = """
[gocept.zestreleaser.customupload]
other.package = other.dest
        """
        self.assertEqual(None, self.choose('my.package', config))

    def test_exact_match(self):
        config = """
[gocept.zestreleaser.customupload]
my.package = my.dest
other.package = other.dest
        """
        self.assertEqual('my.dest', self.choose('my.package', config))
        self.assertEqual('other.dest', self.choose('other.package', config))

    def test_prefix_match(self):
        config = """
[gocept.zestreleaser.customupload]
my = my.dest
        """
        self.assertEqual('my.dest', self.choose('my.package', config))

    def test_longest_match_wins(self):
        config = """
[gocept.zestreleaser.customupload]
my = my.dest.is.much.longer
my.special = special.dest
        """
        self.assertEqual('special.dest', self.choose('my.special', config))

    def test_comparison_is_case_insensitive(self):
        config = """
[gocept.zestreleaser.customupload]
my.package = my.dest
        """
        self.assertEqual('my.dest', self.choose('My.Package', config))
