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

import data_splitting
import complexity_weights
import math_block_set
from model_evaluation import ModelEvaluation
from solution import Solution
import time
from variable_options_dict import VariableOptionsDict
import json
from utils import Throttle
from utils import utils
import warnings
from cStringIO import StringIO
from collections import defaultdict
import csv

class Search:
    """Represents a search on the server. It should be created using the
    :py:meth:`~eureqa.data_source.DataSource.create_search` method. A search can be run
    using the :py:meth:`~eureqa.search.Search.submit` method.
    Once a search has ran, solutions can be retreived from one of several methods below that return
    a :py:class:`~eureqa.solution.Solution`, including :py:meth:`~eureqa.search.Search.get_best_solution`
    to get the best solution and :py:meth:`~eureqa.search.Search.get_solutions` to get a list of all solutions.

    Many of the variables will be set based on the :py:class:`~eureqa.search_settings.SearchSettings` used when
    :py:meth:`~eureqa.data_source.DataSource.create_search` is called. However, these variables can still be changed
    after the Search's creation.

    :var str `~eureqa.search.Search.name`: The name of the search.
    :var MathBlockSet `~eureqa.search.Search.math_blocks`:
        The MathBlockSet which represents mathematical operations allowed to be
        used in the search's solutions. See the usage section of :py:class:`~eureqa.search_settings.SearchSettings` to see
        examples of how to change it.
    :var DataSplitting data_splitting: A DataSplitting object that holds data splitting settings for the search algorithm.
    :var str error_metric: The error metric that will be used for this search. Choose from the error metrics in :mod:`~eureqa.error_metric`.
    :var int maximum_history_absolute_rows: The maximum number of rows that can be used in range based functions.
    :var list prior_solutions: The list of prior solutions.
    :var str row_weight: The row weight expression.
    :var str target_expression: The target expression.
    :var VariableOptionsDict variable_options: Override default behavior for the specified variables.
    """

    def __init__(self, body, eureqa, datasource=None):
        """For internal use only
        PARAM_NOT_EXTERNALLY_DOCUMENTED
        """

        self._id = body['search_id']
        self.name = body['search_name']
        self.math_blocks = math_block_set.MathBlockSet.from_json(body['building_blocks'])
        self._complexity_weights = complexity_weights._from_json(body['complexity_weights'])
        self.data_splitting = data_splitting._from_json(body)
        self._data_source_id = body['datasource_id']
        self.error_metric = body['error_metric']
        self._max_num_variables_per_term = body['max_num_variables_per_term']
        self.maximum_history_absolute_rows = body.get('max_delay')
        self.prior_solutions = body.get('prior_solutions', [])
        self.row_weight = body['row_weight']
        self.row_weight_type = body['row_weight_type']
        self.target_expression = body['target_expression']
        self.default_min_delay = body.get('default_min_delay')
        self.variable_options = VariableOptionsDict.from_json(body['variable_options'])
        self._eureqa = eureqa
        self._body = body
        self._datasource_object = datasource

    def _to_json(self):
        data_splitting_settings = {}
        self.data_splitting._to_json(data_splitting_settings)
        body_updates = {
            'name': self.name,
            'math_blocks': self.math_blocks._to_json(),
            'data_splitting': data_splitting_settings,
            'error_metric': self.error_metric,
            'maximum_history_absolute_rows': self.maximum_history_absolute_rows,
            'prior_solutions': self.prior_solutions,
            'row_weight': self.row_weight,
            'target_expression': self.target_expression,
            'variable_options': self.variable_options._to_json()
        }
        body = dict(self._body)
        body.update(body_updates)
        return body

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)

    @property
    def math_blocks(self):
        """ The MathBlockSet which represents mathematical operations allowed in solutions to the Search.

        """
        return self._math_blocks
    @math_blocks.setter
    def math_blocks(self,val):
        self._math_blocks = val

    def get_data_source(self):
        """ Retrieves from the server the data source information for this search.

        :rtype: DataSource
        """

        if not self._datasource_object:
            self._datasource_object = self._eureqa.get_data_source_by_id(self._data_source_id)
        return self._datasource_object


    def delete(self):
        """Deletes the search from the server.

        :raise Exception: search is already deleted.
        """

        endpoint = '/fxp/datasources/%s/searches/%s' % (utils.quote(self._data_source_id),
                                                        utils.quote(self._id))
        self._eureqa._session.report_progress('Deleting search: \'%s\' from datasource: \'%s\'.' % (self._id, self._data_source_id))
        self._eureqa._session.execute(endpoint, 'DELETE')

    def submit(self, time_seconds):
        """Submit the search to the server to run for the specified amount of time.

        This method does not guarantee to start the search immediately. The search can
        be queued for some time before it will start producing any results.

        :param int time_seconds:
            The maximum amount of time to run the search. The server will stop
            running the search once the running time will reach this limit.
        """


        endpoint = '/fxp/search_queue'
        body = {'datasource_id': self._data_source_id,
                'search_id': self._id,
                'stopping_condition':
                    {'time_seconds': time_seconds,
                     'max_r2': 1}}
        self._eureqa._session.report_progress('Submitting search: \'%s\' from datasource: \'%s\' to the search queue.' % (self._id, self._data_source_id))
        self._eureqa._session.execute(endpoint, 'POST', body)

    @property
    def is_running(self):
        """Indicates if the search currently running.

        :rtype: bool
        """
        search_status = self._get_updated()._body['search_queue_state']
        # The endpoint is returning the internal state of the search queue, which treats
        # queueing states as not running.
        return search_status not in {'', 'QS_NONE', 'QS_DONE', 'QS_ABORTED'}

    def stop(self):
        """Stops running the search."""

        endpoint = '/fxp/search_queue/stop'
        body = {'datasource_id': utils.quote(self._data_source_id),
                'search_id': utils.quote(self._id)}
        self._eureqa._session.report_progress('Stopping search: \'%s\' from datasource: \'%s\'.' % (self._id, self._data_source_id))
        self._eureqa._session.execute(endpoint, 'POST', body)
        self.wait_until_done()

    def wait_until_done(self, show_progress=False, poll_seconds=5, print_callback=None):
        """Waits until the search stops running.

        :param bool show_progress: whether to print the search progress while waiting.
        :param int poll_seconds: number of seconds to wait between checking progress.
        :param function print_callback: method to invoke to print the progress (sys.stdout.write by default).
        """

        if print_callback is None:
            import sys
            print_callback = sys.stdout.write

        prev_solution_string = ''
        while self.is_running:

            if show_progress:
                progress_string = self._get_progress_summary()
                solution_string = self._get_solutions_summary()
                print_callback(progress_string)
                if solution_string != prev_solution_string:
                    prev_solution_string = solution_string
                    print_callback('\n%s' % solution_string)

            time.sleep(poll_seconds)

    def _get_progress_summary(self):
        """Returns convenience values of the search progress."""
        search = self._get_updated()._body
        return 'Search="%s", remaining: %is, converged=%.2g%%, cores=%i, evals=%.4gM (%.2gM e/s), gens=%g (%.4g g/s)' % (
            search['search_name'],
            search['estimated_time_remaining_seconds'],
            search['search_stats']['search_percent_converged'],
            search['search_stats']['search_cpu_cores'],
            search['search_stats']['search_evaluations']/1e6, search['search_stats']['search_evaluations_per_second']/1e6,
            search['search_stats']['search_generations'],     search['search_stats']['search_generations_per_second'])

    def _get_solutions_summary(self):
        ret = ''
        for s in self.get_solutions():
            ret += '%i, %.4g, [ %s ]\n' % (s.complexity,
                s.optimized_error_metric_value, ', '.join(s.terms))
        return ret

    @Throttle()
    def get_solutions(self):
        """Retrieves from the server the list of solutions found so far.

        This method can be called while the search is running to check what searches are
        already found and make a decision whether continue the search.

        :rtype: list of :py:class:`~eureqa.solution.Solution` objects.
        """

        endpoint = '/fxp/datasources/%s/searches/%s/solutions' % (utils.quote(self._data_source_id),
                                                                  utils.quote(self._id))
        self._eureqa._session.report_progress('Getting solutions for search: \'%s\' from datasource: \'%s\'.' % (self._id, self._data_source_id))
        body = self._eureqa._session.execute(endpoint, 'GET')
        return [Solution(x, self._eureqa, self) for x in body]

    def get_best_solution(self):
        """Retrieves from the server the best solution found so far.

        :rtype: Solution
        """

        solutions = self.get_solutions()
        return next((x for x in solutions if x.is_best), None)

    def get_most_accurate_solution(self):
        """Retrieves from the server the most accurate solution found so far.

        :rtype: Solution
        """

        solutions = self.get_solutions()
        if not solutions: return None
        return next((x for x in solutions if x.is_most_accurate), None)

    def create_solution(self, solution_string, use_all_data=False):
        """Creates a custom solution for the search.
        Use this if you want to compute error metrics and other statistics of a specified expression.
        It is also useful to compare how well a known model does against one found by Eureqa

        :param string solution_string: the right hand side of the expression.
        :param bool use_all_data: whether to use all data or just validation data when calculating the metrics for the solution.

        :rtype: Solution
        """

        endpoint = '/fxp/datasources/%s/searches/%s/solutions' % (utils.quote(self._data_source_id),
                                                                  utils.quote(self._id))
        body = {'datasource_id': self._data_source_id,
                'search_id': self._id,
                'solution_string': solution_string,
                'use_all_data': use_all_data}
        result = self._eureqa._session.execute(endpoint, 'POST', body)
        return Solution(result, self._eureqa, self)

    @Throttle()
    def _get_updated(self):
        return self._eureqa._get_search_by_search_id(self._data_source_id, self._id)

    def evaluate_expression(self, expressions, _data_split='all'):
        """Deprecated. Use :py:meth:`~eureqa.eureqa.Eureqa.evaluate_expression()` instead

        :param str expressions: Deprecated.  Do not use.
        """
        warnings.warn("This function has been deprecated.  Please use `Eureqa.evaluate_expression()` instead.", DeprecationWarning)
        return self._eureqa.evaluate_expression(self._data_source_id, expressions, self, _data_split=_data_split)

    def rename(self, new_search_name):
        """Change search display name.

        :param std new_search_name: New search name.
        """

        endpoint = '/fxp/datasources/%s/searches/%s/rename' % (utils.quote(self._data_source_id),
                                                               utils.quote(self._id))
        body = {'new_search_name': new_search_name}
        self._eureqa._session.execute(endpoint, 'POST', body)
        self.name = new_search_name

    def _evaluate_solutions(self, include_data=False, calculate_error_metrics=False, calculate_confidence_intervals=False, num_future_rows=None):
        include_data_string = 'true' if include_data else 'false'
        calculate_error_metrics = 'true' if calculate_error_metrics else 'false'
        calculate_confidence_intervals = 'true' if calculate_confidence_intervals else 'false'
        if num_future_rows is None:
            num_future_rows = -1
        endpoint = '/fxp/datasources/%s/searches/%s/evaluate_models?include_data=%s&calculate_error_metrics=%s&calculate_confidence_intervals=%s&num_future_rows=%s' % (
                utils.quote(self._data_source_id), utils.quote(self._id),
                utils.quote(include_data_string), utils.quote(calculate_error_metrics),
                utils.quote(calculate_confidence_intervals),
                num_future_rows)
        response = self._eureqa._session.execute(endpoint, 'GET')
        return ModelEvaluation(response)

    def _export_expression(self, expressions=None, output_training=True, output_validation=True, output_usable=True, output_all=False):
        if not expressions:
            expressions = self.get_data_source().get_variables()

        endpoint = "/fxp/datasources/%s/export_expression" % utils.quote(self._data_source_id)

        body = {
            "datasource_id": self._data_source_id,
            "columns": [{"column_name": expr, "expression": expr} for expr in expressions],
            "search_id": self._id,
            "output_training_flag": output_training,
            "output_validation_flag": output_validation,
            "output_usable_flag": output_usable,
            "output_all_flag": output_all
        }
        result = self._eureqa._session.execute(endpoint, 'POST', body, raw_return=True)

        def try_numeric(val):
            try:
                return float(val)
            except ValueError:
                return val

        columns = defaultdict(list)
        for row in csv.DictReader(StringIO(result)):
            for column_name, value in row.iteritems():
                columns[column_name].append(try_numeric(value))

        return dict(columns)


