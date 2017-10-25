# -*- coding: utf-8 -*-
import io

from pynlple.exceptions import DataSourceException
from pynlple.module import append_paths, list_dir, is_file, strip_extension, abs_path, exists, is_folder
from pynlple.processing.text import TokenTagger


class DictionaryLookUp(object):
    """
    Dictionary class to store tokens sequences with their classes.
    Implements tree-like storage structure. Supports preprocessing
    of both saved and query sequences.

    Constructor takes:
    1. An iterator of `(sequence, tag)` tuples, where
    sequence can be either a whitespace-separated `str` or `list(str)` of tokens,
    2. A `func(list(str)) -> list(str)` for preprocessing of both contained (before saving)
    and queried (at the moment of query) sequences that is applied
    to each 'str' token in a sequence (`str.split()` first).

    Use built-in `lookup.__setitem__(str_or_list_str, tag_str)` or `lookup.put(str_or_list_str, tag_str)`
    to add new sequence-class mappings. Mappings are overriden if the sequence mapping
    is present in the lookup dictionary.

    Use built-in `lookup.__getitem__(str_or_list_str)` or `lookup.get_tag(str_or_list_str)` to query your
    sequence and get either the class assigned tag or `None` if no corresponding mapping can be found.

    Usage::

        >>> lookup = DictionaryLookUp([('sequence one', 'class1'), (['sequence', 'two'], 'class2')], str.lower)
        >>> lookup['Sequence One']
        class1
        >>> lookup['sequence two'] = 'class1'
        >>> lookup[['sequence' 'two']]
        class1
        >>> lookup[['sequence three']]
        None
    """

    __X = '@endX!'
    """
    Internal tag to mark sequence end. Please, make sure to not have this in your sequences.

    :type str
    """

    def __init__(self, token_mappings, preprocessing_method=None):
        """
        Inits a dictionary lookup from mappings of tokens to their class tags.
        Includes the usafe of a preprocessing function.

        :param iterator(tuple(list(str), object)) token_mappings: iterable of tuples
        of token sequences and corresponding tags
        :param func(list(str)) -> list(str) preprocessing_method: the preprocessing function to be applied
        on stored sequences and queried sequences. Default: None, no preprocessing
        """
        self.dictionary = dict()
        self.preprocess = preprocessing_method
        for tokens, class_ in token_mappings:
            self.__setitem__(tokens, class_)

    def __setitem__(self, tokens, class_):
        if type(tokens) == str:
            tokens = tokens.split()
        DictionaryLookUp.__add_to_dict(self.__prep(tokens), 0, self.dictionary, class_)

    def __getitem__(self, tokens):
        if type(tokens) == str:
            tokens = tokens.split()
        return DictionaryLookUp.__get_from_dict(self.__prep(tokens), 0, self.dictionary)

    @staticmethod
    def __add_to_dict(list_, index, dict_, tag):
        if index < len(list_):
            if list_[index] not in dict_:
                dict_[list_[index]] = dict()
            DictionaryLookUp.__add_to_dict(list_, index + 1, dict_[list_[index]], tag)
        elif index == len(list_):
            dict_.update({DictionaryLookUp.__X: tag})

    @staticmethod
    def __get_from_dict(list_, index, dict_):
        if index < len(list_):
            if list_[index] not in dict_:
                return None
            return DictionaryLookUp.__get_from_dict(list_, index + 1, dict_[list_[index]])
        elif index == len(list_):
            if DictionaryLookUp.__X in dict_:
                return dict_[DictionaryLookUp.__X]
            else:
                return None

    def put(self, tokens, class_):
        """
        Add new or override the existing token sequence - class mapping to the lookup.

        :param list(str) tokens: sequence of tokens to set mapping for.
        Also supports a `str` sequence by applying str.split()
        :param object class_: corresponding class tag
        :return: void
        """
        if type(tokens) == str:
            tokens = tokens.split()
        DictionaryLookUp.__add_to_dict(self.__prep(tokens), 0, self.dictionary, class_)

    def get_tag(self, tokens):
        """
        Query the token sequence to infer its mapped class tag.

        :param list(str) tokens: sequence of tokens to get mapping for.
        Also supports a `str` sequence by applying str.split()
        :return: the corresponding class tag mapping or `None` if such sequence does not contain mapping
        :rtype: object
        """
        if type(tokens) == str or type(tokens) == list:
            tokens = tokens.split()
        return DictionaryLookUp.__get_from_dict(self.__prep(tokens), 0, self.dictionary)

    def __prep(self, tokens):
        if self.preprocess:
            return [self.preprocess(token) for token in tokens]
        else:
            return tokens

    def get_longest_sequence(self):
        """
        Get the longest stored token sequence length.

        :return: the length of the longest sequence
        :rtype: int
        """
        return DictionaryLookUp.__find_local_max(self.dictionary, 0, 0)

    def get_known_classes(self):
        """
        Get the set of classes known by the current lookup.

        :return: a set of string class names
        :rtype: set
        """
        return set(DictionaryLookUp.__find_all_classes(self.dictionary, []))

    @staticmethod
    def __find_local_max(dict_, current, max_):
        if current > max_:
            max_ = current
        for key in dict_.keys():
            if key != DictionaryLookUp.__X:
                max_ = DictionaryLookUp.__find_local_max(dict_[key], current + 1, max_)
        return max_

    @staticmethod
    def __find_all_classes(dict_, classes_list):
        for key in dict_.keys():
            if key == DictionaryLookUp.__X:
                classes_list.append(dict_[key])
            else:
                classes_list = DictionaryLookUp.__find_all_classes(dict_[key], classes_list)
        return classes_list


class FileFolderTokenMapping(object):
    """
    Class instance searches over the file-folder tree and implements `iterator(tuple(str, str))`
    (via `__iter__()`) over all text files surpassing specific conditions yielding `(file-line, file-path-name)`
    tuple pairs consumable by :class:DictionaryLookUp.

    File-folder tree walk is performed relative to `data_folder`, which is by default the 'data' folder
    in plynlple.processing package. Tree walk may be `recursive` (visiting inner subfolders),
    `extension`-sensitive (checking file suffixes to match the `extension` if not None).

    Tree walk is performed for all files and folders in the source `data_folder` (including
    `recursive` and `extension` rules) unless any subpaths are stated in `source_paths'.
    All 'source_paths' are treated exclusively to all other datafile paths. These `source_paths` also
    undergo `recursive` and `extension` rule checks.

    The whole relative path (to the data path) to the file is put as the second item in the output tuple.
    The extension of the file is stripped, though.

    You can mix up `list`/`set`/`tuple`s of file paths, folder paths as well as
    `dictionary`s of `{prefix:suffixes} in `source_paths`.

    Consider the following folder structure::
        -folder1
            -folder1-1
            -file1-1 (folder1/file1-1)
            -file1-2 (folder1/file1-2)
        -folder2
            -folder2-1
                -file2-1-1 (folder2/folder2-1/file2-1-1)
                -file2-1-2 (folder2/folder2-1/file2-1-2)
            -folder2-2
                -file2-2-1 (folder2/folder2-2/file2-2-1)
            -file2-1 (folder2/file2-1)
        -file1 (file1)
        -file2 (file2)

    Setting the `source_paths` to ['folder1', 'folder2/folder2-1] will yield the following tree walked::
        -folder1
            -folder1-1
            -file1-1 (folder1/file1-1)
            -file1-2 (folder1/file1-2)
        -folder2
            -folder2-1
                -file2-1-1 (folder2/folder2-1/file2-1-1)
                -file2-1-2 (folder2/folder2-1/file2-1-2)

    Complex `source_paths` may look like following:
    {'folder2': ['folder2-1', 'folder2-2']}, ['folder1/file1-1', 'file1'] and yield::
        -folder2
            -folder2-1
                -file2-1-1 (folder2/folder2-1/file2-1-1)
                -file2-1-2 (folder2/folder2-1/file2-1-2)
            -folder2-2
                -file2-2-1 (folder2/folder2-2/file2-2-1)
        -folder1
            -file1-1 (folder1/file1-1)
        -file1 (file1)

    Use this class to arrange you Named Entities, POS lists, stopwords, etc. by putting
    the corresponding files to the folders by groups (e.g. rus/stopwords/punctuation.txt)

    """
    def __init__(self, source_paths=None, data_folder=None, recursive=True, extension='.txt', encoding='utf8'):
        """
        Create an `iterator(tuple(str, str))` over all text files surpassing specific conditions
        yielding `(file-line, file-path-name)` tuple pairs consumable by :class:DictionaryLookUp.

        :param iterable source_paths: paths relative to `data_folder` to walk through exclusively
        :param str data_folder: paths to the folder containing data,
        :param bool recursive: visit subfolders
        :param str extension: filter files by suffix, default: None - perform no filtering
        :param str encoding: text file encodings, default: `utf8`
        """
        if data_folder:
            self.__data_folder = data_folder
        else:
            self.__data_folder = abs_path(__file__, 'data')
        self.__recursive = recursive
        self.__extension = extension
        self.__encoding = encoding
        self.__file_tag_mappings = set()
        self.__parse_mapping_sources(self.__file_tag_mappings, '', source_paths)

    def __parse_mapping_sources(self, file_tag_mappings, path_prefix, source_paths):
        if not source_paths or len(source_paths) == 0:
            self.__sweep_folder_or_file(file_tag_mappings, path_prefix, '', True)
        elif type(source_paths) is str:
            self.__sweep_folder_or_file(file_tag_mappings, path_prefix, source_paths, True)
        elif type(source_paths) is list or type(source_paths) is set:
            for seed_path in source_paths:
                self.__parse_mapping_sources(file_tag_mappings, path_prefix, seed_path)
        elif type(source_paths) is dict and all(type(key) is str for key in source_paths):
            for prefix, suffix in source_paths.items():
                self.__parse_mapping_sources(file_tag_mappings, append_paths(path_prefix, prefix), suffix)

    def __sweep_folder_or_file(self, file_tag_mappings, path_prefix, folder_or_file_subpath, recursive):
        absolute_file_or_folder_path = append_paths(self.__data_folder, path_prefix)
        if folder_or_file_subpath and len(folder_or_file_subpath) > 0:
            absolute_file_or_folder_path = append_paths(absolute_file_or_folder_path, folder_or_file_subpath)
        if not exists(absolute_file_or_folder_path):
            if self.__extension and exists(absolute_file_or_folder_path + self.__extension):
                absolute_file_or_folder_path += self.__extension
            else:
                raise DataSourceException('[{0}] File/folder could not be found: {1}, extension: {2}'
                                          .format(__name__, absolute_file_or_folder_path, self.__extension))
        if is_file(absolute_file_or_folder_path):
            # Here check if we have extension set. Use it to check file ending if set
            if not self.__extension or absolute_file_or_folder_path.endswith(self.__extension):
                tag = FileFolderTokenMapping\
                    .normalize_tag(append_paths(path_prefix, strip_extension(folder_or_file_subpath)))
                file_tag_mappings.add((absolute_file_or_folder_path, tag))
        if is_folder(absolute_file_or_folder_path):
            if recursive:
                for element_name in list_dir(absolute_file_or_folder_path):
                    new_path_prefix = append_paths(path_prefix, folder_or_file_subpath)
                    self.__sweep_folder_or_file(file_tag_mappings, new_path_prefix, element_name, self.__recursive)

    @staticmethod
    def normalize_tag(tag):
        """
        Use to replace wrong backslashes with correct slashes.

        :param str tag: tag text derived from file path
        :return: tag with nice slashes
        :rtype: str
        """
        return tag.replace('\\', '/')

    def get_file_tag_mappings(self):
        """
        Get the file paths of files retrieved during file-folder tree walking.
        All conditions applied.

        :return: set of tuple(full-filepath, tag) mappings
        :rtype: set(str, str)
        """
        return self.__file_tag_mappings

    def __iter__(self):
        """
        Get the iterable of tuple(token_sequence, token_tag) from
        the files walked.

        :return: tuples of text lines (token strings) and corresponding tags derived
        from the containing filepath
        :rtype: iterator(tuple(str, str))
        """
        for file_path, tag in self.__file_tag_mappings:
            for line in io.open(file_path, 'rt', encoding=self.__encoding):
                yield line.strip().split(), tag


class DictionaryBasedTagger(TokenTagger):

    def __init__(self, dictionary_look_up):
        self.lookup = dictionary_look_up

    def get_classes(self):
        return sorted(list(self.lookup.get_known_classes()))

    def get_tagged_entities(self, tokens, all_=False):
        max_ = self.lookup.get_longest_sequence()
        entities = list()
        i = 0
        while i < len(tokens):
            j = i + max_ if i + max_ <= len(tokens) else len(tokens)
            while j > i:
                class_ = self.lookup[tokens[i:j]]
                if class_ is not None:
                    entities.append((i, j, class_))
                    if not all_:
                        i = j - 1
                        break
                j -= 1
            i += 1
        return entities
