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
    UndefinedSessionException

blueprint = Blueprint('apiv1', __name__, url_prefix='/api/v1')

description = '''
This short tutorial will show you the basic usage of this API. The full Benchmarking Suite documentation can be found at https://benchmarking-suite.readthedocs.io/

## How to use this API

1. First we create a new Benchmarking Session with a POST at http://localhost:5000/api/v1/sessions/. In the request, we specify the provider and the service type.

    ~~~
    {
       "provider": "filab-vicenza",
       "service": "centos_medium" 
     }
    ~~~
    
    Alternatively, it is possible to specify the configuration directly in the request:
    ~~~
    {
       "config": "[provider]\\nclass = benchsuite.stdlib.provider.existing_vm.ExistingVMProvider\\n[my_vm1]\\nip_address = 217.172.12.215\\nkey_path = /home/ggiammat/credentials/filab-vicenza/ggiammat-key.pem\\nuser = ubuntu\\nplatform = ubuntu"
     }
    ~~~
    
    **Attention**: in this case passwords will be visible in the request.
    
    **Attention**: the config must be specified on a single line (JSON does not allow multiline strings) with '\\n' to delimit newlines.

2. Now we create a new execution in the newly created benchmarking session with a POST at http://localhost:5000/api/v1/sessions/<SESSION_ID>/executions/. In the request we specify the tool and the workload:
    ~~~
    {
      "tool": "cfd",
      "workload": "workload1"
    }
    ~~~

3. Now we can prepare the execution with a POST to http://localhost:5000/api/v1/executions/<EXECUTION_ID>/prepare

4. Finally a POST to http://localhost:5000/api/v1/executions/<EXECUTION_ID>/run will execute the test

** You can experiment the API usage directly from this page. Continue to read ... **

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

@api.errorhandler(ControllerConfigurationException)
def handle_custom_exception(error):
    return {'message': str(error)}, 400


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

