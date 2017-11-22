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

from apply_solution_result import _ApplySolutionResult
from search import Search
from variable_details import VariableDetails
from utils import utils
from utils.jsonrest import _JsonREST

import base64
import json

import warnings

class DataSource(_JsonREST):
    """Acts as an interface to a data source on the server.

    DataSources can be created by calling :py:meth:`~eureqa.eureqa.Eureqa.create_data_source`
    or an existing one can be retreived with :py:meth:`~eureqa.eureqa.Eureqa.get_data_source`

    :var str `~eureqa.data_source.DataSource.name`: The data source name.
    :var str `~eureqa.data_source.DataSource.series_id_column_name`: The name of the column that splits data into series based on its values.
    :var str `~eureqa.data_source.DataSource.series_order_column_name`: The name of the column that defines the order of the data. This indicates the data is timeseries data and will sort the rows based on this column.
    :var int `~eureqa.data_source.DataSource.number_variables`: The number of variables in the data source.
    :var int `~eureqa.data_source.DataSource.number_rows`: The number of rows in the data source.
    :var int `~eureqa.data_source.DataSource.number_series`: The number of series (chunks of rows) in the data source.
    """

    EXISTING_ROW_ORDER = "<row>"

    def __init__(self, eureqa, datasource_name=None, hidden=False, datasource_id=None):
        """For internal use only
        PARAM_NOT_EXTERNALLY_DOCUMENTED
        """

        super(DataSource, self).__init__(eureqa)

        if datasource_id is not None:
            self._datasource_id = datasource_id
        if datasource_name is not None:
            self._datasource_name = datasource_name

        self._hidden = hidden
        self._series_count = 0
        self._series_descriptions = []
        self._prepared_data_col_count = 0
        self._prepared_data_row_count = 0
        self._file_name = ''
        self._file_size = 0
        self._file_uploaded_user = ''
        self._file_uploaded_date = ''
        self._series_order_column = None
        self._series_id_column = None

    def _directory_endpoint(self):
        return "/fxp/datasources"
    def _object_endpoint(self):
        return "/fxp/datasources/%s" % utils.quote(self._datasource_id)
    def _fields(self):
        return ["datasource_id", "datasource_name", "prepared_data_row_count", "prepared_data_col_count", "series_count", "series_descriptions",  "file_name", "file_size", "file_uploaded_user", "file_uploaded_date", "hidden", "series_order_column", "series_order_variable", "series_id_column"]

    @property
    def name(self):
        return self._datasource_name
    @name.setter
    def name(self, val):
        self._datasource_name = val
        self._update()

    @property
    def number_variables(self):
        return self._prepared_data_col_count

    @property
    def number_columns(self):
        warnings.warn("DataSource.number_columns field is deprecated.  Use DataSource.number_variables instead.",
                      DeprecationWarning)
        return self.number_variables

    @property
    def number_rows(self):
        return self._prepared_data_row_count

    @property
    def number_series(self):
        return self._series_count

    @property
    def _data_source_id(self):
        return self._datasource_id

    @property
    def _data_file_name(self):
        return self._file_name

    @property
    def _data_file_size(self):
        return self._file_size

    @property
    def _data_file_uploaded_user(self):
        return self._file_uploaded_user

    @property
    def _data_file_uploaded_date(self):
        return self._file_uploaded_date

    @property
    def series_order_column_name(self):
        """ The name of the column that defines the order of the data. This indicates the data is timeseries data and will sort the rows based on this column. Use DataSource.EXISTING_ROW_ORDER to use the current row number as the series order.

        """
        return self._series_order_column

    @series_order_column_name.setter
    def series_order_column_name(self, val):
        self._update_metadata(series_id_column_name=self.series_id_column_name, series_order_column_name=val)

    @property
    def series_id_column_name(self):
        """The name of the column that splits data into series based on its values.

        """
        return self._series_id_column

    @property
    def series_order_variable_name(self):
        """The name of the variable that defines the order of the data.  Same as `series_order_column_name` except properly escaped for use as a variable name.

        """
        return self._series_order_variable

    @series_id_column_name.setter
    def series_id_column_name(self, val):
        self._update_metadata(series_id_column_name=val, series_order_column_name=self.series_order_column_name)

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)

    def delete(self):
        """Deletes the data source from the server.

        :raise Exception: If the data source is already deleted.
        """
        self._delete()

    def _create(self, file_or_path):
        assert self._datasource_name is not None, "Cannot create DataSource without a name"
        assert not hasattr(self, "_datasource_id"), "Cannot specify DataSources' ID before creation"

        if isinstance(file_or_path, basestring):
            f = open(file_or_path, 'rb')
            file_path = file_or_path
        else:
            f = file_or_path
            # If the file-object has no path, assume it's a .csv
            file_path = getattr(file_or_path, 'name', "temp.csv")

        try:
            raw_data = {}
            if getattr(self, "_series_id_column", None):
                raw_data["series_id_column"] = self._series_id_column
            if getattr(self, "_series_order_column", None):
                raw_data["series_order_column"] = self._series_order_column
            raw_data['datasource_name'] = self.name
            if self._hidden:
                raw_data['hidden'] = "true"
            else:
                raw_data['hidden'] = "false"

            if getattr(self, "_create_series_id_variable", None):
                raw_data["column_variable_settings"] = json.dumps([{ "column_name": self._series_id_column, "derive_indicator_vars": True}])
            resp = self._eureqa._session.execute('/fxp/datasources/create_and_upload', 'POST', files={'file': (file_path,f)}, raw_data=raw_data)
            self._from_json(resp.get('datasource'))
        finally:
            if isinstance(file_or_path, basestring):
                f.close()
        self._get_self()

    def _update_metadata(self, series_id_column_name, series_order_column_name):
        self._series_id_column = series_id_column_name
        self._series_order_column = series_order_column_name
        self._update()

    def download_data_file(self, file_path):
        """Downloads the originally uploaded data from the server.

        :param str file_path: the filepath at which to save the data

        """
        result = self._eureqa._session.execute('/fxp/datasources/%s/download' % utils.quote(self._data_source_id), 'GET', raw_returnfile=file_path)

    def get_variables(self, derivation_type = 'all'):
        """Retrieves from the server a list of variables in a datasource.

        :param str derivation_type: If specified, returns only variables with the specified derivation type. Valid options are 'all' (default), 'custom', 'original' or 'seasonal'. See :class:`~eureqa.variable_details.VariableDetails` for more information.
        :return: A list of the same variables as visible in Eureqa UI, including all derived variables.
        :rtype: list of str
        """
        allowed_derivation_type = ['all', 'original', 'custom', 'seasonal']
        if derivation_type not in allowed_derivation_type:
            raise ValueError("The argument 'derivation_type' must be one of " + str(allowed_derivation_type))
        endpoint = '/fxp/datasources/%s/variables?sort=[{"key":"index"}]' % utils.quote(self._datasource_id)
        self._eureqa._session.report_progress('Getting variable details for datasource: \'%s\'.' % self.name)
        body = self._eureqa._session.execute(endpoint, 'GET')
        if derivation_type == 'all':
            return [x['variable_name'] for x in body]
        else:
            return [x['variable_name'] for x in body if x['type'] == derivation_type]

    def get_searches(self):
        """Retrieves from the server a list of searches associated with the data source.

        :return: The list of all searches associated with the data source.
        :rtype: list of :class:`~eureqa.search.Search`
        """

        endpoint = '/fxp/datasources/%s/searches' % utils.quote(self._datasource_id)
        self._eureqa._session.report_progress('Getting searches for datasource: \'%s\'.' % self.name)
        body = self._eureqa._session.execute(endpoint, 'GET')
        return [Search(x, self._eureqa, self) for x in body]

    def create_search(self, search_settings, _hidden = False):
        """Creates a new search with settings from a :any:`SearchSettings` object.

        :param SearchSettings search_settings: the settings for creating a new search.
        :return: A :class:`~eureqa.search.Search` object which represents a newly create search on the server.
        :rtype: ~eureqa.search.Search
        """

        endpoint = "/fxp/datasources/%s/searches" % utils.quote(self._datasource_id)
        body = search_settings._to_json()
        body['hidden'] = _hidden
        self._eureqa._session.report_progress('Creating search for datasource: \'%s\'.' % self.name)
        result = self._eureqa._session.execute(endpoint, 'POST', body)
        search_id = result['search_id']
        return self._eureqa._get_search_by_search_id(self._datasource_id, search_id)

    def evaluate_expression(self, expressions, _data_split='all'):
        warnings.warn("This function has been deprecated.  Please use `Eureqa.evaluate_expression()` instead.", DeprecationWarning)
        return self._eureqa.evaluate_expression(self, expressions, _data_split=_data_split)

    def get_series_id_values(self):
        """Get all available series id values for this dataset. Note the series id for a single series dataset is reported to be ''

        :return: a list of all available series_id values
        :rtype: list
        """
        return [entry["series_id_val"] for entry in self._series_descriptions]

    def _compute_series_indicator(self):
        """For internal use only.

        Compute an indicator column which indicates the series which each row belongs to, as an integer from 0 to (num_series-1).

        This code was written with the assumption that it would be applied to the entire datasource, as opposed to the training or validation split.
        """
        indicator = []
        for i,series_desc in enumerate(self._series_descriptions):
            indicator += [i]*series_desc['series_size']
        return indicator

    def create_variable(self, expression, variable_name):
        """Adds a new variable to the :py:class:`~data_source.DataSource` with values from evaluating the given expression.

        :param str expression: the expression to evaluate to fill in the values
        :param str variable_name: what to name the new variable
        """
        endpoint = '/fxp/datasources/%s/variables' % utils.quote(self._datasource_id)
        body = {'datasource_id': self._datasource_id,
                'expression': expression,
                'variable_name': variable_name}
        result = self._eureqa._session.execute(endpoint, 'POST', body)
        self.__dict__ = self._eureqa.get_data_source_by_id(self._datasource_id).__dict__

    def get_variable_details(self, variable_name):
        """Retrieves the details for the requested variable from the :py:class:`~data_source.DataSource`.

        :param str variable_name: the name of the variable to get the details for
        :return:
            The object representing the variable details
        :rtype: VariableDetails
        """
        # Note:  'base64.b64encode()' does not fully support Unicode strings.
        # So, pre-encode its argument.
        endpoint = '/fxp/datasources/%s/variables/%s' % (utils.quote(self._datasource_id),
                                                         utils.quote_everything(
                                                             base64.b64encode('%s-_-%s' %
                                                                              (self._datasource_id.encode('utf-8'),
                                                                               variable_name.encode('utf-8')))))
        self._eureqa._session.report_progress('Getting variable details for datasource: \'%s\'.' % self.name)
        body = self._eureqa._session.execute(endpoint, 'GET')
        return VariableDetails(body, self)

    def get_variable(self, variable_name):
        warnings.warn("'get_variable()' function deprecated; please call as 'get_variable_details()' instead", DeprecationWarning)
        return self.get_variable_details(variable_name)

    def create_seasonality_variable(self, seasonal_target_variable, seasonal_period):
        """Adds a seasonality variable to the data_source with specified target variable and seasonal period

        :param str seasonal_target_variable: the variable name to calculate the seasonal trend for for
        :param str seasonal_period: period of the seasonal effect, supported options are 'yearly', 'weekly' or 'daily'
        :return: name of the newly created variable
        :rtype: str
        """
        endpoint = '/fxp/datasources/%s/variables' % utils.quote(self._datasource_id)
        body = {'datasource_id': self._datasource_id,
                'type': 'seasonal',
                'seasonal_target_variable': seasonal_target_variable,
                'seasonal_period': seasonal_period}
        result = self._eureqa._session.execute(endpoint, 'POST', body)
        self.__dict__ = self._eureqa.get_data_source_by_id(self._datasource_id).__dict__
        return result['variable_name']

    def create_variable_from_template(self, template):
        """Create a new derived variable on this data source with the same properties as the template variable.

        :param VariableDetails template: the template to use for creating the new variable
        """
        endpoint = '/fxp/datasources/%s/copy_variable' % utils.quote(self._datasource_id)
        body = {
            "other_variable_id": template._id
        }
        self._eureqa._session.execute(endpoint, 'POST', body)

    def _apply_solutions(self, solutions, expressions=[], only_validate=False):
        solution_requests = []
        for solution in solutions:
            solution_request = {
                    "datasource_id": solution._datasource_id,
                    "search_id": solution._search_id,
                    "solution_id": solution._id}
            solution_requests.append(solution_request);
        body = {
            "solutions": solution_requests,
            "expressions": expressions,
            "only_validate": only_validate}
        endpoint = '/fxp/datasources/%s/apply_solutions' % utils.quote(self._datasource_id)
        result = self._eureqa._session.execute(endpoint, 'POST', body)
        return _ApplySolutionResult(self._eureqa, result)

    def _duplicate(self, new_name, hidden=False):
        endpoint = '/fxp/datasources/%s/duplicate' % utils.quote(self._datasource_id)
        body = {'datasource_name': new_name,
                'hidden': hidden}
        result = self._eureqa._session.execute(endpoint, 'POST', body)
        duplicate = DataSource(self._eureqa)
        duplicate._from_json(result)
        return duplicate
