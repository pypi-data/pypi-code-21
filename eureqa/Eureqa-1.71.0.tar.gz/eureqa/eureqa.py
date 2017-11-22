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

from analysis import Analysis
from analysis_templates import AnalysisTemplate
from data_source import DataSource
from organization import _Organization
from search import Search
from search_templates import SearchTemplates
from session import _Session, Http404Exception
from solution import Solution
from error_metric import ErrorMetrics


import os.path
from utils import utils
from utils import Throttle
from datetime import datetime
from cStringIO import StringIO

class Eureqa:
    """Represents an interface to the Eureqa server. All interactions with the server should start from this class.

    :var ~eureqa.search_templates.SearchTemplates `~eureqa.Eureqa.search_templates`: Provides access to predefined search templates.

    :param str url: The URL of the eureqa server. It should be the same URL as used to access the web UI.
    :param str user_name:
        The user name to login into the server. It should be the same user name as used to login into the web UI.
        If the user name is not provided and the interactive mode is enabled, the user name will be requested
        during the script execution.
    :param str password:
        The password.
        If the password is not provided and the interactive mode is enabled, the password will be requested
        during the script execution.
    :param str organization:
        The name of the organization.
        All request to API will be executed in the context of this organization.
        If the organization name is not provided and the user is assigned to only one organization, then that
        organization will be used by default.
    :param bool interactive_mode:
        If set to True, enables interactive mode. In the interactive mode the script will request user name, password,
        and potentially other information if it is not provided or incorrect.
        If set to False (default), throws an exception if a login or password is incorrect, or if the two factor
        authentication is enabled. This is the default behaviour which prevents scripts from indefinitely waiting
        for the user input if they are executed automatically by a CRON job or a Windows Scheduler task.
    :param bool save_credentials:
        If set to True, saves user name and password to the '.eureqa_passwd' in the user directory. If after that any
        script on the same machine is trying to connect to the same server and does not provide credentials, it reuses
        the saved credentials.
        It does not save a temporary password when the two-factor authentication is enabled.
        When used with the two-factor authentication, the interactive_mode parameter should also be enabled.
    :param bool verify_ssl_certificate:
        If set to False will not verify SSL certificate authenticity while connecting to Eureqa.
    :param bool verify_version:
        If set to False will allow to use Python API library with incompatible version of Eureqa.
        Should only be used for the diagnostic purpose.
    :param bool verbose:
        If set to True will print to the console the detailed information for each request to the server.
        Should only be used for the diagnostic purpose.
    :param int retries:  The number of attempts to establish a session before an Exception is raised
    :param str session_key: The session identifier.
    :param int timeout_seconds:
        The HTTP connection and transmission timeout. Any request to Eureqa API will abort with an exception if it
        takes more time, than set in the timeout, to either connect to the server or to receive a next data package.
    :param str key:
        Authentication key.  Provide either this field or `password`.

    :raise Exception: If the authentication fails or cannot be completed.
    """

    # note that if session_key is present, we don't actually try to do
    # a login and instead use the existing session key directly

    from versions import API_VERSION, SERVER_VERSION

    def __init__(self, url='https://rds.nutonian.com', user_name=None, password=None,
                 organization=None,
                 interactive_mode=False, save_credentials=False,
                 verify_ssl_certificate=True, verify_version=True, verbose=False, retries=5,
                 session_key=None, timeout_seconds=None, key=None):
        self._session = _Session(url, user_name, password, key, verbose, save_credentials, organization,
                                verify_ssl_certificate, retries, timeout_seconds, session_key, interactive_mode)
        if verify_version:
            self._verify_version()

    def create_data_source(self, name, file_or_path, series_id_column_name=None, series_order_column_name=None, _hidden=False, _create_series_id_variable=False):
        """Creates a new data source on the server.

        Uploads raw data and and creates a new datasource.

        :param str name: A name for the new data source.
        :param str file_or_path:
            A path to a local CSV file with data for the data source.
            It can be either an absolute path or path relative to the current working directory.
            Alternatively, a Python file-like object.
        :param str series_id_column_name: The name of the column that splits data into series based on its values.
        :param str series_order_column_name: The name of the column that defines the order of the data. This indicates the data is timeseries data and will sort the rows based on this column. Use DataSource.EXISTING_ROW_ORDER to use the current row number as the series order

        :return: A :py:class:`~eureqa.data_source.DataSource` object that represents a newly created data source on the server.
        :rtype: DataSource

        """

        # Trying to open before creating data source. So if there is a problem
        # with opening this file, a data source will not be even created.
        # Otherwise if there is a problem later, the call will terminal with exception
        # and an empty data source will stay in the system.

        if isinstance(file_or_path, basestring):
            f = open(file_or_path, 'rb')
            f.close()

        data_source = DataSource(self, datasource_name=name, hidden=_hidden)
        data_source._series_id_column = series_id_column_name
        data_source._series_order_column = series_order_column_name
        if series_id_column_name is not None and _create_series_id_variable:
            data_source._create_series_id_variable = _create_series_id_variable
        data_source._create(file_or_path)

        return data_source

    def get_all_data_sources(self):
        """Get all data sources from the server

        :return: A list of :py:class:`~eureqa.data_source.DataSource` objects for all data sources within the organization.
        :rtype: list of :py:class:`~eureqa.data_source.DataSource`
        """
        return DataSource._get_all(self)

    def get_data_source(self, data_source_name):
        """Get a data source by its name.

        Searches on the server for a data source given its name.

        :param str data_source_name: The name of the data source.
        :return: A :py:class:`~eureqa.data_source.DataSource` object if such data source exists, otherwise None.
        :rtype: DataSource
        """

        matching_sources = [ds for ds in self.get_all_data_sources() if ds.name == data_source_name]
        if len(matching_sources) == 0:
            message = 'Unknown datasource_name: \'%s\'' % data_source_name
            raise Exception(message)
        elif len(matching_sources) == 1:
            return matching_sources[0]
        else:
            ids = ''
            for data_source in matching_sources:
                ids += data_source._data_source_id + " "
            message = 'Multiple data sources exist with the name: \'%s\' Use get_data_source_by_id instead with one of the following ids: %s' %(data_source_name, ids)
            raise Exception(message)

    def get_data_source_by_id(self, data_source_id):
        """Get a data source by its id.

        Searches on the server for a data source given its id.

        :param str data_source_id: The ID of the data source.
        :return: A :py:class:`~eureqa.data_source.DataSource` object if such data source exists, otherwise None.
        :rtype: DataSource
        """
        return DataSource._get(self, datasource_id = data_source_id)

    def create_analysis(self, name, description=None):
        """Creates an analysis.

        :param str name: The analysis name. It will be used as the Analysis title.
        :param str description: The analysis description.
        :return: An :py:class:`~eureqa.analysis.Analysis` object that represents a newly created analysis on the server.
        :rtype: Analysis
        """

        body = {'analysis_name': name, 'description': description, 'items': []}
        self._session.report_progress('Creating analysis: \'%s\'.' % name)
        result = self._session.execute('/analysis', 'POST', body)
        return Analysis(result, self)

    def get_analyses(self):
        """Return the list of all analyses from the server.

        :rtype: list of :py:class:`~eureqa.analysis.Analysis`
        """
        self._session.report_progress('Getting details for analyses.')
        results = self._session.execute('/analysis', 'GET')
        return [Analysis(x, self) for x in results]

    def get_analysis(self, analysis_id):
        """Return a specific analysis from the server, by id

        :param str analysis_id: The id of the analysis to return
        :rtype: Analysis
        """
        self._session.report_progress('Getting details for analysis: \'%s\'.' % analysis_id)
        results = self._session.execute('/analysis/%s' % utils.quote(analysis_id), 'GET')
        return Analysis(results, self)

    def create_analysis_template(self, name, description, parameters, icon=None, icon_filepath=None, _sandboxed=None):
        """ Create a new Analysis Template on the Eureqa server.

        :param str name: The analysis template's name.  Will be used to identify the template.
        :param str description: The analysis template's description.  Will be used where more space is available for an expanded description.
        :param ~eureqa.analysis_templates.Parameters parameters: Object describing the parameters that a user must fill in via the UI in order to specify the template's behavior
        :param str icon: The url of an icon to use in the UI for this analysis.
        :param str icon_filepath: The local path to an icon to upload for use in the UI for this analysis. Overrides icon argument.

        :return: An :py:class:`~eureqa.analysis_templates.AnalysisTemplate` object representing the template on the server
        :rtype: ~eureqa.analysis_templates.AnalysisTemplate """
        # :param bool _sandboxed: Should the template be run locally on the app server or remotely on a Docker execution node?
        # Deliberately undocumented; for Nutonian internal use only.
        # Docker execution nodes are not yet available in all configurations; jobs instructed to run on one will fail if one is not available.

        if not self._session._is_root():
            raise Exception("Analysis templates can only be modified by a root user. You are '%s'" %(self._session.user))

        icon_url = None
        icon_url_fill_custom = False
        if icon_filepath is not None:
            if not os.path.isfile(icon_filepath):
                raise Exception('Analysis template icon file located at "' + icon_filepath + '" does not exist')
            icon_url_fill_custom = True
        elif icon is not None:
            icon_url = icon

        body = {"name": name,
                "description": description,
                "icon_url": icon_url,
                "icon_url_fill_custom": icon_url_fill_custom}
        if _sandboxed is not None:
            body["sandboxed"] = _sandboxed
        body.update(parameters._to_json())
        self._session.report_progress('Creating analysis_template: %s' % name)
        result = self._session.execute('/analysis_templates', 'POST', body)
        template = AnalysisTemplate(result, self)

        # now that we have an ID for this analysis template, upload icon file if one was provided
        template.set_icon(icon_filepath)
        return template

    def get_all_analysis_templates(self):
        """Get a list of all Analysis Template objects currently available to this connection

        :rtype: list of :class:`~eureqa.analysis_templates.AnalysisTemplate`
        """

        self._session.report_progress('Getting details for analysis_templates.')
        results = self._session.execute('/analysis_templates', 'GET')
        return [AnalysisTemplate(x, self) for x in results]

    @property
    def search_templates(self):
        """Return all Search Templates available to the current connection

        :rtype: SearchTemplates
        """
        return SearchTemplates(self)

    def _list_search_templates(self):
        endpoint = '/fxp/search_templates'
        self._session.report_progress('Getting list of search templates')
        body = self._session.execute(endpoint, 'GET')
        templates = [x['search_template_id'] for x in body]
        return templates

    def _get_analysis_template(self, template_id):
        self._session.report_progress('Getting details for analysis_template: \'%s\'.' % template_id)
        result = self._session.execute('/analysis_templates/%s' % utils.quote(template_id), 'GET')
        return AnalysisTemplate(result, self)

    def _get_analysis_template_by_name(self, template_name):
        self._session.report_progress('Finding first analysis template with name: \'%s\'.' % template_name)
        for t in self.get_all_analysis_templates():
            if (t.name == template_name):
                return t
        raise Exception("No analysis template has name '%s'" % (template_name))

    def _get_search_by_search_id(self, data_source_id, search_id):
        self._session.report_progress('Getting details for search: \'%s\' in datasource: \'%s\'.' % (search_id, data_source_id))
        endpoint = "/fxp/datasources/%s/searches/%s" % (utils.quote(data_source_id), utils.quote(search_id))
        result = self._session.execute(endpoint, 'GET')
        return Search(result, self)

    def _get_solution_by_id(self, data_source_id, search_id, solution_id):
        self._session.report_progress('Getting details for solution: \'%s\' in search: \'%s\' in datasource: \'%s\'.' % (solution_id, search_id, data_source_id))
        endpoint = "/fxp/datasources/%s/searches/%s/solutions/%s" % (utils.quote(data_source_id),
                                                                     utils.quote(search_id),
                                                                     utils.quote(solution_id))
        result = self._session.execute(endpoint, 'GET')
        return Solution(result, self)

    def _get_solutions_by_id(self, data_source_id, search_id):
        self._session.report_progress('Getting details for solutions: \'%s\' in search: \'%s\' in datasource: \'%s\'.' % (solution_id, search_id, data_source_id))
        endpoint = "/fxp/datasources/%s/searches/%s/solutions" % (utils.quote(data_source_id),
                                                                  utils.quote(search_id))
        result = self._session.execute(endpoint, 'GET')
        return [Solution(body, self) for body in result]

    def _get_rest_endpoint_versions(self):
        try:
            self._session.report_progress('Getting settings_info.')
            settings = self._session.execute('/api/v2/fxp/settings_info', 'GET')
            return (settings['api_version'], settings['version'])
        except Http404Exception:
            # The version of eeb that don't expose this endpoint will return this.
            return 0

    def _get_session_key(self):
        return self._session._get_session_key()

    def _verify_version(self):
        server_versions = self._get_rest_endpoint_versions()
        if Eureqa.API_VERSION != server_versions[0]:
            message = 'An incorrect version of the API library is used. ' \
                      'The server version is {0}, but the library version is {1}.'.format(server_version, Eureqa.API_VERSION)
            raise Exception(message)
        if Eureqa.SERVER_VERSION != server_versions[1]:
            message = 'Warning using version {1} of the eureqa python API ' \
                      'with a server running version {0}. ' \
                      'Consider running `pip install eureqa=={0}`'.format(server_versions[1], Eureqa.SERVER_VERSION)
            print message

    def _create_organization(self, name, eqx_file_or_path=None):
        if eqx_file_or_path:
            return self._create_organization_with_eqx(name, eqx_file_or_path)
        else:
            return self._create_organization_without_eqx(name)

    def _create_organization_without_eqx(self, name):
        self._session.report_progress("Creating organization: '%s'." % name)
        self._session.execute('/api/v2/organizations', 'POST', args={'name': '%s' % name})
        return _Organization(self, name)

    def _create_organization_with_eqx(self, name, eqx_file_or_path):
        # Trying to open before creating organization. So if there is a problem
        # with opening this file, an organization will not be even created
        if isinstance(eqx_file_or_path, basestring):
            # if eqx_file_or_path is a path, check that it is there
            f = open(eqx_file_or_path, 'rb')
            if eqx_file_or_path.endswith('eqx'):
                file_path = eqx_file_or_path
            else:
                raise Exception("%s is not a valid eqx file" % eqx_file_or_path)
        elif eqx_file_or_path is not None:
            f = eqx_file_or_path
            # If the file-object has no path, assume it's a .eqx
            file_path = getattr(eqx_file_or_path, 'name', "temp.eqx")

        try:
            eqx_input = {'file': ( file_path, f), 'organization': ("temp", StringIO(name))}
            eqx_endpoint = '/api/organizations/import_eqx'
            self._session.execute(endpoint=eqx_endpoint, method='POST', files=eqx_input)
            # wait for eqx file to complete loading
            self._session.report_progress("Creating organization: '%s' from file '%s'." % (name, file_path))

            while True:
                # probably need a delay in here to not repeatedly ping the endpoint
                response = [r for r in self._eqx_import_status(eqx_endpoint) if r['organization'] == name][0]
                if response['completed']:
                    break
        finally:
            f.close()
        return _Organization(self, name)

    @Throttle()
    def _eqx_import_status(self, eqx_endpoint):
        return self._session.execute(endpoint=eqx_endpoint, method='GET')

    def _get_organization(self, id):
        self._session.report_progress('Getting organization: \'%s\'.' % id)
        self._session.execute('/api/v2/organizations/%s' % utils.quote(id), 'GET')
        return _Organization(self, id)

    def _delete_organization(self, id):
        self._session.report_progress('Deleting organization: \'%s\'.' % id)
        self._session.execute('/api/v2/organizations/%s' % utils.quote(id), 'DELETE')

    def _get_organization_ids(self):
        self._session.report_progress('Retrieving organization ids.')
        result = self._session.execute('/api/v2/organizations', 'GET')
        return [body['id'] for body in result]

    def compute_error_metrics(self, datasource, target_variable, model_expression, template_search=None,
                              variable_options=[], row_weight=None, row_weight_type=None, _data_split="all",
                              _as_fitness=False):
        """
        Compute the :py:class:`~eureqa.error_metric.ErrorMetrics` for the specified model, against the specified target_variable

        :param DataSource datasource: DataSource to compute error against
        :param str target_variable: Variable (or expression) to compare the model to
        :param str model_expression: Model whose error is to be computed
        :param Search template_search: If specified, inherit variable options from the specified search.  Values specified in :variable_options: take precedence over values in this search; use it for finer-grained control instead of or on top of this argument.
        :param VariableOptionsDict variable_options: Override any default behavior for the specified variables.  If the data contains nulls and no null-handling policy is specified, this method will return an error. A list of :py:class:`~eureqa.variable_options.VariableOptions` may also be provided.
        :param str row_weight: Expression to compute the weight of a row (how much that row contributes to the computed error)
        :param str row_weight_type: The type of expression to use to compute row weight (uniform, target_frequency, variable, or custom_expr)
        :return: The computed error metrics
        :rtype: ErrorMetrics
        """
        # '_data_split' parameter is for internal use.  Non-default valid values are 'training' and 'validation'.
        # '_as_fitness' parameter is for internal use.  Valid values are True and False. Default is False

        if isinstance(variable_options, list):
            var_options = [x._to_json() for x in variable_options]
        else:
            var_options = [x._to_json() for x in variable_options.itervalues()]

        args = {
            'row_weight': row_weight,
            'row_weight_type': row_weight_type,
            'lhs_expression': target_variable,
            'rhs_expression': model_expression,
            'data_type': _data_split,
            'variable_options': var_options,
            'as_fitness': _as_fitness
        }
        if template_search is not None:
            args["search_id"] = template_search._id
        result = self._session.execute('/fxp/datasources/%s/compute_error_metric' % utils.quote(datasource._data_source_id),
                                       'POST', args=args)
        metrics = ErrorMetrics()
        metrics._from_json(result)
        return metrics

    def evaluate_expression(self, datasource, expressions, template_search=None, variable_options=[], _data_split='all'):
        """
        Evaluates the provided expression against the specified datasource.  Returns the value of the evaluated computation.

        Example:

            values = eureqa.evaluate_expression(['x','y','x^2']) # where

            values['x']   --> [1,2,3,4]

            values['y']   --> [5,6,7,8]

            values['x^2'] --> [1,4,9,16]

            data = pandas.DataFrame(values)  # convert to pandas.DataFrame

        :param DataSource datasource: DataSource to perform the computation against
        :param str expressions: If only one expression is to be evaluated, that expression.  If multiple expressions are to be evaluated, a list of those expressions.
        :param Search template_search: If specified, inherit variable options from the specified search.  Values specified in :variable_options: take precedence over values in this search; use it for finer-grained control instead of or on top of this argument.
        :param VariableOptionsDict variable_options: Override default variable options directly for particular variables.  Set interpretation of NaN values, outliers, etc.  default behavior is to make no changes to the original data.  By default, missing values are not filled; missing values in input data may result in missing values in corresponding computed values. A list of :py:class:`~eureqa.variable_options.VariableOptions` may also be provided.
        """
        # '_data_split' parameter is for internal use only.  Non-default valid values are 'training' and 'validation'.

        if isinstance(expressions, basestring): expressions = [expressions]

        if isinstance(variable_options, list):
            var_options = [x._to_json() for x in variable_options]
        else:
            var_options = [x._to_json() for x in variable_options.itervalues()]

        # 'datasource' should be a DataSource instance.
        # Allow it to be a string too.  For internal use only.
        data_source_id = (datasource if isinstance(datasource, basestring) else datasource._data_source_id)

        endpoint = '/fxp/datasources/%s/evaluate_expression' % utils.quote(data_source_id)

        args = {
            'expression': expressions,
            'data_type': _data_split,
            'variable_options': var_options
        }
        if template_search:
            args['search_id'] = template_search._id

        self._session.report_progress('Evaluating expression on datasource: \'%s\'.' % data_source_id)
        body = self._session.execute(endpoint, 'POST', args)
        values = {expr: [] for expr in expressions}
        for series in body['series_details']:
            used_expression = set()
            for expr, column in zip(expressions, series['values']):
                if expr not in used_expression:
                    values[expr].extend(column)
                    used_expression.add(expr)
        return values

    def _expression_values(self, datasource, x_expr, y_expr):
        """
        Invokes the expression_values endpoint with specified x and y expressions. If the x_expr is a
        datetime column, converts the x values into timestamp strings that can be feed back into the
        backend and parsed as datetime again
        """
        data_source_id = (datasource if isinstance(datasource, basestring) else datasource._data_source_id)
        endpoint = '/fxp/datasources/%s/expression_values?expressions[0][x_values]=%s&expressions[0][y_values]=%s' % (utils.quote(data_source_id),
                                                                                                                      utils.quote(x_expr.strip()),
                                                                                                                      utils.quote(y_expr.strip()))
        body = self._session.execute(endpoint, 'GET')
        x_val, y_val = [], []
        for data_point in body[0]['values']:
            x_val.append(data_point['x_value'])
            y_val.append(data_point['y_value'])

        # if x_axis_is_datetime is True, the x values from backend are
        # milliseconds since Unix epoch, convert it into a string that backend
        # can parse back as datetime
        if body[0]['x_axis_is_datetime']:
            x_val = [str(datetime.utcfromtimestamp(x/1000)) for x in x_val]

        return x_val, y_val

    def _grant_user_api_access(self, username, organization, as_role="org_admin"):
        # Function is not public; API may change
        if as_role == "org_admin":
            endpoint = "/api/%(organization)s/auth/user/%(username)s/api_access"
        elif as_role == "user_admin":
            endpoint = "/api/auth/user/%(username)s/api_access/%(organization)s"

        endpoint = endpoint % { 'username': utils.quote(username),
                                'organization': utils.quote(organization) }

        self._session.execute(endpoint, 'PUT', {})

    def _revoke_user_api_access(self, username, organization, as_role="org_admin"):
        # Function is not public; API may change
        if as_role == "org_admin":
            endpoint = "/api/%(organization)s/auth/user/%(username)s/api_access"
        elif as_role == "user_admin":
            endpoint = "/api/auth/user/%(username)s/api_access/%(organization)s"

        endpoint = endpoint % { 'username': utils.quote(username),
                                'organization': utils.quote(organization) }

        self._session.execute(endpoint, 'DELETE', {})

    def _generate_api_key(self, key_name):
        # Function is not public; API may change
        endpoint = "/api/auth/keys"
        result = self._session.execute(endpoint, 'POST', {'name': key_name})
        return result

    def _revoke_api_key_by_id(self, key_id):
        # Function is not public; API may change
        endpoint = "/api/auth/keys/%s" % utils.quote(key_id)
        self._session.execute(endpoint, 'DELETE', {})

    def _revoke_api_key_by_name(self, key_name):
        # Function is not public; API may change
        # get all (both) keys and then find the key_id for the key_name
        endpoint = "/api/auth/keys"
        keys = self._session.execute(endpoint, 'GET', {})
        id = next((key['id'] for key in keys if key['name'] == key_name), -1)
        ## send the -1 default if not found so that we get the same Exception as _by_id
        endpoint = "/api/auth/keys/%s" % utils.quote(id)
        self._session.execute(endpoint, 'DELETE', {})

    def _list_api_keys(self):
        # Function is not public; API may change
        endpoint = "/api/auth/keys"
        result = self._session.execute(endpoint, 'GET', {})
        return result

    def evaluate_models(self, data, solutions, expressions=[], include_data=False,
                        calculate_error_metrics=False, calculate_confidence_intervals=False,
                        num_future_rows=None):
        """ Evaluates the provided solutions and model strings on the specified data source.

        :param str data: A path to the file, Python file-like object,
            or an existing Eureqa datasource on which the models have to be evaluated.
        :param list solutions: The list of :py:class:`~eureqa.solution.Solution` objects.
            which have to be evaluated against the datasource.
        :param list expressions: The optional list of expressions (could be variables) to include
            in the output data (optional).
        :param bool include_data: The boolean flag which will indicate whether all data columns will be included into the response.
        :param bool calculate_error_metrics: The boolean flag which will indicate whether the error metrics
            have to be calculated.
        :param bool calculate_confidence_intervals: The boolean flag which will indicate whether the
            confidence intervals have to be calculated
        :param int num_future_rows: The parameter which allows override the number of future rows on which the solution and expressions are evaluated. If no value provided for this parameter the models are evaluated into the future as far as possible.

        :rtype :py:class:`~eureqa.model_evaluation.ModelEvaluation`
        """

        cleanup_datasource = False
        if isinstance(data, DataSource):
            validation = data._apply_solutions(solutions, expressions, only_validate=True)
            if validation._modified_target_datasource:
                data = data._duplicate(data.name + " evaluate models", hidden=True)
                cleanup_datasource = True
        else:
            data = self.create_data_source("Evaluate models", data, _hidden=True)
            cleanup_datasource = True
        apply_solution_result = data._apply_solutions(solutions, expressions)
        search = apply_solution_result.get_search()
        models_evaluation = search._evaluate_solutions(include_data, calculate_error_metrics,
                                                       calculate_confidence_intervals,
                                                       num_future_rows)
        models_evaluation._apply_expression_mappings(apply_solution_result.expression_mappings)

        # Test hooks
        models_evaluation._evaluation_search = search

        # Strictly speaking this cleanup is not required because the backend will eventually remove
        # unreachable hidden datasources. But if the caller runs a big number of evaluations within
        # a short period of time it an overwhelm the server memory before it will have a chance to
        # clean up.
        if cleanup_datasource:
            data.delete()

        return models_evaluation

