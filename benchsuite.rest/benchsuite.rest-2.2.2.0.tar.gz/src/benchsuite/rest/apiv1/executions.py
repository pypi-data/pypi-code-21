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

from datetime import datetime

from benchsuite.core.controller import BenchmarkingController
from flask_restplus import Namespace, Resource, fields
from benchsuite.rest.apiv1.model import timestamp_to_string

api = Namespace('executions', description='Executions operations')


# register models from the other namespaces
benchmark_model = api.model('Benchmark', {
    'tool_id': fields.String,
    'workload_id': fields.String,
    'tool_name': fields.String,
    'workload_name': fields.String,
    'workload_description': fields.String,
})

vm_model = api.model('VM', {
    'id': fields.String(
        description='the id of the VM as assigned by the Cloud Management Software (e.g. OpenStack)'),

    'ip': fields.String(
        description='the public ip of the VM'),

    'platform': fields.String(
        description='the VM platform (e.g. "Ubuntu")')
})

execution_env_model = api.model('ExecutionEnvironment', {
    'vms': fields.List(fields.Nested(vm_model))
})

execution_model = api.model('Execution', {
    'id': fields.String,
    'test': fields.Nested(benchmark_model),
    'exec_env': fields.Nested(execution_env_model),
    'created': fields.String(attribute=lambda x: timestamp_to_string(x.created))
})

new_execution_model = api.model('NewExecution', {
    'tool': fields.String,
    'workload': fields.String
})

execution_command_info_model = api.model('ExecutionCommand', {
    'started': fields.String(attribute=lambda x: timestamp_to_string(x.started)),
    'duration': fields.String
})


@api.route('/')
class ExecutionList(Resource):

    @api.marshal_with(execution_model)
    def get(self):
        with BenchmarkingController() as bc:
            return list(bc.list_executions())


@api.route('/<string:exec_id>')
class Execution(Resource):

    @api.marshal_with(execution_model)
    def get(self, exec_id):
        with BenchmarkingController() as bc:
            return bc.get_execution(exec_id)


@api.route('/<string:exec_id>/prepare')
class ExecutionPrepareACtion(Resource):

    @api.marshal_with(execution_command_info_model, code=200, description='Runs the prepare commands')
    def post(self, exec_id):
        with BenchmarkingController() as bc:
            return bc.prepare_execution(exec_id)



@api.route('/<string:exec_id>/run')
class ExecutionRunACtion(Resource):

    @api.marshal_with(execution_command_info_model, code=200, description='Runs the run commands')
    def post(self, exec_id):
        with BenchmarkingController() as bc:
            return bc.run_execution(exec_id)
