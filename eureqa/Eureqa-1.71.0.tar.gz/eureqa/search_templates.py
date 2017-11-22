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

import warnings
from utils import utils

from search_settings import SearchSettings
from variable_options_dict import VariableOptionsDict
from variable_options import VariableOptions

class SearchTemplates:
    """Provides a set of search settings for well known search scenarios.
    Created automatically when you create a :py:class:`~eureqa.eureqa.Eureqa`. Can be accessed through :py:class:`~eureqa.eureqa.Eureqa.search_templates`.

    Each function of this class represents a type of search that there is a template for.
    The function will return a :py:class:`~eureqa.search_settings.SearchSettings`
    containing the suggested settings for that type of search.

    """

    Numeric                  = "generic"
    Timeseries               = "timeseries"
    Classification           = "classification"
    ClassificationTimeseries = "timeseries_classification"

    def __init__(self, eureqa):
        """For internal use only
        PARAM_NOT_EXTERNALLY_DOCUMENTED
        """

        self._eureqa = eureqa

    def numeric(self, name, target_variable, input_variables, variable_options=None, datasource=None):
        """The numeric search settings template.

        :param str name: The search name.
        :param str target_variable: The target variable.
        :param list input_variables: The list (str) of input variables.
        :param list variable_options: An optional list of :py:class:`~eureqa.variable_options.VariableOptions`
            to include in the search
        :param ~eureqa.data_source.DataSource datasource: The datasource this template will be applied in.
        :rtype: SearchSettings
        """

        if datasource is None: warnings.warn("'eureqa.SearchTemplates.numeric' should be given a 'datasource' parameter"
                                             ,DeprecationWarning)
        assert not isinstance(input_variables, str), "Input variables must be a list."
        try: input_variables = list(input_variables) # make sure the input variables are a list
        except TypeError: raise Exception('Input variables must be a list.')

        endpoint = '/fxp/search_templates/%s/create_settings' % utils.quote(self.Numeric)
        args = {
            'search_name': name,
            'datasource_id': datasource._datasource_id if datasource is not None else '',
            'input_variables': input_variables,
            'target_variable': target_variable,
            'search_template_id': self.Numeric
        }
        self._add_variable_options_to_args(args, variable_options)
        self._eureqa._session.report_progress('Creating numeric settings for search: \'%s\'.' % name)
        body = self._eureqa._session.execute(endpoint, 'POST', { "search": args })
        settings = SearchSettings.from_json(self._eureqa, body["search"])
        return settings

    def classification(self, name, target_variable, input_variables, variable_options=None, datasource=None):
        """The classification search settings template.

        :param str name: The search name.
        :param str target_variable: The target variable.
        :param list input_variables: The list (str) of input variables.
        :param list variable_options: An optional list of :py:class:`~eureqa.variable_options.VariableOptions`
            to include in the search
        :param ~eureqa.data_source.DataSource datasource: The datasource this template will be applied in.
        :rtype: SearchSettings
        """

        if datasource is None: warnings.warn("'eureqa.SearchTemplates.classification' should be given a 'datasource' parameter"
                                             ,DeprecationWarning)
        assert not isinstance(input_variables, str), "Input variables must be a list."
        try: input_variables = list(input_variables) # make sure the input variables are a list
        except TypeError: raise Exception('Input variables must be a list.')

        endpoint = '/fxp/search_templates/%s/create_settings' % self.Classification
        args = {
            'search_name': name,
            'datasource_id': datasource._datasource_id if datasource is not None else '',
            'input_variables': input_variables,
            'target_variable': target_variable,
            'search_template_id': self.Classification
        }
        self._add_variable_options_to_args(args, variable_options)
        self._eureqa._session.report_progress('Creating classification settings for search: \'%s\'.' % name)
        body = self._eureqa._session.execute(endpoint, 'POST', { "search": args })
        settings = SearchSettings.from_json(self._eureqa, body["search"])
        return settings

    def time_series(self, name, target_variable, input_variables, min_delay=1, data_custom_history_fraction=0.1,
                    max_delays_per_variable=None, variable_options=None, datasource=None):
        """The time series search settings template.

        :param str name: The search name.
        :param str target_variable: The target variable.
        :param list input_variables: The list (str) of input variables.
        :param int min_delay: Optionally specify the minimum number of rows used in the range functions.
        :param float data_custom_history_fraction: Optionally specify the percentage of the data to be withheld
            from history blocks. Specifies the maximum possible delay for a history block.
        :param int max_delays_per_variable: Optionally overrides data_custom_history_fraction to directly set
            the maximum possible delay for a history block.
        :param list variable_options: An optional list of :py:class:`~eureqa.variable_options.VariableOptions`
            to include in the search
        :param ~eureqa.data_source.DataSource datasource: The datasource this template will be applied in.
        :rtype: SearchSettings
        """

        if datasource is None: warnings.warn("'eureqa.SearchTemplates.time_series' should be given a 'datasource' parameter"
                                             ,DeprecationWarning)
        assert not isinstance(input_variables, str), "Input variables must be a list."
        try: input_variables = list(input_variables) # make sure the input variables are a list
        except TypeError: raise Exception('Input variables must be a list.')

        endpoint = '/fxp/search_templates/%s/create_settings' % self.Timeseries
        args = {
            'search_name': name,
            'datasource_id': datasource._datasource_id if datasource is not None else '',
            'input_variables': input_variables,
            'target_variable': target_variable,
            'default_min_delay': min_delay,
            'max_delay': max_delays_per_variable,
            'search_template_id': self.Timeseries
        }
        self._add_variable_options_to_args(args, variable_options)
        self._eureqa._session.report_progress('Creating time series settings for search: \'%s\'.' % name)
        body = self._eureqa._session.execute(endpoint, 'POST', { "search": args })
        settings = SearchSettings.from_json(self._eureqa, body["search"])
        return settings

    def time_series_classification(self, name, target_variable, input_variables, min_delay=1,
                                   data_custom_history_fraction=0.1, max_delays_per_variable=None,
                                   variable_options=None, datasource=None):
        """The time series classification search settings template.

        :param str name: The search name.
        :param str target_variable: The target variable.
        :param list input_variables: The list (str) of input variables.
        :param int min_delay: Optionally specify the number of rows the model should predict into the future (i.e. the default minimum number of rows each variable will be delayed in the model).
        :param float data_custom_history_fraction: Optionally specify the percentage of the data to be withheld
            from history blocks. Specifies the maximum possible delay for a history block.
        :param int max_delays_per_variable: Optionally overrides data_custom_history_fraction to directly set
            the maximum possible delay for a history block.
        :param list variable_options: An optional list of :py:class:`~eureqa.variable_options.VariableOptions`
            to include in the search
        :param ~eureqa.data_source.DataSource datasource: The datasource this template will be applied in.
        :rtype: SearchSettings
        """

        if datasource is None: warnings.warn("'eureqa.SearchTemplates.time_series_classification' should be given" +
                                             "a 'datasource' parameter"
                                             ,DeprecationWarning)
        assert not isinstance(input_variables, str), "Input variables must be a list."
        try: input_variables = list(input_variables) # make sure the input variables are a list
        except TypeError: raise Exception('Input variables must be a list.')

        endpoint = '/fxp/search_templates/%s/create_settings' % self.ClassificationTimeseries
        args = {
            'search_name': name,
            'datasource_id': datasource._datasource_id if datasource is not None else '',
            'input_variables': input_variables,
            'target_variable': target_variable,
            'default_min_delay': min_delay,
            'max_delay': max_delays_per_variable,
            'search_template_id': self.ClassificationTimeseries
        }
        self._add_variable_options_to_args(args, variable_options)
        self._eureqa._session.report_progress('Creating time series classification settings for search: \'%s\'.' % name)
        body = self._eureqa._session.execute(endpoint, 'POST', { "search": args })
        settings = SearchSettings.from_json(self._eureqa, body["search"])
        return settings


    #Private Helper Methods
    def _add_variable_options_to_args(self, args, variable_options):
        if variable_options is not None:
            if isinstance(variable_options, VariableOptionsDict):
                args['variable_options'] = variable_options._to_json()
            else:
                try:
                    args['variable_options'] = []
                    for opt in variable_options:
                        assert isinstance(opt, VariableOptions)
                        args['variable_options'].append(opt._to_json())
                except TypeError, AssertionError:
                    raise Exception('variable_options must be a VariableOptionsDict or a list of VariableOptions')
