from numbers import Number
from collections import defaultdict

def to_csv(response, **kwargs):
    keen_csv = KeenCSV(response, **kwargs)
    return keen_csv.generate_csv()

class KeenCSV(object):
    def __init__(self, raw_response, delimiter = ',', filteredColumns = None, delimiterSub = '.', nestedDelimiter = '.'):
        self.raw_response    = raw_response
        self.delimiter       = delimiter
        self.delimiterSub    = delimiterSub
        self.nestedDelimiter = nestedDelimiter
        self.filteredColumns = filteredColumns

    def generate_csv(self):
        """Generates a CSV from the input raw_response"""
        result_columns = self._generate_result_columns()
        headers = result_columns['columns'].keys()

        csv = self.delimiter.join(headers)

        for row_index in range(0, result_columns['max_row_index'] + 1, 1):
            csv += "\r\n"
            csv += self.delimiter.join([ self._filter_value(result_columns['columns'][column].get(row_index)) for column in headers])

        return csv

    def _generate_result_columns(self):
        """Pivots the raw_response into colums, to account for any data gaps"""
        result_columns = {
            "columns": defaultdict(dict),
            "max_row_index": 0
        }

        def set_column_value(column, row_index, value):
            if (not isinstance(self.filteredColumns, list) or column not in self.filteredColumns):
                result_columns["columns"][column][row_index] = value
                if row_index > result_columns["max_row_index"]:
                    result_columns["max_row_index"] = row_index

        # return early if this is a simple count
        if isinstance(self.raw_response, Number):
            set_column_value('result', 0, self.raw_response)
            return result_columns

        row_index = 0
        for obj in self.raw_response:
            if isinstance(obj.get('value'), list):
                for group in obj['value']:
                    flattened = self._flatten(group)
                    [ set_column_value(column, row_index, flattened[column]) for column in flattened ]
                    if obj['timeframe']:
                        flattened = self._flatten({"timeframe": obj['timeframe']})
                        [ set_column_value(column, row_index, flattened[column]) for column in flattened ]
                    row_index += 1
            else:
                flattened = self._flatten(obj)
                [ set_column_value(column, row_index, flattened[column]) for column in flattened ]
                row_index += 1

        return result_columns

    def _filter_value(self, value):
        """Takes a string value, and sanitizes it for CSV"""
        if value is None:
            return ''
        return str(value).replace(self.delimiter, self.delimiterSub)

    def _flatten(self, obj, flattened = None, prefix = ""):
        """Recursively traverses nested lists/dictionaries and flattens them with a delimiter

        Arguments:
        obj -- the Dictionary or List of objects to be flattened

        Keyword arguments:
        flattened -- for recursion use only.
        prefix    -- for recursion use only.
        """

        if flattened is None:
            flattened = {}

        loopable = obj if isinstance(obj, dict) else xrange(len(obj))
        for key in loopable:
            if isinstance(loopable[key], list) or isinstance(loopable[key], dict):
                self._flatten(loopable[key], flattened, prefix + self._filter_value(key) + self.nestedDelimiter)
            else:
                flattened[prefix + self._filter_value(key)] = loopable[key]
        return flattened
