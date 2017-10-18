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

from flask_restplus import Namespace, fields, Resource
from benchsuite.core.controller import BenchmarkingController


api = Namespace('benchmarks', description='Benchmarks operations')

#
# Models
#
benchmark_workload_config_model = api.model('BenchmarkWorkloadConfiguration', {
    'id': fields.String(
        description='The id of the workload (i.e. the name of the section containing the configuration)'),

    'workload_name': fields.String(
        description='the value of the "workload_name" field in the configuration'),

    'workload_description': fields.String(
        description='the value of the "workload_description" field in the configuration')
})

benchmark_config_model = api.model('BenchmarkConfiguration', {
    'id': fields.String(
        description='The id of the benchmark (i.e. the name of the file containing the configuration'),

    'tool_name': fields.String(
        description='the value of the "tool_name" field in the configuration'),

    'workloads': fields.List(fields.Nested(benchmark_workload_config_model))
})


#
# Routes
#

@api.route('/')
class BenchmarkConfigurationsList(Resource):

    @api.marshal_with(benchmark_config_model,
                      as_list=True,
                      code=200,
                      description='Returns the list of all benchmark tools configuration files found')
    def get(self):
        with BenchmarkingController() as bc:
            return bc.list_available_benchmark_cfgs()


@api.route('/<string:benchmark_id>')
class BenchmarkConfiguration(Resource):

    @api.marshal_with(benchmark_config_model,
                      code=200,
                      description="Returns one benchmark tool and all available workloads")
    def get(self, benchmark_id):
        with BenchmarkingController() as bc:
            return bc.get_benchmark_cfg(benchmark_id)