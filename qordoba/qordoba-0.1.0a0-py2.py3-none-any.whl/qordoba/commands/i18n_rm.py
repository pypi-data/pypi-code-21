from qordoba.settings import get_localization_files
import json
import yaml
import pandas as pd
import logging
import datetime
import os

from qordoba.commands.i18n_base import BaseClass, FilesNotFound, FileExtensionNotAllowed
log = logging.getLogger('qordoba')

class RemoveClass(BaseClass):
    """
    The remove command will execute 2 steps
    1. It will match all keys within the localization files containing the keyword
    2. removes all keys, corresponding leaves and creates a new file with updated dictionary
    """
    def i18n_remove_command(self, curdir, config, keyword=None):
        command = 'i18n_remove'
        pattern = get_localization_files(config)
        files = []
        for file_path in pattern:

            if '*' in file_path:
                file_list = list(self.find_files_by_pattern(curdir, file_path))
                for k in file_list:
                    files.append(k)
                if not files:
                    raise FilesNotFound('Files not found by pattern `{}`'.format(pattern))
            else:
                files.append(file_path)

            for file in files:  # JSON, YML, CSV, PO
                filename = file.split('/')[-1]
                timestamp = datetime.datetime.now().isoformat()
                outputdir = self.makeoutputdir()
                output_filename = outputdir + '/' + filename + '_' + str(timestamp)

                if 'json' in file[-4:]:
                    json_data = open(file)
                    json_dictionary = json.load(json_data)
                    #filteres out dictionary by given keyword
                    filtered_dict = self.iterate_dict(json_dictionary, keyword)

                    with open(output_filename + '.json', "w") as jsonFile:
                        log.info('Removed all keys with keyword `{}` from file {}'.format(keyword[0], file))
                        json.dump(filtered_dict, jsonFile, sort_keys=True, indent=4, separators=(',', ': '))

                if any(x in file[-4:] for x in ['yml', 'yaml']):
                    with open(file, 'r') as yml_file:
                        yaml_data = yaml.safe_load(yml_file)
                        try:
                            print(yaml_data)
                            filtered_dict = self.iterate_dict(yaml_data, keyword)
                            with open(output_filename + '.yml', "w") as ymlFile:
                                log.info('Removed all keys with keyword `{}` from file {}'.format(keyword[0], file))
                                yaml.dump(filtered_dict, ymlFile, default_flow_style=False, explicit_start=True, allow_unicode=True)

                        except yaml.YAMLError as exc:
                            print(exc)

                if 'csv' in file[-4:]:
                    #NOTE: keys have to be in first row of csv
                    df = pd.read_csv(file, header=None)
                    df_filterd =  df[df[0].str.contains(keyword[0]) == False]
                    with open(output_filename + '.csv', 'wb') as myfile:
                        pass
                    df_filterd.to_csv(output_filename, sep='\t', encoding='utf-8', index=False, header=False)
                    log.info('Removed all keys with keyword `{}` from file {}'.format(keyword[0], file))

                log.info('Done. Find updated localizations file in `~/Desktop/Output_Qordoba/filename`')