# Benchmarking Suite
# Copyright 2014-2017 Engineering Ingegneria Informatica S.p.A.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Developed in the ARTIST EU project (www.artist-project.eu) and in the
# CloudPerfect EU project (https://cloudperfect.eu/)


from flask import Blueprint
from flask_restplus import Api, fields, Resource

from benchsuite.core.model.exception import ControllerConfigurationException, BashCommandExecutionFailedException, \
    UndefinedSessionException, ProviderConfigurationException, BaseBenchmarkingSuiteException

blueprint = Blueprint('apiv1', __name__, url_prefix='/api/v1')

description = '''

A quick tutorial on how to use the API is available in the Benchmarking Suite online documentation at:


http://benchmarking-suite.readthedocs.io/en/latest/rest.html#quick-start

'''

api = Api(
    blueprint,
    title='Benchmarking Suite REST API',
    version='1.0',
    description=description,
    # All API metadatas
)

bash_command_failed_model = api.model('BashCommandExecutionFailed', {
    'message': fields.String,
    'stdout': fields.String(example='This will be the command stdout'),
    'stderr': fields.String(example='This will be the command stderr')
})



# default error handler
@api.errorhandler
def handle_custom_exception(error):
    return {'message': str(error)}, 500

@api.errorhandler(BashCommandExecutionFailedException)
def handle_command_failed_exception(error):
    return {'message': str(error), 'stdout': str(error.stdout), 'stderr': str(error.stderr)}, 400

@api.errorhandler(UndefinedSessionException)
def handle_undefined_session(error):
    return {'message': str(error)}, 400

from .executions import api as executions_ns
from .sessions import api as sessions_ns
from .providers import api as providers_ns
from .benchmarks import api as benchmarks_ns

api.add_namespace(sessions_ns)
api.add_namespace(executions_ns)
api.add_namespace(providers_ns)
api.add_namespace(benchmarks_ns)

