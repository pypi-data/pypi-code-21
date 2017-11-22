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

from error_metric import ErrorMetrics

import json

class Solution:
    """Represents one of the solutions found by the server for a particular search. Can be obtained from
    one of the methods in :py:class:`~eureqa.search.Search`. Some solutions may be available even if the
    search has not finished running.

    :var str `~eureqa.solution.Solution.target`: The target variable.
    :var str `~eureqa.solution.Solution.model`: The model expression.
    :var int `~eureqa.solution.Solution.complexity`: The model complexity based on the complexity weights.
    :var bool `~eureqa.solution.Solution.is_best`:
        An indicator whether the solution is considered to be the best based on its complexity and precision.
        The system can pick only one solution as best.
    :var bool `~eureqa.solution.Solution.is_most_accurate`:
        An indicator whether the solution is the most accurate for the optimized error metric.
        The system can pick only one solution as most accurate.
    :var str `~eureqa.solution.Solution.optimized_error_metric`:
        The error metric for which the solution was optimized.
        It is one of the error metrics from :mod:`~eureqa.error_metric`.
    :var float `~eureqa.solution.Solution.optimized_error_metric_value`: The value of the optimized error metric.
    :var ~eureqa.search.Search `~eureqa.solution.Solution.search`: The search object to which this solution belongs.
    """

    def __init__(self, body, eureqa, search=None):
        """For internal use only.
        PARAM_NOT_EXTERNALLY_DOCUMENTED
        """

        self._id = body['solution_id']
        self._search_id = body['search_id']
        self._datasource_id = body['datasource_id']
        self.target = body['target_variable']
        self.model = body['model_string']
        self.complexity = body['model_complexity']
        self.is_best = body['solution_type']['best']
        self.is_most_accurate = body['solution_type']['most_accurate']
        self._error_metrics = {x['metric_name']: x['metric_value'] for x in body['error_metric_values']}
        self.optimized_error_metric = body['model_optimized_error_metric']
        self.optimized_error_metric_value = body['model_optimized_error_metric_value']
        self._model_fitness = body['model_fitness']
        self._model_aic_parameters = body.get('model_aic_parameters')
        self.terms = [t['term_string'] for t in body['terms']]
        self._body = body
        self._eureqa = eureqa
        self._search_object = search

    def _to_json(self):
        body = {
            'target': self.target,
            'model': self.model,
            'complexity': self.complexity,
            'is_best': self.is_best,
            'is_most_accurate': self.is_most_accurate,
            'optimized_error_metric': self.optimized_error_metric,
            'optimized_error_metric_value': self.optimized_error_metric_value,
            'terms': self.terms
        }
        return body

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)

    def get_error_metric_value(self, name):
        """
        Returns the value for the specified error metric.

        :param str name: One of the error metrics from :mod:`~eureqa.error_metric`.
        :rtype: float
        """

        return self._error_metrics[name]

    def get_all_series_error_metrics(self, data_split='all'):
        """
        Returns the metric values for each series in the datasource.

        :param str data_split: For internal use only.

        :return: list of :class:`~eureqa.error_metric.ErrorMetrics` objects.
        :rtype: list
        """

        # Compatibility shim:
        # 'all' really means "all data"
        # 'usable' means "all non-reserved data", which is the same thing with an exception to handle history functions correctly and consistently.
        # 'all' used to mean 'usable', and 'usable' used to not exist.
        # So, translate here.
        if data_split == 'all':
            data_split = 'usable'

        result = self.search._eureqa._session.execute('/fxp/datasources/%s/searches/%s/solutions/%s/series_metrics?data_type=%s'% (self.search._data_source_id, self.search._id, self._id, data_split), 'GET')
        metrics_list = []
        for x in result:
            metrics = ErrorMetrics()
            metrics._from_json(x)
            metrics_list.append(metrics)
        return metrics_list

    def get_single_series_error_metrics(self, series=None, data_split='all', series_index=None):
        """
        Returns the metric values for the specified series in the datasource.

        :param int,str series: The series to compute the metrics on. If series is an integer, returns the error metrics for the series with that series index. Otherwise, returns the error metrics for the series with the specified series id value.
        :param str data_split: For internal use only.
        :param int series_index: Deprecated. Only kept for backwards compatibility. Do not use.
        :rtype: ErrorMetrics
        """

        assert series_index is None and series is not None or\
               series_index is not None and series is None

        if series_index is not None:
            series=series_index

        if isinstance(series, (int, long)):
            result = self.search._eureqa._session.execute('/fxp/datasources/%s/searches/%s/solutions/%s/series_metrics/%s?data_type=%s'% (self.search._data_source_id, self.search._id, self._id, series, data_split), 'GET')
            metrics = ErrorMetrics()
            metrics._from_json(result)
            return metrics
        else:
            result = self.search._eureqa._session.execute('/fxp/datasources/%s/searches/%s/solutions/%s/series_metrics?data_type=%s&series_id_value=%s'% (self.search._data_source_id, self.search._id, self._id, data_split, series), 'GET')
            assert len(result) == 1
            metrics = ErrorMetrics()
            metrics._from_json(result[0])
            return metrics

    @property
    def search(self):
        if not self._search_object:
            self._search_object = self._eureqa._get_search_by_search_id(self._datasource_id, self._search_id)
        return self._search_object
