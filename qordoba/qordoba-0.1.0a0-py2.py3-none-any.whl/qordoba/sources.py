from __future__ import unicode_literals, print_function

import glob
import logging
import os
import re
from collections import OrderedDict

from qordoba.languages import normalize_language, LanguageNotFound
from qordoba.utils import python_2_unicode_compatible

log = logging.getLogger('qordoba')

DEFAULT_PATTERN = '<language_code>.<extension>'

CONTENT_TYPE_CODES = dict()
CONTENT_TYPE_CODES['excel'] = ('xlsx',)
CONTENT_TYPE_CODES['xliff'] = ('xliff', 'xlf')
CONTENT_TYPE_CODES['XLIFF1.2'] = ('xliff', 'xlf')
CONTENT_TYPE_CODES['xmlAndroid'] = ('xml',)
CONTENT_TYPE_CODES['PO'] = ('po',)
CONTENT_TYPE_CODES['POT'] = ('pot',)
CONTENT_TYPE_CODES['stringsI18nProperties'] = ('properties',)
CONTENT_TYPE_CODES['YAMLi18n'] = ('yml', 'yaml')
CONTENT_TYPE_CODES['YAML'] = ('yml', 'yaml')
CONTENT_TYPE_CODES['iosStringsDict'] = ('stringsdict', )
CONTENT_TYPE_CODES['macStrings'] = ('strings',)
CONTENT_TYPE_CODES['csv'] = ('csv',)
CONTENT_TYPE_CODES['JSON'] = ('json',)
CONTENT_TYPE_CODES['SRT'] = ('srt',)
CONTENT_TYPE_CODES['md'] = ('md', 'text')
CONTENT_TYPE_CODES['stringsHtml'] = ('html', 'htm')
CONTENT_TYPE_CODES['stringsResx'] = ('resx',)
CONTENT_TYPE_CODES['stringsDocx'] = ('docx',)

# .xlsx, .pptx idml ts

ALLOWED_EXTENSIONS = dict(
    {extension: k for k, extensions in CONTENT_TYPE_CODES.items() for extension in extensions}
)

ADJUST_EXTENSION = {
    # "resx": "regex",
}

MIMETYPES = {
    'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
}

CUSTOM_LANGUAGE_CODE = {
     'zh-chs' : 'zh-Hans',
     'zh-cht' : ' zh-Hant',
     'pt-br' : 'pt-BR',
     'zh-cn' : 'zh-CN',
}

def get_mimetype(content_type):
    return MIMETYPES.get(content_type, 'application/octet-stream')

class PatternNotValid(Exception):
    pass


class FileExtensionNotAllowed(Exception):
    """
    The file extension doesn't match any file format allowed for this project
    """


def to_posix(filepath):
    return filepath if os.altsep is None else filepath.replace(os.altsep, '/').replace(os.sep, '/')


def to_native(filepath):
    return filepath if os.altsep is None else filepath.replace(os.altsep, os.sep)


@python_2_unicode_compatible
class TranslationFile(object):
    def __init__(self, path, lang, curdir):
        self.relpath = path
        self.name = os.path.basename(path)
        self.lang = lang
        self._curdir = curdir
        self.fullpath = os.path.join(curdir, path)

    @property
    def extension(self):
        try:
            extension = os.path.splitext(self.name)[1][1:]
        except ValueError:
            extension = None
        return extension

    @property
    def posix_path(self):
        return to_posix(self.relpath)

    @property
    def native_path(self):
        return to_native(self.relpath)

    @property
    def path_parts(self):
        return self.relpath.split(os.sep)

    @property
    def unique_name(self):
        return self.name

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return self.name

    def replace(self, name):
        """
        Replace file name. Create new TranslationPath
        :param str name:
        :rtype: qordoba.sources.TranslationPath
        """
        new_path = os.path.join(os.path.dirname(self.relpath), name)

        return self.__class__(new_path, self.lang, self._curdir)


def validate_path(curdir, path, lang):
    """
    Validate path
        Make path relative to curdir
        Validate language string
        Create TranslationFile object
    :param str curdir: FilePath.
    :param str path: Raw file path
    :param str lang: Raw language string
    :rtype: qordoba.sources.TranslationFile
    """
    lang = normalize_language(lang)
    if not isinstance(path, TranslationFile):
        if os.path.isabs(path):
            path = os.path.relpath(path, curdir)
        path = TranslationFile(path, lang, curdir)

    return path


class PatternVariables(object):
    language_code = 'language_code'
    language_name = 'language_name'
    language_name_cap = 'language_name_cap'
    language_name_allcap = 'language_name_allcap'
    language_lang_code = 'language_lang_code'

    filename = 'filename'
    extension = 'extension'

    all = language_code, language_name, language_name_cap, language_name_allcap, language_lang_code, filename, extension

#
def custom_language(language):
    return CUSTOM_LANGUAGE_CODE[str(language)]

push_pattern_validate_regexp = re.compile(
    '\<({})\>'
        .format('|'.join((PatternVariables.language_code, PatternVariables.language_lang_code)))
)
pull_pattern_validate_regexp = re.compile('\<({})\>'.format('|'.join(PatternVariables.all)))


def validate_push_pattern(pattern):
    '''uncommenting allows users to configure the config.yml so they can push files with the same name'''
    # if not glob.has_magic(pattern):
    #     raise PatternNotValid('Push pattern is not valid. Pattern should contain one of the values: *,?')
    pass

def create_target_path_by_pattern(curdir, language, version_tag, source_name,  pattern=None, distinct=False, content_type_code=None):

    if not distinct and pattern is not None and not pull_pattern_validate_regexp.search(pattern):
        raise PatternNotValid(
            'Pull pattern is not valid. Pattern should contain one of the values: {}'.format(
                ', '.join(PatternVariables.all)))

    if pattern is None:
        pattern = language.code + '-' + source_name
        if version_tag:
            pattern = language.code + '-' + version_tag + '_' +source_name

    pattern = pattern or DEFAULT_PATTERN

    if 'lproj' in pattern and str(language) in CUSTOM_LANGUAGE_CODE.keys():
        target_path = pattern.replace('<{}>'.format(PatternVariables.language_code), custom_language(language))
        target_path = target_path.replace('<{}>'.format(PatternVariables.language_lang_code), custom_language(language))
        target_path = target_path.replace('<{}>'.format(PatternVariables.language_name), custom_language(language))
        target_path = target_path.replace('<{}>'.format(PatternVariables.language_name_cap),
                                          custom_language(language))
        target_path = target_path.replace('<{}>'.format(PatternVariables.language_name_allcap),
                                          custom_language(language))

    else:
        target_path = pattern.replace('<{}>'.format(PatternVariables.language_code), language.code)
        target_path = target_path.replace('<{}>'.format(PatternVariables.language_lang_code), language.lang)
        target_path = target_path.replace('<{}>'.format(PatternVariables.language_name), language.name)
        target_path = target_path.replace('<{}>'.format(PatternVariables.language_name_cap),
                                          language.name.capitalize())
        target_path = target_path.replace('<{}>'.format(PatternVariables.language_name_allcap),
                                          language.name.upper())


    if '<{}>'.format(PatternVariables.extension) in target_path \
            or '<{}>'.format(PatternVariables.filename) in target_path:
        try:
            filename, extension = os.path.splitext(source_name)
            extension = extension.strip('.')
            if version_tag:
                filename, extension = os.path.splitext(source_name)
                filename = version_tag + '_' + filename
                extension = extension.strip('.')
        except (ValueError, AttributeError):
            extension = ''
            filename = source_name
            if version_tag:
                filename = version_tag + '_' + filename

        target_path = target_path.replace('<{}>'.format(PatternVariables.extension), extension)
        target_path = target_path.replace('<{}>'.format(PatternVariables.filename), filename)

    return validate_path(curdir, target_path, language)


def files_in_project(curpath, return_absolute_path=True):
    """
    Iterate over the files in the project.

    Return each file under ``curpath`` with its absolute name.
    """
    visited = set()
    for root, dirs, files in os.walk(curpath, followlinks=True):
        root_realpath = os.path.realpath(root)

        # Don't visit any subdirectory
        if root_realpath in visited:
            del dirs[:]
            continue

        for f in files:
            file_path = os.path.realpath(os.path.join(root, f))
            if not return_absolute_path:
                file_path = os.path.relpath(file_path, curpath)
            yield file_path

        visited.add(root_realpath)

        # Find which directories are already visited and remove them from
        # further processing
        removals = list(
            d for d in dirs
            if os.path.realpath(os.path.join(root, d)) in visited
        )
        for removal in removals:
            dirs.remove(removal)



def _ishidden(path):
    return path[0] in ('.', b'.'[0])


def find_files_by_pattern(curpath, pattern, lang, remote_content_type_codes):
    validate_push_pattern(pattern)

    for path in glob.iglob(pattern):
        if os.path.isdir(path):
            continue

        if _ishidden(os.path.basename(path)):
            continue

        path = validate_path(curpath, path, lang)

        try:
            _ = get_content_type_code(path, remote_content_type_codes)
        except FileExtensionNotAllowed as e:
            log.info('File path ignored: {}'.format(e))
            continue

        yield path


def add_project_file_formats(formats, target_dict=ALLOWED_EXTENSIONS):
    """
    Adds items from the qordoba.yml file_formats key to the list of allowed
    extensions. This is to support per-project file formats (eg, txt, resx, etc)
    """
    if formats is not None:
        for key, val in formats.items():
            for item in val:
                target_dict[item] = key

    return target_dict


def get_content_type_code(path, remote_content_type_codes):
    """
    :param qordoba.sources.TranslationFile path:
    :return:
    """
    remote_content_types_list = list()
    for content_type in remote_content_type_codes:
        remote_content_types_list.append(content_type['content_type_code'])

    path_ext = path.extension


    if path_ext not in ALLOWED_EXTENSIONS:
        raise FileExtensionNotAllowed("File format `{}` not in allowed list of file formats: {}"
                                      .format(path_ext, ', '.join(ALLOWED_EXTENSIONS)))

    final_content_type = None
    content_set = False

    for k, v in CONTENT_TYPE_CODES.items():

        for value in v:
            if value == path_ext:
                final_content_type = k
                content_set = True

        if final_content_type in remote_content_types_list:
            final_content_type = k
            content_set = True

        if content_set:

            if not final_content_type:
                raise FileExtensionNotAllowed("File format `{}` not in allowed list of file formats: {}. Or not specified as file format in your project (supported filefomats are: {})"
                                          .format(path_ext, ', '.join(ALLOWED_EXTENSIONS), remote_content_types_list))

            return final_content_type

        else:

            continue




