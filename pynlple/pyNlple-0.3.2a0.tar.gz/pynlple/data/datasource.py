# -*- coding: utf-8 -*-
import io
import json

from pandas import DataFrame
from pandas import read_csv, read_json

from pynlple.data.source import Source


class DataframeSource(Source):

    def __init__(self, dataframe):
        self.dataframe = dataframe

    def get_dataframe(self):
        return self.dataframe

    def set_dataframe(self, dataframe):
        self.dataframe = dataframe


class TsvDataframeSource(Source):

    def __init__(self, dataframe_path, separator='\t', quote=0, escape_char='\\', column_names=None, fill_na_map=None, encoding='utf-8', index_columns=None):
        self.path = dataframe_path
        self.separator = separator
        self.column_names = column_names
        self.na_map = fill_na_map
        self.encoding = encoding
        self.index_columns = index_columns
        self.quote = quote
        self.escape_char = escape_char

    def get_dataframe(self):
        #TODO: Eats \r\n and spits sole \n in literal value strings instead
        if self.column_names:
            header = None
            names = self.column_names
        else:
            header = 'infer'
            names = None
        dataframe = read_csv(self.path,
                             sep=self.separator,
                             header=header,
                             names=names,
                             quoting=self.quote,
                             escapechar=self.escape_char,
                             encoding=self.encoding)
        if self.index_columns:
            dataframe.set_index(keys=self.index_columns, inplace=True)
        if self.na_map:
            for key, value in self.na_map.items():
                dataframe[key].fillna(value, inplace=True)
        print('Read: ' + str(len(dataframe.index)) + ' rows from ' + self.path)
        return dataframe

    def set_dataframe(self, dataframe):
        if self.column_names:
            names = self.column_names
        else:
            names = True
        dataframe.to_csv(self.path,
                         sep=self.separator,
                         header=names,
                         quoting=self.quote,
                         escapechar=self.escape_char,
                         encoding=self.encoding)
        print('Write: ' + str(len(dataframe.index)) + ' rows to ' + self.path)


class JsonFileDataframeSource(Source):

    FILE_READ_METHOD = 'rt'
    FILE_WRITE_METHOD = 'wt'
    DEFAULT_ENCODING = 'utf-8'

    def __init__(self, json_file_path, fill_na_map=None, index_columns=None):
        self.json_file_path = json_file_path
        self.na_map = fill_na_map
        self.index_columns = index_columns

    def get_dataframe(self):
        with io.open(self.json_file_path, JsonFileDataframeSource.FILE_READ_METHOD, encoding=JsonFileDataframeSource.DEFAULT_ENCODING) as data_file:
            df = read_json(data_file, orient='records', encoding=JsonFileDataframeSource.DEFAULT_ENCODING)
        return df

    def set_dataframe(self, dataframe):
        with io.open(self.json_file_path, JsonFileDataframeSource.FILE_WRITE_METHOD, encoding=JsonFileDataframeSource.DEFAULT_ENCODING) as data_file:
            json.dump(dataframe.reset_index().to_dict(orient='records'), data_file, ensure_ascii=False, indent=2)


class JsonDataframeSource(Source):

    def __init__(self, json_source, keys=None, fill_na_map=None, index_columns=None):
        self.json_source = json_source
        self.keys = keys
        self.na_map = fill_na_map
        self.index_columns = index_columns

    def get_dataframe(self):
        extracted_entries = list()
        for json_object in self.json_source.get_data():
            entry = dict()
            if self.keys:
                for key in self.keys:
                    if key not in json_object:
                        entry[key] = self.na_map[key]
                    else:
                        entry[key] = json_object[key]
            else:
                for key in json_object:
                    entry[key] = json_object[key]
                if self.na_map:
                    for key, value in self.na_map:
                        if key not in entry:
                            entry[key] = value
            extracted_entries.append(entry)
        dataframe = DataFrame(extracted_entries)
        if self.index_columns:
            dataframe.set_index(keys=self.index_columns, inplace=True)
        if self.na_map:
            for key, value in self.na_map.items():
                dataframe[key].fillna(value, inplace=True)
        print('Read: ' + str(len(dataframe.index)) + ' rows from jsonsource')
        return dataframe

    def set_dataframe(self, dataframe):
        entries = dataframe.reset_index().to_dict(orient='records')
        for entry in entries:
            if self.keys:
                for key in list(entry.keys()):
                    if key not in self.keys:
                        entry.pop(key, None)
            if self.na_map:
                for key, value in self.na_map:
                    if key not in entry:
                        entry[key] = value
        self.json_source.set_data(entries)

