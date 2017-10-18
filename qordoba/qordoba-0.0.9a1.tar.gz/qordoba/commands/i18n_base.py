import logging
import glob
from collections import OrderedDict
import os
import yaml, csv, json
import datetime
import pandas as pd
import sys

log = logging.getLogger('qordoba')

CONTENT_TYPE_CODES = OrderedDict()

CONTENT_TYPE_CODES['YAML'] = ('yml', 'yaml')
CONTENT_TYPE_CODES['YAMLi18n'] = ('yml', 'yaml')
CONTENT_TYPE_CODES['csv'] = ('csv',)
CONTENT_TYPE_CODES['JSON'] = ('json',)

ALLOWED_EXTENSIONS = OrderedDict(
    {extension: k for k, extensions in CONTENT_TYPE_CODES.items() for extension in extensions}
)

IGNOREFILES = [
    ".DS_Store",
    '.gitignore',
    '.git'
]

OUTPUT = dict()

class FilesNotFound(Exception):
    """
    Files not found
    """


class FileExtensionNotAllowed(Exception):
    """
    The file extension doesn't match any file format allowed for this project
    """


class BaseClass(object):

    def strip_qoutes(self, string):
        if string[:1] == "'" and string[-1] == "'" or string[:1] == '"' and string[-1] == '"':
            string = string[1:-1].strip()
            string = self.strip_qoutes(string)
        return string

    # change dir path e.g. 'command/dirs/' to 'command/dirs'
    def change_dir_path_to_default(self, dir_path):
        default_directory = str(dir_path).strip()
        if default_directory[-1] == '/':
            default_directory = default_directory[:-1]
        return default_directory

    # iterate python 2 and 3 compatible
    def iterate_items(self, to_iterate):
        if (sys.version_info > (3, 0)):
            # Python 3 code in this block
            return to_iterate.items()
        else:
            # Python 2 code in this block
            return to_iterate.iteritems()

    # validates csv report for i18n-generate (keys=False), i18n-execute (keys=True)
    def validate_report(self, file_path, keys=False):
        df = pd.read_csv(file_path)
        columns = list(df.columns.values)
        if not keys:
            try:
                 columns == ['filename',
                             'startLineNumber',
                             'startCharIdx',
                             'endLineNumber',
                             'endCharIdx',
                             'text']
            except ValueError:
                return False
            return True
        else:
            try:
                list(df.columns.values) == [
                    'filename', 'startLineNumber', 'startCharIdx',
                    'endLineNumber', 'endCharIdx', 'text', 'existing_keys',
                    'existing_localization_file', 'generated_keys']
            except ValueError:
                return False
            return True

    def get_files_in_Dir(self, report):
        files=list()
        for file_ in os.listdir(report):
            files.append(file_)
        return files

    def convert(self, input):
        if isinstance(input, dict):
            try:
                return {self.convert(key): self.convert(value) for key, value in input.iteritems()}
            except AttributeError:
                return {self.convert(key): self.convert(value) for key, value in input.items()}
        elif isinstance(input, list):
            return [self.convert(element) for element in input]
        elif isinstance(input, str) or isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input

    # json_dictionary, list(), dict()
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

    def get_nested_dictionary(self, file):

        if 'json' in file[-4:]:
            json_data = json.loads(open(file, "r").read())
            return json_data

        if any(x in file[-4:] for x in ['yml', 'yaml']):
            with open(file, 'r') as stream:
                try:
                    i18n_key_values_yml = yaml.load(stream)
                    return i18n_key_values_yml
                except yaml.YAMLError as exc:
                    print(exc)

        if 'csv' in file[-4:]:

            with open(file, mode='r') as infile:
                reader = csv.reader(infile)
                mydict = dict(row[:2] for row in reader if row)
            return mydict

    """
    Base methods for move, find, remove command
    and
    find-new source
    """

    def makeoutputdir(self):
        desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop', 'Output_Qordoba')
        try:
            os.makedirs(desktop)
            return desktop
        except OSError:
            return desktop
            pass

    def get_content_type_code(self, path):
        extension = path.split('.')[-1]
        if extension not in ALLOWED_EXTENSIONS:
            raise FileExtensionNotAllowed("File format `{}` not in allowed list of file formats: {}"
                                          .format(extension, ', '.join(ALLOWED_EXTENSIONS)))
        return ALLOWED_EXTENSIONS[extension]


    def find_files_by_pattern(self, curpath, pattern):

        for path in glob.iglob(pattern):

            if os.path.isdir(path):
                continue
            _ = self.get_content_type_code(path)

            yield path


    def delete_keys_from_dict(self, dict_del, lst_keys):
        for k in lst_keys:
            try:
                del dict_del[k]
            except KeyError:
                pass

        for v in dict_del.values():
            if isinstance(v, dict):
                self.delete_keys_from_dict(v, lst_keys)

        return dict_del


    def get_line(self, filepath, i18n_keys_values):
        try:
            for i, line in enumerate(open(filepath)):
                for key, _ in i18n_keys_values.items():

                    Rails_tokenz = [
                        str('I18n.t' + "('" + str(key) + "')"),
                        str('I18n.t' + " '" + str(key) + "'"),
                        str('t("' + str(key) + '")'),
                    ]

                    for token in Rails_tokenz:
                        if token in line:
                            if token not in OUTPUT:
                                OUTPUT.setdefault(token, {})
                            if filepath not in OUTPUT[token]:
                                OUTPUT[token][filepath] = []
                            OUTPUT[token][filepath].append(i + 1)
        except UnicodeDecodeError:
            print("UnicodeDecodeError. File: {}".format(filepath))
            pass

    def find_keys_in_project(self, i18n_keys_values, i18n_app_path):

        if os.path.isdir(i18n_app_path[0]):
            for subdir, dirs, files in os.walk(i18n_app_path[0]):
                for file in files:
                    if file in IGNOREFILES:
                        continue
                    filepath = subdir + os.sep + file
                    self.get_line(filepath, i18n_keys_values)
            return OUTPUT
        elif os.path.isfile(i18n_app_path[0]):
            filepath = i18n_app_path[0]
            self.get_line(filepath, i18n_keys_values)
            return OUTPUT
        else:
            print("Can't process {} \n".format(i18n_app_path[0]))

    def deepdelete(self, branch, keys):

        if len(keys) > 1:
            empty = self.deepdelete(branch[keys[0]], keys[1:])
            if empty:
                del branch[keys[0]]
        else:
            try:
                del branch[keys[0]]
            except KeyError:
                pass
        return branch

    def iterate_dict(self, data, keyword):

        data = self.deepdelete(data, keyword)
        for key in data.keys():
            value_ = data.get(key)
            if isinstance(value_, dict):
                self.iterate_dict(value_, keyword)
            else:
                continue

        return data

    def get_i18n_dictionary(self, file):

        if 'json' in file[-4:]:
            json_data = open(file)

            i18n_key_values_json = self.get_all_keys(json.load(json_data), list(), dict())
            return i18n_key_values_json

        if any(x in file[-4:] for x in ['yml', 'yaml']):
            with open(file, 'r') as stream:
                try:
                    i18n_key_values_yml = self.get_all_keys(yaml.load(stream), list(), dict())
                    return i18n_key_values_yml
                except yaml.YAMLError as exc:
                    print(exc)

        if 'csv' in file[-4:]:

            with open(file, mode='r') as infile:
                reader = csv.reader(infile)
                mydict = dict(row[:2] for row in reader if row)
            return mydict

    def write_results_to_outputJSON(self, output, filename):

        timestamp = datetime.datetime.now().isoformat()
        file, _  = filename.split('.')
        outputdir = self.makeoutputdir()
        output_file = outputdir + '/i18n_find_' + str(timestamp) + '.yml'

        if output == {}:
            output = 'Nothing found'
        with open(output_file, 'w') as outfile:
            yaml.dump("timestamp: " + timestamp, outfile, default_flow_style=False)
            yaml.dump("localization file: " + filename, outfile, default_flow_style=False)
            yaml.dump(output, outfile, default_flow_style=False)
        log.info('Done. Find results in `Desktop/Output_Qordoba/...`')
        return

    def write_to_output(self, file, result, command):

            filename = file.split('/')[-1]
            timestamp = datetime.datetime.now().isoformat()
            outputdir = self.makeoutputdir()
            output_filename = outputdir + '/' + str(timestamp) + command + filename

            if 'json' in file[-4:]:
                with open(output_filename, "w") as jsonFile:
                    json.dump(result, jsonFile, sort_keys=True, indent=4, separators=(',', ': '))

            if any(x in file[-4:] for x in ['yml', 'yaml']):

                with open(output_filename, "w") as ymlFile:
                    yaml.dump(result, ymlFile, default_flow_style=False, explicit_start=True,
                              allow_unicode=True)

            if 'csv' in file[-4:]:
                # NOTE: keys have to be in first row of csv
                with open(output_filename, 'wb') as myfile:
                    pass
                result.to_csv(output_filename, sep='\t', encoding='utf-8', index=False, header=False)

            log.info('\n Created new i18n file in folder `./output/{}`'.format(command))