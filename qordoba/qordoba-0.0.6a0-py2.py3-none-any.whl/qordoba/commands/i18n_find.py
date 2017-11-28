import json
import yaml
import pandas as pd
import logging
import datetime

log = logging.getLogger('qordoba')

from qordoba.settings import get_localization_files, get_i18n_app_pattern
from qordoba.commands.i18n_base import BaseClass, FilesNotFound

class FindClass(BaseClass):
    """
    The find command executes in 3 major consecutive steps
    1. the localization file is identified. Given keyword is matched with keys within the localization file, batch of keys found are temp stored
    2. iterate through project file by file looking for matching i18n keys.
    3. Writing found keys, occurrences/ location into output file
    """

    def i18n_find_command(self, curdir, config, keyword=None):

        pattern = get_localization_files(config)
        i18n_app_path = get_i18n_app_pattern(config)
        files = []

        for file_path in pattern:
            # collecting all given files in directory
            log.info('Scanning {} for keys in {}'.format(i18n_app_path[0], file_path))
            if '*' in file_path:
                file_list = list(self.find_files_by_pattern(curdir, file_path))
                for k in file_list:
                    files.append(k)
                if not files:
                    raise FilesNotFound('Files not found by pattern `{}`'.format(pattern))
            else:
                files.append(file_path)

            # each localization fileformat is treated differently. Currently supported JSON, YML, CSV
            for file in files:
                filename = file.split('/')[-1]
                if 'json' in file[-4:]:
                    json_data = open(file)
                    # getting all keys from localization file
                    i18n_key_values_json = self.get_all_keys(json.load(json_data), list(), dict())
                    # filtering all keys if match with keyword
                    filtered_dict = {k: i18n_key_values_json[k] for k in i18n_key_values_json if keyword[0] in k}
                    log.info('Found keys: {}'.format(filtered_dict))
                    # iterating through project. Save keys found plus occurrences/location
                    output = self.find_keys_in_project(filtered_dict, i18n_app_path)

                if any(x in file[-4:] for x in ['yml', 'yaml']):
                    with open(file, 'r') as stream:
                        try:
                            i18n_key_values_yml = self.get_all_keys(yaml.load(stream), list(), dict())
                            filtered_dict = {k: i18n_key_values_yml[k] for k in i18n_key_values_yml if keyword[0] in k}
                            log.info('Fround keys: {}'.format(filtered_dict))
                            output = self.find_keys_in_project(filtered_dict, i18n_app_path)
                        except yaml.YAMLError as exc:
                            print(exc)

                if 'csv' in file[-4:]:
                    df = pd.read_csv(file, header=None)
                    try:
                        df_filterd = df[df[0].str.contains(keyword[0]) == True]
                    except KeyError:
                        print('The key {} does not exsist in {}'.format(keyword[0], file))
                    df_filterd = pd.Series(df_filterd[1].values, index=df_filterd[0]).to_dict()
                    output = self.find_keys_in_project(df_filterd, i18n_app_path)
                    log.info('Fround keys: {}'.format(df_filterd.keys()))

                self.write_results_to_outputJSON(output, filename)
