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


import json
from datetime import datetime

class VariableDetails:
    """Holds information about a variable. Obtained through the :py:meth:`~eureqa.data_source.DataSource.get_variable_details` method
    of a :py:class:`~eureqa.data_source.DataSource` . Use this class to find mathematic properties of a variable and to change a variable's
    name.

    :var str `~eureqa.variable.VariableDetails.name`: The name of the variable.
    :var str `~eureqa.variable.VariableDetails.expression`: The expression used to create the variable if it is a custom or seasonal variable
    :var float/datetime `~eureqa.variable.VariableDetails.min_value`: The smallest value. Will be a datetime if datatype is 'datetime'.
    :var float/datetime `~eureqa.variable.VariableDetails.max_value`: The largest value. Will be a datetime if datatype is 'datetime'.
    :var float/datetime `~eureqa.variable.VariableDetails.mean_value`: The mean value. Will be a datetime if datatype is 'datetime'.
    :var float `~eureqa.variable.VariableDetails.standard_deviation`: The standard deviation of the values.
    :var int `~eureqa.variable.VariableDetails.distinct_values`: The number of distinct values.
    :var int `~eureqa.variable.VariableDetails.missing_values`: The number of missing values.
    :var int `~eureqa.variable.VariableDetails.total_rows`: The total rows occupied by the variable.
    :var str `~eureqa.variable.VariableDetails.datatype`: Whether it is a binary or numeric variable
    :var int `~eureqa.variable.VariableDetails.num_zeroes`: The number of zero values.
    :var int `~eureqa.variable.VariableDetails.num_ones`: The number of one values.
    :var str `~eureqa.variable.VariableDetails.derivation_type`: From where this variable originated. Valid values are 'original' for variables from the original dataset, 'custom' for `custom derived variables <https://help.nutonian.com/topics/deriving-a-new-variable>`_, or 'seasonal' for `seasonal variables <https://help.nutonian.com/topics/seasonality-variable>`_.
    :var str `~eureqa.variable.VariableDetails.seasonal_target_variable`: For seasonal variables, what variable was the target used to derive the seasonal trend. None for other types of variables
    :var str `~eureqa.variable.VariableDetails.seasonal_period`: For seasonal variables, over what period was the seasonal trend derived. None for other types of variables
    :var `~eureqa.data_source.DataSource` `~eureqa.variable_details.VariableDetails.data_source`: The DataSource the VariableDetails belongs to
    """

    def __init__(self, body, data_source):
        """For internal use only
        PARAM_NOT_EXTERNALLY_DOCUMENTED
        """

        self._id = body['variable_id']
        self.name = body['variable_name']
        self.expression = body.get('expression')
        self.standard_deviation = body['standard_deviation']
        self.distinct_values = body['distinct_values']
        self.missing_values = body['missing_values']
        self.num_zeroes = body['num_zeros']
        self.total_rows = body['total_rows']
        self.datatype = body['datatype']
        self._min_value = body['min_value']
        self._max_value = body['max_value']
        self._mean_value = body['mean_value']
        self.num_ones = body.get('num_ones')
        self.data_source = data_source
        self.derivation_type = body['type']
        self.seasonal_target_variable = body.get('seasonal_target_variable')
        self.seasonal_period = body.get('seasonal_period')
        self._body = body

    def _to_json(self):
        body = {
            'variable_id' : self._id,
            'variable_name' : self.name,
            'expression' : self.expression,
            'min_value' : self._min_value,
            'max_value' : self._max_value,
            'mean_value' : self._mean_value,
            'standard_deviation' : self.standard_deviation,
            'distinct_values' : self.distinct_values,
            'missing_values' : self.missing_values,
            'num_zeros' : self.num_zeroes,
            'total_rows' : self.total_rows,
            'datatype' : self.datatype,
            'num_ones' : self.num_ones,
            'datasource_id' : self.data_source._data_source_id,
            'type' : self.derivation_type,
            'seasonal_target_variable': self.seasonal_target_variable,
            'seasonal_period': self.seasonal_period
        }
        return body

    def __str__(self):
        body = self._to_json()
        body['min_value'] = self._get_formatted_value(self._min_value, True)
        body['max_value'] = self._get_formatted_value(self._max_value, True)
        body['mean_value'] = self._get_formatted_value(self._mean_value, True)
        return json.dumps(body, indent=4)

    def _get_formatted_value(self, val, dates_as_strings=False):
        if self.datatype == 'datetime':
            date = datetime.utcfromtimestamp(val/1000)
            if dates_as_strings:
                return str(date)
            return date
        return val

    @property
    def min_value(self):
        return self._get_formatted_value(self._min_value)

    @property
    def max_value(self):
        return self._get_formatted_value(self._max_value)

    @property
    def mean_value(self):
        return self._get_formatted_value(self._mean_value)


class SeasonalVariableDetails(VariableDetails):
    def __init__(self, body, data_source):
        """For internal use only
        PARAM_NOT_EXTERNALLY_DOCUMENTED
        """

        VariableDetails.__init__(self, body, data_source)
        self.seasonal_target_variable = body['seasonal_target_variable']
        self.seasonal_period = body['seasonal_period']

    def _to_json(self):
        body = VariableDetails._to_json()

class Variable(VariableDetails):
    def __init__(*args, **kwargs):
        warnings.warn("Class 'Variable' has been renamed to 'VariableOptions'", DeprecationWarning)
        super(Variable, self).__init__(*args, **kwargs)
