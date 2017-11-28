# from buildtools import update

# from mock.mock import self

from qordoba.commands.i18n_base import BaseClass, IGNOREFILES
from qordoba.settings import get_localization_files, get_i18n_app_pattern

import logging
import pprint
import os

pp = pprint.PrettyPrinter(indent=4)
log = logging.getLogger('qordoba')

class MoveClass(BaseClass):
    """
    the move command will help to rename keys in an already localized app & localization file
    """
    def get_all_keys(self, json_dictionary, path, c):

        for key, value in json_dictionary.items():

            path.append(key)
            if type(value) is not dict:
                s_path = '.'.join(path)
                c[s_path] = value
            else:
                self.get_all_keys(value, path, c)
            path.pop()

        return c

    def get_match(self, source, target):

        source_key = source.split('.')
        target_key = target.split('.')

        if len(source_key) == len(target_key):

            overlap = []
            for i in range(len(source_key)):

                if source_key[i] == target_key[i]:
                    overlap.append(source_key[i])
                else:
                    overlap.append(source_key[i])
                    overlap = ['.'.join(overlap) + '.']
                    overlap.append(tuple((source_key[i], target_key[i])))
                    return overlap
        else:
            "keys have to be the same length"

    def find_affected_keys(self, key_match, all_keys):

        move = []
        for k in all_keys.keys():

            if key_match[0] in k:
                move.append(k)

        return move

    def replace_key(self, keys2move, key_match):

        keys_moved = {}
        source, dest = key_match[1]
        for key in keys2move:
            old_key = key
            new_key = key.replace(source, dest)
            keys_moved[old_key] = new_key

        log.info("key pairs that will be changed in localization-file: {} \n ".format(pprint.pprint(keys_moved)))

        return keys_moved

    def change_key_heirarchy(self, new_dict, old_key, new_key):
        '''
            changing the hierarchy of the dictionary, to 'merge out' exact match
        '''

        old_list = old_key.split('.')
        new_list = new_key.split('.')

        parent = new_dict
        d = new_dict

        for i in range(len(old_list) - 1):
            old_key = old_list[i]
            new_key = new_list[i]
            parent = d
            d = d[old_key]
            if old_key != new_key:
                try:
                    shifted = d[new_key]
                except KeyError:
                    shifted = {}
                    parent[new_key] = shifted

                next_key = old_list[i + 1]

                shifted[next_key] = d.pop(next_key)

        return new_dict

    def find_replace(self, new_dict, old_list, new_list):
        '''
        standard changing the keys in a dictionary.
        '''
        try:
            while len(old_list) != 0:
                k = 0
                if old_list[k] == new_list[k]:
                    key = old_list[k]
                    del old_list[k]
                    del new_list[k]
                    self.find_replace(new_dict[key], old_list, new_list)
                else:
                    n_key = new_list[k]
                    o_key = old_list[k]
                    try:
                        new_dict[n_key] = new_dict.pop(o_key)
                    except KeyError:
                        pass

                    del old_list[k]
                    del new_list[k]
                    self.find_replace(new_dict[n_key], old_list, new_list)
        except IndexError:
            pass
        return new_dict

    def replace_key_in_file(self, dictionary, keyPairs):
        '''Creating new localization file in output folder with new key structure'''

        for old_key, new_key in keyPairs.items():

            old_list = old_key.split('.')
            new_list = new_key.split('.')
            dictionary_new = self.find_replace(dictionary, old_list, new_list)

        return dictionary_new

    def replace_keys_in_project(self, fileToSearch, keyPairs):

        filename = fileToSearch.split('/')[-1]

        with open(fileToSearch, 'r') as file:
            try:
                filedata = file.read()
                for old_key, new_key in keyPairs.items():
                    filedata = filedata.decode().replace(old_key, new_key)
                    with open(fileToSearch, 'w') as file:
                        file.write(filedata)
            except UnicodeDecodeError:
                log.info("File cant be decoded {}".format(filename))

        # for i, line in enumerate(open(fileToSearch)):
        #     # for line in file:
        #     print(fileToSearch)
        #     written = False
        #     count = 0
        #     try:
        #         for old_key, new_key in keyPairs.items():
        #             new_line = line.decode().replace(old_key, new_key)
        #             count += 1
        #             if new_key in new_line:
        #                 fileToSearch.write(new_line)
        #                 written = True
        #             if written is False and len(keyPairs) == count:
        #                 f.write(new_line)
        #     except UnicodeDecodeError:
        #         log.info("line cant be decoded {}".format(line))

    def i18n_move_command(self, curdir, config, run=False, exact_match=False, source=None, target=None):

        pattern = get_localization_files(config)
        i18n_app_path = get_i18n_app_pattern(config)

        for file_path in pattern:

            json_dictionary = self.get_i18n_dictionary(file_path)

            # without the exact match flag all keys where a leaf changes will be replaced
            key_match = self.get_match(source, target)
            all_keys = self.get_all_keys(json_dictionary, list(), dict())
            keys2move = self.find_affected_keys(key_match, all_keys)

            if exact_match:
                keyPairs = dict()
                keyPairs[source] =  target

            else:
                keyPairs = self.replace_key(keys2move, key_match)

            result = self.find_keys_in_project(keyPairs, i18n_app_path)

            if run is False:
                # logging the files which will be affected to stdout, no changes will be executed
                if result != {}:
                    log.info(
                        "\n Moving would affect the following files and lines. \n "
                        "To execute, run mv command with the `--run` flag.")

                    for k, v in result.items():
                        for label in v.keys():
                            num = v[label]
                            log.info( "--- \n {:<8} \n  file: {:<15} \n  line: {:<10}".format(k, label, num))

                else:
                    log.info("\n In the actual project path where no keys found to change. Path is: `{}`".format(
                        i18n_app_path))

            # changes will be executed with run - the keys in the project and the localization file
            if run:
                # first, create updated localization file and store in output folder
                json_dictionary_no_i18n_keys_but_nested = self.get_nested_dictionary(file_path)
                if exact_match:
                    new_dict = self.change_key_heirarchy(self.get_nested_dictionary(file_path).copy(), source, target)
                else:
                    new_dict = self.replace_key_in_file(json_dictionary_no_i18n_keys_but_nested.copy(), keyPairs)
                command = '_i18n_'
                self.write_to_output(file_path, new_dict, command)

                # second, change keys within project
                log.info("\n STARTING... to replace keys in project: {} \n".format(i18n_app_path[0]))
                for subdir, dirs, files in os.walk(i18n_app_path[0]):
                    for file in files:
                        if file in IGNOREFILES:
                            continue
                        fileToSearch = subdir + os.sep + file
                        self.replace_keys_in_project(fileToSearch, keyPairs)
                    log.info("Replaced keys in subdir {}".format(subdir))
