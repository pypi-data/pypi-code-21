# -*- coding: utf-8 -*-
import unittest

from pynlple.exceptions import DataSourceException
from pynlple.processing.dictionary import FileFolderTokenMapping
from ..module import abs_path as path

from ..processing.dictionary import DictionaryLookUp, DictionaryBasedTagger


class TaggerTest(unittest.TestCase):

    def setUp(self):
        self.mappings = [
            ('a b c', 'class1'),
            ('a b', 'class11'),
            ('a c', 'class1'),
            ('b c', 'class11'),
            ('a a a', 'class2'),
            ('a a', 'class21'),
            ('b b b', 'class2'),
            ('c c c', 'class2'),
            ('a b c d', 'class3'),
            ('a b c e', 'class3'),
        ]
        self.dictionary = DictionaryLookUp(self.mappings)

    def test_should_result_be_empty(self):
        tagger = DictionaryBasedTagger(DictionaryLookUp([]))
        tokens = 'a b c a b a a a c c c a b c d a b c e'.split()
        self.assertEqual(0, len(tagger.get_tagged_entities(tokens)))

    def test_should_match_one_result(self):
        tagger = DictionaryBasedTagger(self.dictionary)
        tokens = 'a c a b'.split()
        self.assertEqual([(0, 2, 'class1'), (2, 4, 'class11')], tagger.get_tagged_entities(tokens))

    def test_should_match_some_results(self):
        tagger = DictionaryBasedTagger(self.dictionary)
        tokens = 'c c c a'.split()
        self.assertEqual((0, 3, 'class2'), tagger.get_tagged_entities(tokens)[0])

    def test_should_match_many_longer_parts_results(self):
        tagger = DictionaryBasedTagger(self.dictionary)
        tokens = 'a b c b b b a b c e a a a'.split()
        self.assertEqual([(0, 3, 'class1'),
                          (3, 6, 'class2'),
                          (6, 10, 'class3'),
                          (10, 13, 'class2')],
                         tagger.get_tagged_entities(tokens, False))

    def test_should_match_all_and_short_parts_results(self):
        tagger = DictionaryBasedTagger(self.dictionary)
        tokens = 'a b c b b b a b c e a a a'.split()
        self.assertEqual({(0, 3, 'class1'),
                          (0, 2, 'class11'),
                          (1, 3, 'class11'),
                          (3, 6, 'class2'),
                          (6, 10, 'class3'),
                          (6, 8, 'class11'),
                          (7, 9, 'class11'),
                          (6, 9, 'class1'),
                          (10, 13, 'class2'),
                          (10, 12, 'class21'),
                          (11, 13, 'class21')},
                         set(tagger.get_tagged_entities(tokens, True)))


class FileFolderTokenMappingTest(unittest.TestCase):

    def test_should_get_mappings_from_whole_data_folder_extension_txt(self):
        mapper = FileFolderTokenMapping(data_folder=path(__file__, 'data/dictionary'), extension='.txt')

        mappings = {
            (path(__file__, 'data/dictionary/file1.txt'), 'file1'),
            (path(__file__, 'data/dictionary/sub1data/sub1file1.txt'), 'sub1data/sub1file1'),
            (path(__file__, 'data/dictionary/sub1data/sub1file2.txt'), 'sub1data/sub1file2'),
            (path(__file__, 'data/dictionary/sub1data/sub1sub1data/sub1sub1file1.txt'), 'sub1data/sub1sub1data/sub1sub1file1'),
            (path(__file__, 'data/dictionary/sub2data/sub2file1.txt'), 'sub2data/sub2file1'),
            (path(__file__, 'data/dictionary/sub2data/sub2file2.txt'), 'sub2data/sub2file2'),
        }
        self.assertEqual(mappings, mapper.get_file_tag_mappings())

    def test_should_get_few_mappings_from_whole_data_folder_NOT_recursive(self):
        mapper = FileFolderTokenMapping(data_folder=path(__file__, 'data/dictionary'), recursive=False)

        mappings = {
            (path(__file__, 'data/dictionary/file1.txt'), 'file1'),
        }
        self.assertEqual(mappings, mapper.get_file_tag_mappings())

    def test_should_get_few_mappings_from_whole_sub_data_folder_NOT_recursive_txt(self):
        mapper = FileFolderTokenMapping('sub1data', data_folder=path(__file__, 'data/dictionary'), recursive=False, extension='.txt')

        mappings = {
            (path(__file__, 'data/dictionary/sub1data/sub1file1.txt'), 'sub1data/sub1file1'),
            (path(__file__, 'data/dictionary/sub1data/sub1file2.txt'), 'sub1data/sub1file2'),
        }
        self.assertEqual(mappings, mapper.get_file_tag_mappings())

    def test_should_get_mapping_for_file_no_extension_extension_not_specified(self):
        mapper = FileFolderTokenMapping('no_extension', data_folder=path(__file__, 'data/dictionary'), extension=None)

        mappings = {
            (path(__file__, 'data/dictionary/no_extension'), 'no_extension')
        }
        self.assertEqual(mappings, mapper.get_file_tag_mappings())

    def test_should_get_mappings_from_whole_data_folder_extension_any(self):
        mapper = FileFolderTokenMapping(data_folder=path(__file__, 'data/dictionary'), extension=None)

        mappings = {
            (path(__file__, 'data/dictionary/no_extension'), 'no_extension'),
            (path(__file__, 'data/dictionary/file1.txt'), 'file1'),
            (path(__file__, 'data/dictionary/sub1data/sub1file1.txt'), 'sub1data/sub1file1'),
            (path(__file__, 'data/dictionary/sub1data/sub1file2.txt'), 'sub1data/sub1file2'),
            (path(__file__, 'data/dictionary/sub1data/sub1file1.csv'), 'sub1data/sub1file1'),
            (path(__file__, 'data/dictionary/sub1data/sub1sub1data/sub1sub1file1.txt'), 'sub1data/sub1sub1data/sub1sub1file1'),
            (path(__file__, 'data/dictionary/sub2data/sub2file1.txt'), 'sub2data/sub2file1'),
            (path(__file__, 'data/dictionary/sub2data/sub2file1.csv'), 'sub2data/sub2file1'),
            (path(__file__, 'data/dictionary/sub2data/sub2file2.txt'), 'sub2data/sub2file2'),
        }
        self.assertEqual(mappings, mapper.get_file_tag_mappings())

    def test_should_get_mappings_via_dict_keys_and_values(self):
        mapper = FileFolderTokenMapping({'sub1data': ['sub1file1.txt', 'sub1file2.txt'], 'sub2data': ['sub2file1.txt']},
                                        data_folder=path(__file__, 'data/dictionary'))

        mappings = {
            (path(__file__, 'data/dictionary/sub1data/sub1file1.txt'), 'sub1data/sub1file1'),
            (path(__file__, 'data/dictionary/sub1data/sub1file2.txt'), 'sub1data/sub1file2'),
            (path(__file__, 'data/dictionary/sub2data/sub2file1.txt'), 'sub2data/sub2file1'),
        }
        self.assertEqual(mappings, mapper.get_file_tag_mappings())

    def test_should_get_mappings_via_filenames_without_extension_extension_specified(self):
        mapper = FileFolderTokenMapping({'sub1data': ['sub1file1', 'sub1file2'], 'sub2data': ['sub2file1']},
                                        data_folder=path(__file__, 'data/dictionary'), extension='.txt')

        mappings = {
            (path(__file__, 'data/dictionary/sub1data/sub1file1.txt'), 'sub1data/sub1file1'),
            (path(__file__, 'data/dictionary/sub1data/sub1file2.txt'), 'sub1data/sub1file2'),
            (path(__file__, 'data/dictionary/sub2data/sub2file1.txt'), 'sub2data/sub2file1'),
        }
        self.assertEqual(mappings, mapper.get_file_tag_mappings())

    def test_should_raise_exception_on_filenames_without_extension_extension_not_specified(self):
        self.assertRaises(DataSourceException, lambda: FileFolderTokenMapping({'sub1data': ['sub1file1', 'sub1file2'], 'sub2data': ['sub2file1']},
                                        data_folder=path(__file__, 'data/dictionary'), extension=None))

    def test_should_get_mappings_via_dict_keys_nested(self):
        mapper = FileFolderTokenMapping({'sub1data': {'sub1sub1data': 'sub1sub1file1.txt'}}, data_folder=path(__file__, 'data/dictionary'))

        mappings = {
            (path(__file__, 'data/dictionary/sub1data/sub1sub1data/sub1sub1file1.txt'), 'sub1data/sub1sub1data/sub1sub1file1')
        }
        self.assertEqual(mappings, mapper.get_file_tag_mappings())

    def test_should_raise_exception_on_wrong_path(self):
        self.assertRaises(DataSourceException, lambda: FileFolderTokenMapping('this/path/does/not/exists.txt',
                                                                              data_folder=path(__file__, 'data')))

    def test_should_init_lookup_from_mapper(self):
        mapper = FileFolderTokenMapping('sub1data/sub1sub1data/sub1sub1file1.txt', data_folder=path(__file__, 'data/dictionary'))
        dictionary_lookup = DictionaryLookUp(mapper)

        self.assertIsNotNone(dictionary_lookup)
        self.assertEquals('sub1data/sub1sub1data/sub1sub1file1', dictionary_lookup['a'])


class FileFolderTokenMappingReadTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_should_read_first_and_third_lines(self):
        name = 'escape'
        import io
        file = io.open('data/' + name + '.txt', 'rt', encoding='utf-8')
        read_file = [(line.split(), name) for line in file]
        expected_mappings = [read_file[0], read_file[2]]

        mapper = FileFolderTokenMapping(name, data_folder=path(__file__, 'data'))
        self.assertEqual(expected_mappings, list(mapper))


class DictionaryLookUpPreprocessingTest(unittest.TestCase):

    def setUp(self):
        self.mappings = [
            ('a B c', 'class121'),
            ('a b C', 'class112'),
            ('A b C', 'class212')
        ]

    def test_should_apply_while_initing(self):
        preprocessing = lambda x: x.lower()
        dict = DictionaryLookUp(self.mappings, preprocessing)

        self.assertIsNotNone(dict['a b c'])
        self.assertEqual('class212', dict['a b c'])

    def test_should_apply_while_referring(self):
        preprocessing = lambda x: x.lower()
        dict = DictionaryLookUp(self.mappings, preprocessing)

        self.assertIsNotNone(dict['a B C'])
        self.assertEqual('class212', dict['A b c'])
        self.assertEqual(dict['A b C'], dict['a B c'])


class DictionaryLookUpTest(unittest.TestCase):

    def setUp(self):
        self.mappings = [
            ('a b c', 'class1'),
            ('a b', 'class11'),
            ('a c', 'class1'),
            ('b c', 'class1'),
            ('a a a', 'class2'),
            ('a a', 'class21'),
            ('b b b', 'class2'),
            ('c c c', 'class2'),
            ('a b c d', 'class3'),
            ('a b c e', 'class3'),
        ]

    def test_should_init_from_strings(self):
        dictionary = DictionaryLookUp(self.mappings)
        self.assertIsNotNone(dictionary)

    def test_should_init_from_tokens(self):
        dictionary = DictionaryLookUp([(tokens.split(), classes) for (tokens, classes) in self.mappings])
        self.assertIsNotNone(dictionary)

    def test_should_contain_simple_mapping(self):
        dictionary = DictionaryLookUp(self.mappings)
        self.assertIsNotNone(dictionary.get_tag(self.mappings[7][0]))

    def test_should_contain_sub_mapping(self):
        dictionary = DictionaryLookUp(self.mappings)
        self.assertIsNotNone(dictionary.get_tag(self.mappings[1][0]))

    def test_should_contain_mega_mapping(self):
        dictionary = DictionaryLookUp(self.mappings)
        self.assertIsNotNone(dictionary.get_tag(self.mappings[8][0]))

    def test_should_not_contain_mapping(self):
        dictionary = DictionaryLookUp(self.mappings)
        self.assertIsNone(dictionary.get_tag(' '.join([tokens for tokens, _ in self.mappings])))

    def test_should_contain_correct_tag_for_simple_mapping(self):
        dictionary = DictionaryLookUp(self.mappings)
        self.assertEqual(dictionary.get_tag(self.mappings[7][0]), self.mappings[7][1])

    def test_should_contain_correct_tag_for_sub_mapping(self):
        dictionary = DictionaryLookUp(self.mappings)
        self.assertEqual(dictionary.get_tag(self.mappings[1][0]), self.mappings[1][1])

    def test_should_contain_correct_tag_for_mega_mapping(self):
        dictionary = DictionaryLookUp(self.mappings)
        self.assertEqual(dictionary.get_tag(self.mappings[8][0]), self.mappings[8][1])

    def test_should_rewrite_class(self):
        new_mappings = list(self.mappings)
        new_mappings.append((self.mappings[len(self.mappings) - 1][0],self.mappings[len(self.mappings) - 1][1][::-1]))
        dictionary = DictionaryLookUp(new_mappings)
        self.assertEqual(dictionary.get_tag(self.mappings[len(self.mappings) - 1][0]), new_mappings[len(new_mappings) - 1][1])
        self.assertNotEqual(dictionary.get_tag(self.mappings[len(self.mappings) - 1][0]), self.mappings[len(self.mappings) - 1][1])

    def test_should_contain_correct_tag_for_simple_mapping_via_getitem(self):
        dictionary = DictionaryLookUp(self.mappings)
        self.assertEqual(dictionary[self.mappings[7][0]], self.mappings[7][1])

    def test_should_contain_simple_mapping_via_getitem(self):
        dictionary = DictionaryLookUp(self.mappings)
        self.assertIsNotNone(dictionary[self.mappings[7][0]])

    def test_should_add_simple_mapping_via_setitem(self):
        dictionary = DictionaryLookUp({})
        dictionary['new mapping'] = 'new_class'
        self.assertIsNotNone(dictionary['new mapping'])
        self.assertEqual(dictionary['new mapping'], 'new_class')

    def test_should_get_longest(self):
        dictionary = DictionaryLookUp(self.mappings)
        self.assertEqual(max([len(token.split()) for token, _ in self.mappings]), dictionary.get_longest_sequence())

    def test_should_get_longest_zero(self):
        dictionary = DictionaryLookUp([])
        self.assertEqual(0, dictionary.get_longest_sequence())

    def test_should_get_longest_multiple_alternatives(self):
        mappings = [('a a a a a a a a a a b', 'c'), ('a a a a a a a a a a c', 'c2')]
        dictionary = DictionaryLookUp(mappings)
        self.assertEqual(max([len(token.split()) for token, _ in mappings]), dictionary.get_longest_sequence())

    def test_should_get_known_classes_empty(self):
        dictionary = DictionaryLookUp([])
        self.assertEqual(0, len(dictionary.get_known_classes()))

    def test_should_get_known_classes(self):
        dictionary = DictionaryLookUp(self.mappings)
        self.assertEqual(sorted(list({c for _, c in self.mappings})), sorted(list(dictionary.get_known_classes())))