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

from benchsuite.core.controller import BenchmarkingController
from flask_restplus import Namespace, Resource, fields
from datetime import datetime
from benchsuite.rest.apiv1.executions import new_execution_model, execution_model
from benchsuite.rest.apiv1.model import APIException

api = Namespace('sessions', description='Benchmarking Sessions operations')

api.models[execution_model.name] = execution_model
api.models[new_execution_model.name] = new_execution_model

provider_model = api.model('Provider', {
    'id': fields.String,
    'type': fields.String
})

session_model = api.model('Session', {
    'id': fields.String,
    'provider': fields.Nested(provider_model),
    'created': fields.String(attribute=lambda x: datetime.fromtimestamp(x.created).strftime('%Y-%m-%d %H:%M:%S')),
    'executions': fields.Nested(execution_model, as_list=True, attribute=lambda x: list(x.executions.values()))
})

new_session_model = api.model('NewSession', {
    'provider': fields.String(required=False),
    'service': fields.String(required=False),
    'config': fields.String(required=False, description="Specify the provider configuration as a string without "
                                                        "loading it from the Benchmarking Suite configuration folder")
})

@api.route('/')
class SessionList(Resource):

    @api.marshal_with(session_model, as_list=True, code=200, description='Returns the list of the existing sessions')
    def get(self):
        with BenchmarkingController() as bc:
            return list(bc.list_sessions())

    @api.expect(new_session_model)
    @api.marshal_with(session_model, code=204,
                      description='Creates a new benchmarking session. Returns the newly created session')
    def post(self):
        with BenchmarkingController() as bc:

            if 'provider' in self.api.payload and 'service' in self.api.payload:
                return bc.new_session(self.api.payload['provider'], self.api.payload['service'])

            if 'config' in self.api.payload:
                return bc.new_session_by_config(self.api.payload['config'])

            raise APIException('Either config or provider must be specified')


@api.route('/<string:session_id>')
@api.param('session_id', 'The id of the session')
class Session(Resource):

    @api.marshal_with(session_model, as_list=False, code=200, description='The session with the requested session id')
    def get(self, session_id):
        with BenchmarkingController() as bc:
            return bc.get_session(session_id)

    @api.response(204, description='Deletes a benchmarking session')
    def delete(self, session_id):
        with BenchmarkingController() as bc:
            bc.destroy_session(session_id)
        return '', 204


@api.route('/<string:session_id>/executions/')
class SessionExecution(Resource):

    @api.marshal_with(execution_model, code=200,
                      description='Returns the executions associated with this session')
    def get(self, session_id):
        with BenchmarkingController() as bc:
            return list(bc.get_session(session_id).list_executions())


    @api.expect(new_execution_model)
    @api.marshal_with(execution_model, code=200,
                      description='Creates a new execution in this benchmarking session. Returns the newly created execution')
    def post(self, session_id):
        with BenchmarkingController() as bc:
            return bc.new_execution(session_id, self.api.payload['tool'], self.api.payload['workload'])