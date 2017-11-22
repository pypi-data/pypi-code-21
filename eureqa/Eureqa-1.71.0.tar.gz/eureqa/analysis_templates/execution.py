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

from progress_update import ProgressUpdate
from parameters_values import ParametersValues
from parameter_validation_result import ParameterValidationResult
from eureqa.utils import Throttle

import json
from eureqa.utils import utils

class Execution:
    """Represents an analysis template execution on the server.

    :param dict body: Class metadata as dictionary
    :param str template_id: The id of the analysis_template the execution belongs to.
    :param Eureqa eureqa: A eureqa connection.

    :var str `~eureqa.analysis_templates.execution.Execution.template_id`: The id of the analysis_template the execution belongs to.
    :var str `~eureqa.analysis_templates.execution.Execution.analysis_id`: The id of the analysis the execution belongs to.
    :var str state: The current state of the execution.
    :var list `~eureqa.analysis_templates.execution.Execution.parameters`: The list of parameter values for the execution.
    :var list `~eureqa.analysis_templates.execution.Execution.progress_updates`: The list of updates for the execution.
    """
    def __init__(self, body, template_id, eureqa):
        """For internal use only"""

        self._id = body['id']
        self.template_id = template_id
        self.analysis_id = body['analysis_id']
        self.parameters = ParametersValues._from_json(eureqa, body, execution=self).parameters
        self._add_self_to_data_file_parameters()
        self._eureqa = eureqa
        self._body = body

    @property
    @Throttle()
    def state(self):
        return self._get_updated_self()._body['state']

    def _get_updated_self(self):
        """ Internal. Return a new Execution object representing the current state on the server """
        self._eureqa._session.report_progress('Getting details for execution: \'%s\' of analysis_template: \'%s\'.' % (self._id, self.template_id))
        updated_execution = self._eureqa._session.execute('/analysis_templates/%s/executions/%s' %
                                                          (utils.quote(self.template_id),
                                                           utils.quote(self._id)), 'GET')
        return Execution(updated_execution, self.template_id, self._eureqa)

    def _is_running(self):
        """Internal (to programatically drive an analysis template). Return
        true if the execution is currently executing or validating"""
        the_state = self.state # NB actually makes a RPC
        return the_state in { 'VALIDATING',  'RUNNING' }

    def _is_done(self):
        """Internal (to programatically drive an analysis template). Return
        true if the execution is currently executing or validating"""
        the_state = self.state # NB actually makes a RPC
        return the_state in { 'DONE', 'ERRORED', 'ABORTED' }

    def _is_waiting_on_confirmation(self):
        """Internal (to programatically drive an analysis template). Return
        true if the execution is waiting on the user to accept results of confirmation"""
        the_state = self.state # NB actually makes a RPC
        return the_state == 'WAITING_FOR_CONFIRMATION'

    @property
    def progress_updates(self):
        """Get all progress updates for an execution of an analysis template."""
        self._eureqa._session.report_progress('Getting progress_updates for execution: \'%s\' of analysis_template: \'%s\'.' % (self._id, self.template_id))
        results = self._eureqa._session.execute('/analysis_templates/%s/executions/%s/progress_updates' %
                                                (utils.quote(self.template_id),
                                                 utils.quote(self._id)), 'GET')
        return [ProgressUpdate(x) for x in results]

    @property
    @Throttle()
    def validation_results(self):
        """Get all validation results for the execution of an analysis template."""
        def make_parameter(body):
            r = ParameterValidationResult(type='UNKNOWN')
            r._from_json(body)
            return r
        return [make_parameter(x) for x in self._get_updated_self()._body['validation_results']]

    def _to_json(self):
        body = {
            'template_id': self.template_id,
            'analysis_id': self.analysis_id,
            'state': self._body['state'],
            'parameter': ParametersValues(self.parameters)._to_json(),
            'progress_updates': [x._to_json() for x in self.progress_updates]
        }
        return body

    def _is_running(self):
        """Internal (to programatically drive an analysis template). Return
        true if the execution is currently executing or validating"""
        the_state = self.state # NB actually makes a RPC
        return the_state in { 'VALIDATING', 'RUNNING' }

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)

    def get_analysis(self):
        """Retrieves the analysis that belongs to the execution."""
        return self._eureqa.get_analysis(self.analysis_id)

    def get_analysis_template(self):
        """Retrieves the analysis that belongs to the execution."""
        return self._eureqa._get_analysis_template(self.template_id)

    def update_progress(self, message):
        """Create a progress update for an execution of an analysis template.

        :param str message: The progress message
        """
        self._eureqa._session.report_progress('Updating progress of execution: \'%s\' of analysis_template: \'%s\'.' % (self._id, self.template_id))
        self._eureqa._session.execute('/analysis_templates/%s/executions/%s/progress_updates' %
                                      (utils.quote(self.template_id),
                                       utils.quote(self._id)), 'POST', { 'message': message })

    def report_validation_result(self, type, message=None, details=None, parameter_id=None):
        """
        Report an info/warning/error message about the specified parameter to be shown to the user in validation review

        :param str type: If this result is INFO, WARNING, or ERROR
        :param str message: The result message
        :param str details: (optional) Detailed message about the result
        :param str parameter_id: (optional) the analysis template parameter that this progress update refers to
        """
        self._eureqa._session.report_progress('Reporting validation result for execution: \'%s\' of analysis_template: \'%s\'.' % (self._id, self.template_id))
        validation_result = ParameterValidationResult(type, message, details, parameter_id)
        self._eureqa._session.execute('/analysis_templates/%s/executions/%s/validation_result' %
                                      (utils.quote(self.template_id),
                                       utils.quote(self._id)), 'POST', validation_result._to_json())

    def report_fatal_error(self, error):
        """Notifies the server that an error occurred during the execution
        and terminates the script execution.
       
        :param str error: The error that occurred during the execution.

        """
        self._eureqa._session.report_progress('Reporting error in execution: \'%s\' of analysis_template: \'%s\'.' % (self._id, self.template_id))
        self._eureqa._session.execute('/analysis_templates/%s/executions/%s/error' %
                                      (utils.quote(self.template_id),
                                       utils.quote(self._id)), 'POST', {'message': error})
        self._hard_exit()

    def _report_validation_completion(self):
        """Notifies the server that the validation portion has completed."""
        self._eureqa._session.report_progress('Reporting completion of validation: \'%s\' of analysis_template: \'%s\'.' % (self._id, self.template_id))
        self._eureqa._session.execute('/analysis_templates/%s/executions/%s/validation_completion' %
                                      (utils.quote(self.template_id),
                                       utils.quote(self._id)), 'POST', {})

    def _abort(self):
        """Notifies the server that something bad happened to the execution."""
        self._eureqa._session.report_progress('Aborting execution \'%s\' of analysis_template: \'%s\'.' % (self._id, self.template_id))
        self._eureqa._session.execute('/analysis_templates/%s/executions/%s/abort' %
                                      (utils.quote(self.template_id),
                                       utils.quote(self._id)), 'POST', {})

    def _report_validation_results_confirmed(self):
        """Internal (to programatically drive an analysis template). Reports
        that that the user confirmed validation results"""
        self._eureqa._session.report_progress('Reporting validation results were confirmed for execution: \'%s\' of analysis_template: \'%s\'.' % (self._id, self.template_id))
        self._eureqa._session.execute('/analysis_templates/%s/executions/%s/validation_results_confirmed' %
                                      (utils.quote(self.template_id),
                                       utils.quote(self._id)), 'POST', '{}')

    def _report_completion(self):
        """Notifies the server that the execution completed
        and terminates the script execution.
        """
        self._eureqa._session.report_progress('Reporting completion of execution: \'%s\' of analysis_template: \'%s\'.' % (self._id, self.template_id))
        self._eureqa._session.execute('/analysis_templates/%s/executions/%s/complete' %
                                      (utils.quote(self.template_id),
                                       utils.quote(self._id)), 'POST', {})

    def _wait_until_finished(self):
        while not self._is_done():
            if self._is_waiting_on_confirmation():
                self._report_validation_results_confirmed()

    def _hard_exit(self):
        import traceback
        with open('/tmp/we_are_quitting.txt', 'wb') as fd:
            fd.write(traceback.format_exc() + '\n')
        import sys
        sys.exit()

    def _add_self_to_data_file_parameters(self):
        if self.parameters is not None:
            for p_id in self.parameters:
                param = self.parameters[p_id]
                if param._type is "data_file":
                    param._execution = self
