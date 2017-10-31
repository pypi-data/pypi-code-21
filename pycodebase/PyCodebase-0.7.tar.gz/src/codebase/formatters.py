import csv
import json

from . import utils


class _Output(object):
    def __init__(self, columns, format_func, out_fh):
        """Columns is a list of column names that will be picked from the
        formatted data dict. format_func is called for each row, and must
        return a dictionary. fh is an open file handle, results are written to.
        """
        self.columns = columns
        self.format_func = format_func
        self.out_fh = out_fh


class JsonOutput(_Output):
    def __call__(self, records):
        data = [self.format_func(record) for record in records]
        json.dump(data, self.out_fh)

        return self.out_fh


class CsvOutput(_Output):
    def __call__(self, records):
        writer = csv.DictWriter(self.out_fh, self.columns, extrasaction='ignore')
        writer.writeheader()

        for record in records:
            out = self.format_func(record)
            out = utils.encode_dict(out)
            writer.writerow(out)

        self.out_fh


_formatters = {
    'json': JsonOutput,
    'csv': CsvOutput,
}


def get_formatter(name):
    return _formatters[name]
