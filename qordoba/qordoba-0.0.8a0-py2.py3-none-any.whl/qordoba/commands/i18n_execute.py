from qordoba.commands.i18n_base import BaseClass
import pandas as pd
import os
import logging
log = logging.getLogger('qordoba')


class ReportNotValid(Exception):
    """
    Files not found
    """

class i18nExecutionClass(BaseClass):

    def __init__(self):
        self.next = False

    def final_replace(self, key_type, picked_line, v):
        picked_line_1 = picked_line.replace("'" + v['text'].strip() + "'", "${" + v[key_type].strip() + "}")
        picked_line_2 = picked_line_1.replace('"' + v['text'].strip() + '"', "${" + v[key_type].strip() + "}")
        picked_line_3 = picked_line_2.replace(v['text'].strip(), "${" + v[key_type].strip() + "}")
        return picked_line_3
    # file is list of strings. replaces strings in list
    def replace_strings_for_keys(self, df_to_dict, file_array):
        # Python 2
        for k, v in self.iterate_items(df_to_dict):
            idx_start = v['startLineNumber']
            idx_end = v['endLineNumber']
            if idx_start == idx_end:
                picked_line = file_array[idx_start]
                # replaces with html keys. "STRING" -->  ${KEY}
                if v['existing_keys'] is None:
                    replaced_line = self.final_replace('generated_keys', picked_line, v)
                else:
                    replaced_line = self.final_replace('existing_keys', picked_line, v)
                file_array[idx_start] = replaced_line

            if idx_start < idx_end:
                picked_lines = list()
                for i in range(idx_start, idx_end):
                    picked_lines.append(file_array[i])
                if v['filename'][-4:] == 'html':
                    joined_lines = ''.join(picked_lines)
                else:
                    joined_lines = '\n'.join(picked_lines)

                if v['existing_keys'] is None:
                    replaced_line = self.final_replace('generated_keys', joined_lines, v)
                else:
                    replaced_line = self.final_replace('existing_keys', joined_lines, v)

                file_array[idx_end] = replaced_line

                for i in range(idx_start, idx_end):
                    file_array[i] = None

        file_array_list = list()
        # print(max(map(int, file_array)))
        for i in range(len(file_array)):
            idx = i + 1
            file_array_list.append(file_array[idx])

        return file_array_list

    # loads file into list. Items of list are lines in file
    def get_filerows_as_list(self, file_path):
        file_dict = {}
        count= 0
        try:
            with open(file_path, "r") as ins:
                for line in ins:
                    count += 1
                    if file_path[-4:] == 'html':
                        file_dict[count] = line.replace("'", "")
                    else:
                        file_dict[count] = line
            return file_dict
        except IOError:
            print("File '{}' does not exist.".format(file_path))
            pass

    def execute(self, curdir, report, directory, output):
        output = str(output).strip()
        report = str(report).strip()
        directory = str(directory).strip()
        if report[-1] == '/':
            report = report[:-1]
        if output[-1] == '/':
            output = output[:-1]

        reports = self.get_files_in_Dir(report)
        reports_file_path = [report + '/' + x for x in reports if x.endswith('.csv')]
        for report_path in reports_file_path:

            if not self.validate_report(report_path, keys=True):
                raise ReportNotValid("The given report is not valid. ")

            df_nan = pd.read_csv(report_path)
            df = df_nan.where((pd.notnull(df_nan)), None)
            files = list()
            for index, row in df.iterrows():
                files.append(row.filename)

            # batch lines in report with same filepath, apply replace
            files_in_report = set(files)
            for file_in_report in files_in_report:
                log.info("Replacing strings with keys in `{}`.".format(file_in_report))
                project_file_path = directory + file_in_report[11:]
                df_single_file = df[df.filename == file_in_report]
                df_to_dict = df_single_file.T.to_dict()
                file_dict = self.get_filerows_as_list(project_file_path)
                try:
                    if len(file_dict) == 0:
                        print('File {} is empty'.format(file_in_report))
                        continue
                except TypeError:
                    print('File {} is empty'.format(file_in_report))
                    continue
                new_file_dict = self.replace_strings_for_keys(df_to_dict, file_dict)
                new_file_dict_1 = [x for x in new_file_dict if x != None]

                # remove old file, dump new
                os.remove(project_file_path)
                print("THIS IS A NEW FILE AND I DONT KNOW WHY ITS NOT WORKING")
                print(new_file_dict_1)
                Html_file = open(project_file_path, "w")
                if project_file_path[-4:] == 'html':
                    ''.join(new_file_dict_1)
                Html_file.write("".join(new_file_dict_1))
                Html_file.close()


            # create localization file in output folder
            if output[-1] == '/':
                report = output[:-1]
            new_localization_file = output + '/qordoba_localization_file.json'
            # WTF! NEEDS REFACTURING
            del df['filename']
            del df['startLineNumber']
            del df['startCharIdx']
            del df['endLineNumber']
            del df['endCharIdx']
            del df['existing_localization_file']
            json_dump = dict()
            for index, row in df.iterrows():
                if row['existing_keys'] is None:
                    json_dump[row['generated_keys']]  = row['text']
                else:
                    json_dump[row['existing_keys']] = row['text']

            import json
            with open(new_localization_file, "w") as jsonFile:
                json.dump(json_dump, jsonFile, sort_keys=True, indent=4, separators=(',', ': '))