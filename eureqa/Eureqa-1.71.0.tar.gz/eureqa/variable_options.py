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
import missing_value_policies


class VariableOptions(object):
    """Represents a set of settings for a variable that can be included into a search. Overrides any default behavior for
    the specified variable.

    :param str name: The name of the variable. It is the same as a column name in the list of data source columns.
    :param str missing_value_policy: A policy name for the processing of missing values. One of the values from missing_value_policies module can be used.
    :param bool remove_outliers_enabled: Enables removal of rows which contain outlier.
    :param float outlier_threshold: Controls the threshold for whether a point is considered an outlier. A higher value means points must be further from the mean to be considered outliers.  Default value is 2.0.
    :param bool normalize_enabled: Enables normalization of the variable. If True, each value tranformed via the expression (value - normalization_offset) / normalization_scale
    :param int normalization_offset: A constant offset value to subtract from each value. Defaults to 0 if not specified.
    :param int normalization_scale: A constant factor to divide each value after subtracting the normalization offset. Defaults to 1 if not specified.
    :param int min_delay: The number of time increments into the future to predict with a time series search.

    :var str ~VariableOptions.name: The name of the variable. It is the same as a column name in the list of data source columns.
    :var bool missing_values_enabled: Enables additional processing of missing values.
    :var str missing_value_policy: A policy name for the processing of missing values. One of the values from
        missing_value_policies module can be used. missing_value_policies.column_mean is used if the additional
        processing of missing values is enabled but no policy name provided.
    :var float outlier_threshold: The threshold at which a point is considered an outlier and will be removed.
    """

    def __init__(self, name=None, missing_value_policy=missing_value_policies.column_iqm,
                 remove_outliers_enabled=False, outlier_threshold=None, normalize_enabled=False,
                 normalization_offset=None, normalization_scale=None, min_delay=None, _update_parent_settings=None):

        self.missing_value_policy = missing_value_policy

        self.remove_outliers_enabled = remove_outliers_enabled
        self.outlier_threshold = outlier_threshold

        self.normalize_enabled = normalize_enabled
        if normalize_enabled and normalization_offset is None:
            self.normalization_offset = '<none>'
        else:
            self.normalization_offset = normalization_offset

        if normalize_enabled and normalization_scale is None:
            self.normalization_scale = '<none>'
        else:
            self.normalization_scale = normalization_scale

        self._min_delay = min_delay

        self.name = name

        self._filter_enabled = False
        self._filter_expression = None

        self._update_parent_settings = _update_parent_settings


    @property
    def min_delay(self):
        return self._min_delay
    @min_delay.setter
    def min_delay(self, val):
        self._min_delay = val
        if self._update_parent_settings is not None:
            self._update_parent_settings()

    def _set_filter(self, filter_enabled, filter_expression):
        # It is more appropriate to expose filter properties as a search options, not variable options.
        # Therefore they are not exposed as public fields. But we have to keep them at this level
        # because that's what the backend expects.
        self._filter_enabled = filter_enabled
        self._filter_expression = filter_expression

    def _to_json(self):
        body = {'variable_name': self.name}

        if self._filter_expression:
            body['filter_enabled'] = True
            body['filter_expression'] = self._filter_expression
        else:
            body['filter_enabled'] = False

        if self.missing_value_policy:
            body['missing_value_policy'] = self.missing_value_policy

        if self.outlier_threshold:
            body['outlier_threshold'] = self.outlier_threshold

        body['remove_outliers_enabled'] = self.remove_outliers_enabled

        if self.normalization_offset:
            body['normalize_enabled'] = True
            body['normalize_offset'] = self.normalization_offset
            body['normalize_scale'] = self.normalization_scale
        else:
            body['normalize_enabled'] = False

        if self.min_delay is not None:
            body['min_delay'] = self.min_delay
        return body

    def __from_json(self, body):
        self.name = body['variable_name']
        self.missing_value_policy = body.get('missing_value_policy')
        self.remove_outliers_enabled = body.get('remove_outliers_enabled')
        self.outlier_threshold = body.get('outlier_threshold')
        self.normalize_enabled = body.get('normalize_enabled')
        self.normalization_offset = body.get('normalize_offset')
        self.normalization_scale = body.get('normalize_scale')
        self._filter_enabled = body.get('filter_enabled')
        self._filter_expression = body.get('filter_expression')
        self._min_delay = body.get('min_delay')
        self._body = body

    @classmethod
    def _from_json(cls, body, _update_parent_settings=None):
        variableOptions = VariableOptions(_update_parent_settings=_update_parent_settings)
        variableOptions.__from_json(body)
        return variableOptions

    def __eq__(self, other):
        if not isinstance(other, VariableOptions):
            return False
        return (self.name == other.name
                and self.missing_value_policy == other.missing_value_policy
                and self.remove_outliers_enabled == other.remove_outliers_enabled
                and self.outlier_threshold == other.outlier_threshold
                and self.normalize_enabled == other.normalize_enabled
                and self.normalization_offset == other.normalization_offset
                and self.normalization_scale == other.normalization_scale
                and self._filter_enabled == other._filter_enabled
                and self._filter_expression == other._filter_expression
                and self.min_delay == other.min_delay)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        tpl = (self.missing_value_policy, self.remove_outliers_enabled,
               self.outlier_threshold, self.normalize_enabled, self.normalization_offset, self.normalization_scale,
               self._filter_enabled, self._filter_expression, self.name, self.min_delay)
        return hash(tpl)

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)
