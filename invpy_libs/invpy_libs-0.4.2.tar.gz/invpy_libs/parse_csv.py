#!/usr/bin/python3
import io
import os
import csv
import itertools
import codecs
from urllib import request

def csv_as_dict(file, ref_header, delimiter=";", encoding='utf-8'):
    """
    http://stackoverflow.com/questions/14091387/creating-a-dictionary-from-a-csv-file
    :param file: Input csv file
    :param ref_header: Column name reference for each key
    :param delimiter: separator to read the csv

    :return: dict with csv content, first row with headers in lowercase
    """

    def lower_first(iterator):
        """
        Function to make first row lower
        """
        return itertools.chain([next(iterator).lower()], iterator)

    reader = csv.DictReader(lower_first(codecs.open(file, mode='r', encoding=encoding,
                                                    errors='replace')),
                            delimiter=delimiter,
                            skipinitialspace=True)
    result = {}
    for row in reader:
        key = row.pop(ref_header.lower())
        if key in result:
            # implement your duplicate row handling here
            pass
        result[key] = row
    return result


def save_csv_data(csv_rows=None, csv_filename='test.csv', csv_delimiter=',', encoding='utf-8'):
    """

    :param csv_rows: python list with rows
    :param csv_filename: output file
    :param csv_delimiter: output separator to use as delimiter
    :return: None
    """
    if not csv_filename:
        return 'No csv_file selected'
    if not csv_rows:
        return 'There are no csv rows to write'
    print('saving to csv file:', csv_filename)
    csv_file_obj = open(csv_filename, 'w', newline='', encoding=encoding)
    csv_writer = csv.writer(csv_file_obj, delimiter=csv_delimiter)
    for row in csv_rows:
        csv_writer.writerow(row)
    csv_file_obj.close()
    if csv_filename:
        if os.path.isfile(csv_filename):
            print('exported to:', csv_filename)


def get_csv_from_url(csv_url, csv_output='output.csv', delimiter=',', encoding='utf-8'):
    """

    :param csv_url: url to get the csv
    :param csv_output: path to output the csv
    :param delimiter: delimiter of the csv
    :return:
    """
    url = csv_url
    try:
        response = request.urlopen(url)
    except:
        return None
    # Read csv from urlopen
    datareader = csv.reader(io.TextIOWrapper(response, encoding=encoding), delimiter=delimiter)
    save_csv_data(datareader, csv_filename=csv_output, csv_delimiter=delimiter)
    if os.path.isfile:
        return "file saved to: ", csv_output
