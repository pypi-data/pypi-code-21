# Copyright (c) 2017, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the Nutonian Inc nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NUTONIAN INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from csv import DictReader
from datetime import datetime
from StringIO import StringIO
import uuid

from error_metric import ErrorMetrics

class ModelEvaluation(object):
    """ Represents the result of evaluting solutions and expressions.

    :var dict data: The dictionary, where keys are expressions and variable names, and values are columns of data.
    :var int num_future_rows: The number of future rows that are included in each data series.
    :var pandas.PandFrame frame: The Pandas frame, where column names are expressions and variable names.
    :var dict error_metrics: The dictionary where the keys are model strings for the provided solutions and expressions,
        and values are :py:class:`~eureqa.error_metric.ErrorMetrics` objects.

    """

    def __init__(self, body):
        """For internal use only
        PARAM_NOT_EXTERNALLY_DOCUMENTED
        """
        self._body = body
        self._columns = body.get('columns')
        self._csv_data = body.get('csv_data')
        self._datetime_column = body.get('datetime_column')
        self._series_id_column = body.get('series_id_column')
        self.num_future_rows = body.get('num_future_rows')

        error_metrics_array = [ErrorMetrics(_body=value) for value in body.get('error_metrics', [])]
        self.error_metrics = {value._model: value for value in error_metrics_array}

        self.data = {key: [] for key in self._columns}

        # When the evaluation returns only one column and first n rows have NaN-s,
        # then the first n rows of the csv appear as empty lines.
        # Inserting placeholder into each empty line so the DictReader passes through those lines.
        # Otherwise its default behaviour is to eliminate all empty lines.
        placeholder = str(uuid.uuid1())
        lines = self._csv_data.split('\n')
        new_lines = []
        for line in lines:
            if line == '':
                line = placeholder
            new_lines.append(line)
        new_lines.pop() # Backend always adds new line at the end which should not be treated as NaN.
        csv_data = '\n'.join(new_lines)

        for row in DictReader(StringIO(csv_data), fieldnames=self._columns):
            for key in self._columns:
                value = row[key]
                if value == placeholder:
                    # Restore the empty value
                    value = ''
                if key == self._datetime_column:
                    try:
                        value = datetime.strptime(row[key],'%m/%d/%Y %H:%M:%S')
                    except ValueError:
                        value = datetime.strptime(row[key],'%m/%d/%Y')
                elif key == self._series_id_column:
                    pass # Just keep it as string
                else:
                    value = float('nan') if not value else float(value)
                self.data[key].append(value)

    @property
    def frame(self):
        from pandas import DataFrame
        return DataFrame(self.data)

    def _apply_expression_mappings(self, mappings):
        for (original_expression, parsed_expression) in mappings.items():
            if original_expression == parsed_expression: continue
            self.data[original_expression] = self.data[parsed_expression]
            if parsed_expression in self.error_metrics:
                self.error_metrics[original_expression] = self.error_metrics[parsed_expression]
        # There could be multiple original expressions which map to the same parsed form.
        # Therefore the code above should not delete parsed expression key after the first use.
        # Because it can be reused multiple time.
        for (original_expression, parsed_expression) in mappings.items():
            if original_expression == parsed_expression: continue
            if parsed_expression in self.data:
                del self.data[parsed_expression]
            if parsed_expression in self.error_metrics:
                del self.error_metrics[parsed_expression]

