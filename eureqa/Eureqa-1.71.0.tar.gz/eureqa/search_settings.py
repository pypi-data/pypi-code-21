# Copyright (c) 2017, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright
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

from data_splitting import DataSplitting
from complexity_weights import ComplexityWeights
from math_block_set import MathBlockSet
from variable_options import VariableOptions
from variable_options_dict import VariableOptionsDict
import json
import math_block_set
from utils import utils


class SearchSettings(object):
    """A set of settings that describe how a :py:class:`~eureqa.search.Search` will run. To create an instance of this class,
    call a method from :py:meth:`~eureqa.eureqa.Eureqa.search_templates`. After than, the settings can then be
    changed from their default values. Once the desired settings are attained, pass the SearchSettings instance into :py:func:`~eureqa.data_source.DataSource.create_search` to create
    a :py:class:`~eureqa.search.Search` with those settings.

    :var str `~eureqa.search_settings.SearchSettings.name`: The name of the search.
    :var str target_variable: The target variable.
    :var list input_variables: The list of input variables.
    :var MathBlockSet `~eureqa.search_settings.SearchSettings.math_blocks`: The set of mathematical operations allowed in the search's solution.
    :var DataSplitting data_splitting: The data splitting settings for the search algorithm.
    :var str error_metric: The error metric that will be used for this search. Choose from the error metrics in :mod:`~eureqa.error_metric`.
    :var int maximum_history_absolute_rows: The maximum number of rows that can be used in range based functions.
    :var list prior_solutions: The list of prior solutions.
    :var str row_weight: The row weight expression.
    :var str row_weight_type: The row weight type expression.
    :var str target_expression: The target expression.
    :var VariableOptionsDict variable_options: Override default behavior for the specified variables.
    :var int default_min_delay: the default minimum number of rows each variable will be delayed in the model, if not overridden by a specific variable option.

    Example::

      # create a new SearchSettings object with the default settings for a numeric search
      settings = e.search_templates.numeric("Sample Model", target_variable, variables - {target_variable})

      # enable the pow building block and set its complexity to 3
      settings.math_blocks.pow.enable(complexity=3)
      # disable the pow building block in searches
      settings.math_blocks.pow.disable()
      # set the complexity of log to 5 (do not change enabled or disabled)
      settings.math_blocks.log.complexity = 5

      # enable a list of blocks with default complexity
      for block in [settings.math_blocks.pow, settings.math_blocks.exp]:
          block.enable()

      # print a list of enabled blocks w/ complexity
      for block in settings.math_blocks:
          if block.enabled:
               print block.name + \": \" + str(block.complexity)

      # select a different error metric
      settings.error_metric = error_metric.mean_square_error()

      # create a new Search with these settings
      search = my_data_source.create_search(settings)


   """

    def __init__(self, eureqa=None,
                 name=None,
                 search_template_id=None,
                 target_variable=None,
                 input_variables=None,
                 data_splitting=None,
                 error_metric=None,
                 max_num_variables_per_term=None,
                 prior_solutions=None,
                 target_expression=None,
                 row_weight_type=None,
                 row_weight=None,
                 maximum_history_percentage=None,
                 maximum_history_absolute_rows=None,
                 default_min_delay=None,
                 variable_options=None,
                 datasource_id=None):
        """For internal use only.
        PARAM_NOT_EXTERNALLY_DOCUMENTED
        """

        self._body = {}
        self._eureqa = eureqa
        self.name = name
        self._search_template_id = search_template_id
        self._target_variable = target_variable
        self._input_variables = UpdatingList(self._update, input_variables or [])
        self.math_blocks = MathBlockSet()
        self._complexity_weights = ComplexityWeights()
        self.data_splitting = data_splitting or DataSplitting()
        self.error_metric = error_metric
        self._max_num_variables_per_term = max_num_variables_per_term
        self._maximum_history_percentage = maximum_history_percentage
        self.maximum_history_absolute_rows = maximum_history_absolute_rows
        self.prior_solutions = prior_solutions
        self._row_weight = row_weight or 1.0
        self._row_weight_type = row_weight_type or 'uniform'
        if target_expression is not None:
            self.target_expression = target_expression
        else:
            # No target expression defined.
            # Don't trigger the logic in the target_expression setter to use a custom expression.
            self._target_expression = None
        self._default_min_delay = default_min_delay
        if variable_options:
            self._variable_options = VariableOptionsDict([(x.name, x) for x in variable_options])
        else:
            self._variable_options = VariableOptionsDict([(x, VariableOptions(name=x, min_delay=default_min_delay, _update_parent_settings=self._update)) for x in (input_variables or [])])
        self._datasource_id = datasource_id
        if self._row_weight_type == 'custom':
            self._row_weight_type = 'custom_expr'


    @property
    def target_variable(self):
        return self._target_variable
    @target_variable.setter
    def target_variable(self, val):
        self._target_variable = val
        self._update()


    @property
    def input_variables(self):
        return self._input_variables
    @input_variables.setter
    def input_variables(self, val):
        self._input_variables = val
        self._update()

    @property
    def variable_options(self):
        return self._variable_options

    @property
    def default_min_delay(self):
        """
        The default minimum number of rows each variable will be delayed
        in the model, if not overridden by a specific variable
        option. This value is the number of rows the resulting
        model can predict into the future.
        """
        return self._default_min_delay
    @default_min_delay.setter
    def default_min_delay(self, val):
        self._default_min_delay = val
        self._update()

    @property
    def math_blocks(self):
        """
        The :class:`~eureqa.math_block_set.MathBlockSet` which represents mathematical operations allowed in solutions to the search.
        """
        return self._math_blocks
    @math_blocks.setter
    def math_blocks(self, val):
        self._math_blocks = val

    @property
    def target_expression(self):
        """ The target expression to optimize.

        Only set if a custom expression is required.
        If set, the resulting search will be treated as an "Advanced"
        search in the UI; the variable chooser will be replaced with
        an expression editor.
        """
        return self._target_expression
    @target_expression.setter
    def target_expression(self, val):
        self._target_expression = val
        self._body['target_expression_edited'] = True
    @target_expression.deleter
    def target_expression(self):
        # Deleting a custom target_expression reverts to the default
        assert hasattr(self, '_original_target_expression'), "Can't delete the target expression:  Was not created from a template; no default to fall back to."
        self._target_expression = self._original_target_expression
        if 'target_expression_edited' in self._body:
            del self._body['target_expression_edited']

    @property
    def row_weight(self):
        """The relative weight that each row is given when computing the error
        metric values for a model.

        See description of :attr:`~row_weight_type` for
        restrictions on the value of row_weight.

        """
        return self._row_weight
    @row_weight.setter
    def row_weight(self, val):
        self._row_weight = val

    @property
    def row_weight_type(self):
        """The method to use for weighting the error metric calculation.

        Options are 'uniform' (default), 'target_frequency',
        'variable', and 'custom_expr'.  If set to 'variable',
        :attr:`~row_weight` must be the name of a variable. If set to
        'custom_expr', :attr:`~row_weight` may be an arbitrary
        expression.

        """
        return self._row_weight_type
    @row_weight_type.setter
    def row_weight_type(self, val):
        self._row_weight_type = val


    @classmethod
    def from_json(cls, eureqa, body):
        name = body.get('search_name')
        datasource_id = body.get('datasource_id')
        search_template_id = body.get('search_template_id')
        target_variable = body.get('target_variable')
        input_variables = body.get('input_variables')
        target_expression = body.get('target_expression')
        error_metric = body.get('error_metric')
        max_num_variables_per_term = body.get('max_num_variables_per_term')
        row_weight = body.get('row_weight')
        row_weight_type = body.get('row_weight_type')
        data_splitting = DataSplitting.from_json(body)
        maximum_history_absolute_rows = body.get('max_delay', None)
        maximum_history_percentage = body.get('maximum_history_percent', None)
        prior_solutions = body.get('prior_solutions', [])
        default_min_delay = body.get('default_min_delay', None)
        ss = SearchSettings(eureqa=eureqa,
                            name=name,
                            search_template_id=search_template_id,
                            target_variable=target_variable,
                            input_variables=input_variables,
                            data_splitting=data_splitting,
                            error_metric=error_metric,
                            max_num_variables_per_term=max_num_variables_per_term,
                            prior_solutions=prior_solutions,
                            row_weight=row_weight,
                            row_weight_type=row_weight_type,
                            target_expression=target_expression,
                            maximum_history_percentage=maximum_history_percentage,
                            maximum_history_absolute_rows=maximum_history_absolute_rows,
                            default_min_delay=default_min_delay,
                            variable_options = [VariableOptions._from_json(var) for var in (body.get('variable_options') or [])],
                            datasource_id=datasource_id)
        ss.math_blocks = math_block_set.MathBlockSet.from_json(body.get('building_blocks') or [])
        ss._original_target_expression = target_expression
        ss._body['target_expression_edited'] = body.get('target_expression_edited')
        for var_opt in ss.variable_options.keys():
            ss.variable_options[var_opt]._update_parent_settings = ss._update
        return ss

    def _to_json(self):
        if self.name is not None:
            self._body['search_name'] = self.name

        if self._search_template_id is not None:
            self._body['search_template_id'] = self._search_template_id

        if self.target_variable is not None:
            self._body['target_variable'] = self.target_variable

        if self.input_variables is not None:
            self._body['input_variables'] = self.input_variables

        if self.target_expression is not None:
            self._body['target_expression'] = self.target_expression

        if self.error_metric is not None:
            self._body['error_metric'] = self.error_metric

        if self._max_num_variables_per_term is not None:
            self._body['max_num_variables_per_term'] = self._max_num_variables_per_term

        if self.row_weight is not None:
            self._body['row_weight'] = self.row_weight

        if self.row_weight_type is not None:
            self._body['row_weight_type'] = self.row_weight_type

        self.data_splitting._to_json(self._body)

        if self.maximum_history_absolute_rows is not None:
            self._body['max_delay'] = self.maximum_history_absolute_rows
        elif self._maximum_history_percentage is not None:
            self._body['maximum_history_percent'] = self._maximum_history_percentage

        self._body['building_blocks'] = self.math_blocks._to_json()
        self._body['complexity_weights'] = self._complexity_weights._to_json()
        self._body['variable_options'] = self.variable_options._to_json()

        if self._datasource_id is not None:
            self._body['datasource_id'] = self._datasource_id

        if self.prior_solutions is not None:
            self._body['prior_solutions'] = self.prior_solutions

        if self.default_min_delay is not None:
            self._body['default_min_delay'] = self.default_min_delay

        return self._body

    def _from_json(self, body):

        self._body = {}
        self.name = body.get('search_name')
        self._datasource_id = body.get('datasource_id')
        self._search_template_id = body.get('search_template_id')
        self._target_variable = body.get('target_variable')
        self._input_variables = UpdatingList(self._update, body.get('input_variables'))
        self.math_blocks = math_block_set.MathBlockSet.from_json(body.get('building_blocks'))
        self._complexity_weights = ComplexityWeights()
        self.data_splitting = DataSplitting.from_json(body)
        self.error_metric = body.get('error_metric')
        self._max_num_variables_per_term = body.get('max_num_variables_per_term')
        self._maximum_history_percentage = body.get('maximum_history_percent', None)
        self.maximum_history_absolute_rows = body.get('max_delay', None)
        self.prior_solutions = body.get('prior_solutions', [])
        self._row_weight = body.get('row_weight')
        self._row_weight_type = body.get('row_weight_type')
        self._target_expression = body.get('target_expression')
        self._default_min_delay = body.get('default_min_delay', None)

        if body.get('target_expression_edited'):
            self._body['target_expression_edited'] = True
            if body.get('target_expression_from_template') is not None:
                self._original_target_expression = body.get('target_expression_from_template')
        else:
            if 'target_expression_edited' in self._body:
                del self._body['target_expression_edited']
            self._original_target_expression = body.get('target_expression')

        var_opts = [VariableOptions._from_json(var_opt, self._update) for var_opt in body.get('variable_options')]
        self._variable_options = VariableOptionsDict((var.name, var) for var in var_opts)

    def __str__(self):
        return json.dumps(self._to_json())

    # used to regenerate target_expression when a property that affects the target expression is changed
    # also checks the SearchSettings object is valid
    def _update(self):
        endpoint = '/fxp/search_templates/%s/create_settings' % utils.quote(self._search_template_id)
        resp = self._eureqa._session.execute(endpoint, 'POST', { "search": self._to_json() })
        self._from_json(resp["search"])

#Helper class to allow SearchSettings to update on input_variables change
class UpdatingList(list):

    def __init__(self, update_parent_settings, *args, **kwargs):
        super(UpdatingList, self).__init__(*args, **kwargs)
        self.update_parent_settings = update_parent_settings

    def __setitem__(self, key, value):
        super(UpdatingList, self).__setitem__(key, value)
        if hasattr(self, 'update_parent_settings'):
            self.update_parent_settings()

    def __delitem__(self, key):
        super(UpdatingList, self).__delitem__(key)
        if hasattr(self, 'update_parent_settings'):
            self.update_parent_settings()

    def append(self, val):
        super(UpdatingList, self).append(val)
        if hasattr(self, 'update_parent_settings'):
            self.update_parent_settings()
