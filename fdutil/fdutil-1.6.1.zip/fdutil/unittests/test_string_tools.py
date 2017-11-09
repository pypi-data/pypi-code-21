import unittest

from fdutil import string_tools


class TestStringTools(unittest.TestCase):

    def setUp(self):
        self.longest_word = u'Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch'
        self.lorem_ipsum_short = u'Lorem ipsum dolor sit amet, consectetur adipiscing elit'
        self.lorem_ipsum = (u'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt'
                            u' ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation '
                            u'ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in '
                            u'reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur '
                            u'sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim '
                            u'id est laborum.')

    def tearDown(self):
        pass

    # limit_word_length
    def test_limit_word_length(self):

        split_9 = [
            u'Llanfair-',
            u'pwllgwyn-',
            u'gyllgoge-',
            u'rychwyrn-',
            u'drobwlll-',
            u'lantysil-',
            u'iogogogo-',
            u'ch'
        ]

        self.assertEqual(string_tools.limit_word_length(self.longest_word, 9), split_9)
        self.assertEqual(string_tools.limit_word_length(self.longest_word, 60), [self.longest_word])

    # limit_word_lengths
    def test_limit_word_lengths(self):

        words = self.lorem_ipsum_short.split(u' ')

        split_9 = [
            u'Lorem',
            u'ipsum',
            u'dolor',
            u'sit',
            u'amet,',
            u'consecte-',
            u'tur',
            u'adipisci-',
            u'ng',
            u'elit'
        ]

        self.assertEqual(string_tools.limit_word_lengths(words, 12), words)
        self.assertEqual(string_tools.limit_word_lengths(words, 9), split_9)

    # make_multi_line_list
    def test_make_multi_line_list(self):

        split_80 = [u'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor',
                    u'incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis',
                    u'nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
                    u'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu',
                    u'fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in',
                    u'culpa qui officia deserunt mollit anim id est laborum.']

        self.assertEqual(string_tools.make_multi_line_list(self.lorem_ipsum, 80), split_80)

    def test_make_multi_line_list_2_lines_input(self):

        double_line = u'{l}\n{l}'.format(l=self.lorem_ipsum_short)

        split_30 = [u'Lorem ipsum dolor sit amet,',
                    u'consectetur adipiscing elit',
                    u'Lorem ipsum dolor sit amet,',
                    u'consectetur adipiscing elit']

        self.assertEqual(string_tools.make_multi_line_list(double_line, 30), split_30)

    # make_multi_line
    def test_make_multi_line(self):

        split_80 = (u'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor\n'
                    u'incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis\n'
                    u'nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.\n'
                    u'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu\n'
                    u'fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in\n'
                    u'culpa qui officia deserunt mollit anim id est laborum.')

        self.assertEqual(string_tools.make_multi_line(self.lorem_ipsum, 80), split_80)

    # make_multi_line_conversion
    def test_make_multi_line_conversion(self):
        expected_keys = [u'converter', u'maximum_width']
        conversion = string_tools.make_multi_line_conversion()

        for key in expected_keys:
            self.assertIn(key, conversion)

    # multiple_replace
    def test_multiple_replace(self):
        self.assertEqual(string_tools.multiple_replace(u"Do you like coffee? No, I prefer tea.",
                                                       {u'coffee': u'tea',
                                                        u'tea':    u'coffee',
                                                        u'like':   u'prefer'}),
                         u"Do you prefer tea? No, I prefer coffee.")
