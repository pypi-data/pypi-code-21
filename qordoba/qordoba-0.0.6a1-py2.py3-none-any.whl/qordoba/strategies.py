from __future__ import unicode_literals, print_function
from qordoba.utils import get_data
import logging
import os
import yaml


log = logging.getLogger('qordoba')

class Extension(object):
    def __init__(self):
        self.strategy_name = 'extension'
        self.language_extension_mappings = {}
        language_path = get_data('resources/language.yml')
        with open(language_path, 'r') as stream:
            try:
                data = yaml.load(stream)
                for ext_key_value in self.find_ext(data, 'extensions'):
                    (language, ext_list) = ext_key_value
                    self.language_extension_mappings[language] = ext_list
            except yaml.YAMLError as exc:
                print(exc)

    def get_extension(self, file_path):
        _, file_extension = os.path.splitext(file_path)
        return file_extension

    def find_ext(self, language_config, extention_tag):
        for language in language_config:
            extensions = language_config[language].get(extention_tag, [])
            yield language, set(extensions)

    def find_type(self, file_path):
        extension = self.get_extension(file_path)
        file_languages = []

        if extension:
            for language in self.language_extension_mappings:
                ext_set = self.language_extension_mappings[language]
                if extension in ext_set:
                    file_languages.append(str(language).capitalize())
        log.info('--- File `{}` with extension {} most certainly is of type {}'.format(file_path, extension, file_languages))
        return file_languages

class Shebang():

    def __init__(self):
        self.strategy_name = 'shebang'

    def get_shebang_script(self, first_line):
        if first_line[:2] != '#!':
            return []
        if len(first_line) < 4:
            # Empty after the shebang then return
            return []

        last_path = first_line.split('/')[-1]
        if not last_path:
            return []
        scripts = last_path.split()

        if len(scripts) == 1 and scripts[0] != 'env':
            return [str(scripts[0]).capitalize()]
        elif len(scripts) == 2 and scripts[0] == 'env':
            return [str(scripts[1]).capitalize()]
        else:
            for script in scripts:
                if script != 'env' and script[:2] != '--':
                    return [str(script).capitalize()]


    def find_type(self, file_path):
        infile = open(file_path, 'r')
        firstLine = infile.readline()
        log.info(
            '--- File `{}` with shebang most certainly is of type {}'.format(file_path, self.get_shebang_script(firstLine)))

        return self.get_shebang_script(firstLine)


class Filename():

    def __init__(self):
        self.strategy_name = 'filename'
        self.language_filename_mappings = {}
        language_path = get_data('resources/language.yml')
        with open(language_path, 'r') as stream:
            try:
                data = yaml.load(stream)
                for ext_key_value in self.find_filename(data, 'filenames'):
                    (language, ext_list) = ext_key_value
                    self.language_filename_mappings[language] = ext_list
            except yaml.YAMLError as exc:
                print(exc)

    def get_filename(self, file_path):
        file = file_path.split(os.sep)[-1]
        filename, _ = os.path.splitext(file)
        return filename

    def find_filename(self, language_config, filename_tag):
        for language in language_config:
            filename = language_config[language].get(filename_tag, [])
            yield language, set(filename)

    def find_type(self, file_path):
        filename = self.get_filename(file_path)
        file_languages = []

        if filename:
            for language in self.language_filename_mappings:
                filename_set = self.language_filename_mappings[language]
                if filename in filename_set:
                    file_languages.append(str(language).capitalize())
        log.info(
            '--- File `{}` with filename {} most certainly is of type {}'.format(file_path, filename, file_languages))
        return file_languages

# class Modeline():
#
#     def __init__(self):
#         self.strategy_name = 'modeline'
#
#     EMACS_MODELINE = re.compile(r"""-\*-(?:\s* (?= [^:;\s]+ \s* -\*-)|(?:.*?[;\s]|(?<=-\*-))mode\s*:\s*)([^:;\s]+)(?=[\s;]|(?<![-*])-\*-).*?-\*-""")
#
#     # VIM_MODELINE = re.compile()
#
#     Modeline = [EMACS_MODELINE, VIM_MODELINE]
#
#     def find_type(self, file_path):
#         with open(file_path) as blob:
#             lines = blob.readlines()
#         header = ('').join(lines[:10])
#         footer = ('').join(lines[-10:])
#         joined_blob = header + footer
#         for regex in self.Modeline:
#             match = regex.match(joined_blob)
#             if match:
#                 return match.group()
