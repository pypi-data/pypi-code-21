import csv
import json
from collections import OrderedDict


class CsvJson:
    def __init__(self, sort_columns=False, pretty_print = False):
        self.sort_columns = sort_columns
        self.indent = 4 if pretty_print else None

    def convert(self, csv_data):
        reader = csv.DictReader(csv_data, delimiter=",")
        rows = []
        for row in reader:
            if self.sort_columns:
                rows.append(row)
            else:
                unsorted_row = OrderedDict(sorted(row.items(),
                                                  key=lambda item: reader.fieldnames.index(item[0])))
                rows.append(unsorted_row)
        return json.dumps(rows, sort_keys=self.sort_columns, indent=self.indent)
