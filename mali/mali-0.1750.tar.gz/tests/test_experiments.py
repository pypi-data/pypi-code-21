# coding=utf-8
import requests
import fudge
import json

from fudge.inspector import arg

from click.testing import CliRunner

from tests.base import BaseCliTest
from mali import cli
from mali_commands.experiments import chart_name_to_id


class TestExperiments(BaseCliTest):
    project_id = BaseCliTest.some_random_shit_number_int63()
    experiment_id = BaseCliTest.some_random_shit_number_int63()
    user_sent_metrics = {
        BaseCliTest.some_random_shit(): BaseCliTest.some_random_shit()
    }

    @fudge.patch('mali_commands.commons.handle_api')
    def testListExperiments(self, handle_api_mock):
        handle_api_mock.expects_call().with_matching_args(
            arg.any(),  # ctx
            requests.get,
            'projects/{project_id}/experiments'.format(project_id=self.project_id)
        ).returns({
            'experiments': [
                {
                    'experiment_id': BaseCliTest.some_random_shit_number_int63(),
                    'created_at': '2017-05-04T07:18:47.620155',
                    'display_name': BaseCliTest.some_random_shit(),
                    'description': BaseCliTest.some_random_shit()
                }
            ]
        })

        runner = CliRunner()
        result = runner.invoke(cli, ['experiments', 'list', '--projectId', self.project_id], catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)

    @fudge.patch('mali_commands.commons.handle_api')
    def testUpdateMetrics_withValidJSON_callHandleApiAndExit(self, handle_api_mock):
        handle_api_mock.expects_call().with_matching_args(
            arg.any(),  # ctx
            requests.post,
            'projects/{project_id}/experiments/{experiment_id}/metrics'.format(project_id=self.project_id,
                                                                               experiment_id=self.experiment_id),
            self.user_sent_metrics
        ).returns({})

        runner = CliRunner()
        result = runner.invoke(cli, ['experiments', 'updateMetrics', '--projectId', self.project_id,
                                     '--experimentId', self.experiment_id, '--metrics',
                                     json.dumps(self.user_sent_metrics)], catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)

    @fudge.patch('mali_commands.commons.handle_api')
    def testGraphUpdateUpdateGraph_withValidJSONAndShortHands_callHandleApiAndExit(self, handle_api_mock):
        import json

        chart_name = self.some_random_shit(size=10)
        chart_id = chart_name_to_id(chart_name)

        chart_x_name = self.some_random_shit(size=10)
        chart_y_name = self.some_random_shit(size=10)
        chart_size = 10
        chart_x = list(range(0, chart_size))
        chart_y = list(range(0, chart_size))
        chart_type = 'line'
        scope = 'test'
        data = {'name': chart_name,
                'x_int': chart_x, 'y_data': chart_y, 'chart': chart_type, 'scope': scope, 'labels': [chart_x_name, chart_y_name]}
        request = dict(data)
        request['project_id'] = self.project_id
        request['experiment_id'] = self.experiment_id
        request['chart_id'] = chart_id
        handle_api_mock.expects_call().with_matching_args(
            arg.any(),  # ctx
            requests.put,
            'projects/{project_id}/experiments/{experiment_id}/chart/{chart_id}'.format(project_id=self.project_id,
                                                                                        experiment_id=self.experiment_id,
                                                                                        chart_id=chart_id),
            data
        ).returns({})

        runner = CliRunner()
        result = runner.invoke(cli, ['experiments', 'updateChart', '-p', self.project_id,
                                     '-e', self.experiment_id, '-c', chart_name,
                                     '-cs', scope, '-ct', chart_type,
                                     '-cxn', chart_x_name, '-cyn', chart_y_name,
                                     '-cx', json.dumps(chart_x), '-cy', json.dumps(chart_y)],
                               catch_exceptions=False
                               )
        self.assertEqual(result.exit_code, 0)

    @fudge.patch('mali_commands.commons.handle_api')
    def testGraphUpdateUpdateGraph_withValidJSON_callHandleApiAndExit(self, handle_api_mock):
        import json

        chart_name = self.some_random_shit(size=10)
        chart_id = chart_name_to_id(chart_name)

        chart_x_name = self.some_random_shit(size=10)
        chart_y_name = self.some_random_shit(size=10)
        chart_size = 10
        chart_x = list(range(0, chart_size))
        chart_y = list(range(0, chart_size))
        chart_type = 'line'
        scope = 'test'
        data = {'name': chart_name,
                'x_int': chart_x, 'y_data': chart_y, 'chart': chart_type, 'scope': scope, 'labels': [chart_x_name, chart_y_name]}
        request = dict(data)
        request['project_id'] = self.project_id
        request['experiment_id'] = self.experiment_id
        request['chart_id'] = chart_id
        handle_api_mock.expects_call().with_matching_args(
            arg.any(),  # ctx
            requests.put,
            'projects/{project_id}/experiments/{experiment_id}/chart/{chart_id}'.format(project_id=self.project_id,
                                                                                        experiment_id=self.experiment_id,
                                                                                        chart_id=chart_id),
            data
        ).returns({})

        runner = CliRunner()
        result = runner.invoke(cli, ['experiments', 'updateChart', '--projectId', self.project_id,
                                     '--experimentId', self.experiment_id, '--chartName', chart_name,
                                     '--chartScope', scope, '--chartType', chart_type,
                                     '--chartXName', chart_x_name, '--chartYName', chart_y_name,
                                     '--chartX', json.dumps(chart_x), '--chartY', json.dumps(chart_y)],
                               catch_exceptions=False
                               )
        self.assertEqual(result.exit_code, 0)

    @fudge.patch('mali_commands.commons.handle_api')
    def testGraphUpdateUpdateGraph_withSizeMismach_withValidJSON_callHandleApiAndExit(self, handle_api_mock):
        import json

        chart_id = self.some_random_shit(size=10)
        chart_name = self.some_random_shit(size=10)
        chart_x_name = self.some_random_shit(size=10)
        chart_y_name = self.some_random_shit(size=10)
        chart_size = 10
        chart_x = list(range(0, chart_size + 1))
        chart_y = list(range(chart_size, 2 * chart_size))
        chart_type = 'line'
        scope = 'test'
        data = {'name': chart_name, 'x_name': chart_x_name, 'y_name': chart_y_name,
                'x': chart_x, 'y': chart_y, 'chart': chart_type,
                'scope': scope}
        request = dict(data)
        request['project_id'] = self.project_id
        request['experiment_id'] = self.experiment_id
        request['chart_id'] = chart_id

        runner = CliRunner()
        result = runner.invoke(cli, ['experiments', 'updateChart', '--projectId', self.project_id,
                                     '--experimentId', self.experiment_id, '--chartName', chart_id,
                                     '--scope', scope, '--chartType', chart_type, '--chartName', chart_name,
                                     '--chartXName', chart_x_name, '--chartYName', chart_y_name,
                                     '--chartX', json.dumps(chart_x), '--chartY', json.dumps(chart_y)],
                               catch_exceptions=True)
        self.assertEqual(result.exit_code, 2)

    @fudge.patch('mali_commands.commons.handle_api')
    def testGraphUpdateUpdateGraph_with_no_proj_withValidJSON_callHandleApiAndExit(self, handle_api_mock):
        import json

        chart_id = self.some_random_shit(size=10)
        chart_name = self.some_random_shit(size=10)
        chart_x_name = self.some_random_shit(size=10)
        chart_y_name = self.some_random_shit(size=10)
        chart_size = 10
        chart_x = list(range(0, chart_size))
        chart_y = list(range(chart_size, 2 * chart_size))
        chart_type = 'line'
        scope = 'test'
        data = {'name': chart_name, 'x_name': chart_x_name, 'y_name': chart_y_name,
                'x': chart_x, 'y': chart_y, 'chart': chart_type,
                'scope': scope}
        request = dict(data)
        request['project_id'] = self.project_id
        request['experiment_id'] = self.experiment_id
        request['chart_id'] = chart_id

        runner = CliRunner()
        result = runner.invoke(cli, ['experiments', 'updateChart',
                                     '--experimentId', self.experiment_id, '--chartName', chart_id,
                                     '--chartScope', scope, '--chartType', chart_type, '--chartName', chart_name,
                                     '--chartXName', chart_x_name, '--chartYName', chart_y_name,
                                     '--chartX', json.dumps(chart_x), '--chartY', json.dumps(chart_y)],
                               catch_exceptions=True)
        self.assertEqual(result.exit_code, 2)

    def testGraphUpdateUpdateGraph_with_bad_y_size_withValidJSON_callHandleApiAndExit(self):
        import json

        chart_id = self.some_random_shit(size=10)
        chart_name = self.some_random_shit(size=10)
        chart_x_name = self.some_random_shit(size=10)
        chart_y_name = [self.some_random_shit(size=10), self.some_random_shit(size=10)]
        chart_size = 10
        chart_x = list(range(0, chart_size))
        chart_y = list(range(2 * chart_size + 1))
        chart_type = 'line'
        scope = 'test'
        data = {'name': chart_name, 'x_name': chart_x_name, 'y_name': chart_y_name,
                'x': chart_x, 'y': chart_y, 'chart': chart_type,
                'scope': scope}
        request = dict(data)
        request['project_id'] = self.project_id
        request['experiment_id'] = self.experiment_id
        request['chart_id'] = chart_id

        runner = CliRunner()
        result = runner.invoke(cli, ['experiments', 'updateChart', '--projectId', self.project_id,
                                     '--experimentId', self.experiment_id, '--chartName', chart_id,
                                     '--chartScope', scope, '--chartType', chart_type, '--chartName', chart_name,
                                     '--chartXName', chart_x_name, '--chartYName', json.dumps(chart_y_name),
                                     '--chartX', json.dumps(chart_x), '--chartY', json.dumps(chart_y)],
                               catch_exceptions=True)
        self.assertEqual(result.exit_code, 2)
        self.assertEqual(result.output, 'Usage: cli experiments updateChart [OPTIONS]\n\nError: X and Y arrays must be of the same size\n')

    @fudge.patch('mali_commands.commons.handle_api')
    def testGraphUpdateUpdateGraph_with_no_experiment_withValidJSON_callHandleApiAndExit(self, handle_api_mock):
        import json

        chart_id = self.some_random_shit(size=10)
        chart_name = self.some_random_shit(size=10)
        chart_x_name = self.some_random_shit(size=10)
        chart_y_name = self.some_random_shit(size=10)
        chart_size = 11
        chart_x = list(range(0, chart_size))
        chart_y = list(range(chart_size, 2 * chart_size))
        chart_type = 'line'
        scope = 'test'
        data = {'name': chart_name, 'x_name': chart_x_name, 'y_name': chart_y_name,
                'x': chart_x, 'y': chart_y, 'chart': chart_type,
                'scope': scope}
        request = dict(data)
        request['project_id'] = self.project_id
        request['experiment_id'] = self.experiment_id
        request['chart_id'] = chart_id

        runner = CliRunner()
        result = runner.invoke(cli, ['experiments', 'updateChart', '--projectId', self.project_id,
                                     '--scope', scope, '--chartType', chart_type, '--chartName', chart_name,
                                     '--chartXName', chart_x_name, '--chartYName', chart_y_name,
                                     '--chartX', json.dumps(chart_x), '--chartY', json.dumps(chart_y)],
                               catch_exceptions=True)
        self.assertEqual(result.exit_code, 2)

    @fudge.patch('mali_commands.commons.handle_api')
    def testUpdateMetrics_withValidJSONAndShortHands_callHandleApiAndExit(self, handle_api_mock):
        handle_api_mock.expects_call().with_matching_args(
            arg.any(),  # ctx
            requests.post,
            'projects/{project_id}/experiments/{experiment_id}/metrics'.format(project_id=self.project_id,
                                                                               experiment_id=self.experiment_id),
            self.user_sent_metrics
        ).returns({})

        runner = CliRunner()
        result = runner.invoke(cli, ['experiments', 'updateMetrics', '-p', self.project_id,
                                     '-e', self.experiment_id, '-m', json.dumps(self.user_sent_metrics)],
                               catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)

    @fudge.patch('mali_commands.commons.handle_api')
    def testUpdateMetrics_withWeightsHash_callHandleApiAndExit(self, handle_api_mock):
        model_weights_hash = BaseCliTest.some_random_shit()
        handle_api_mock.expects_call().with_matching_args(
            arg.any(),  # ctx
            requests.post,
            'model_weights_hashes/{model_weights_hash}/metrics?experiment_only=1'.format(
                model_weights_hash=model_weights_hash),
            self.user_sent_metrics
        ).returns({})

        runner = CliRunner()
        result = runner.invoke(cli, ['experiments', 'updateMetrics', '--weightsHash', model_weights_hash,
                                     '--metrics', json.dumps(self.user_sent_metrics)],
                               catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)

    def testUpdateMetrics_projectIdSpecifiedWithoutExperimentId_raiseBadOptionUsage(self):
        runner = CliRunner()
        params = ['experiments', 'updateMetrics', '--projectId', self.project_id,
                  '--metrics', BaseCliTest.some_random_shit()]
        result = runner.invoke(cli, params, catch_exceptions=False)
        self.assertEqual(result.output, 'Usage: cli experiments updateMetrics [OPTIONS]\n\n'
                                        'Error: Please also specify --experimentId option.\n')

    def testUpdateMetrics_experimentIdSpecifiedWithoutProjectId_raiseBadOptionUsage(self):
        runner = CliRunner()
        params = ['experiments', 'updateMetrics', '--experimentId', self.experiment_id,
                  '--metrics', BaseCliTest.some_random_shit()]
        result = runner.invoke(cli, params, catch_exceptions=False)
        self.assertEqual(result.output, 'Usage: cli experiments updateMetrics [OPTIONS]\n\n'
                                        'Error: Please also specify --projectId option.\n')

    def testUpdateMetrics_noOptionSpecified_raiseBadOptionUsage(self):
        runner = CliRunner()
        params = ['experiments', 'updateMetrics', '--metrics', BaseCliTest.some_random_shit()]
        result = runner.invoke(cli, params, catch_exceptions=False)
        self.assertEqual(result.output, 'Usage: cli experiments updateMetrics [OPTIONS]\n\n'
                                        'Error: Please specify the experiment using (1) --projectId and '
                                        '--experimentId optionsor (2) --weightsHash options.\n')

    def testUpdateMetrics_withInvalidJSON_raiseValueError(self):
        runner = CliRunner()
        params = ['experiments', 'updateMetrics', '--projectId', self.project_id, '--experimentId', self.experiment_id,
                  '--metrics', BaseCliTest.some_random_shit()]
        result = runner.invoke(cli, params, catch_exceptions=False)
        self.assertEqual(result.output, 'Usage: cli experiments updateMetrics [OPTIONS]\n\n'
                                        'Error: Invalid value: The supplied sting is not a valid JSON dictionary format.\n')

    @fudge.patch('mali_commands.commons.handle_api')
    def testUpdateModelMetrics_withValidJSON_callHandleApiAndExit(self, handle_api_mock):
        model_weights_hash = BaseCliTest.some_random_shit()
        handle_api_mock.expects_call().with_matching_args(
            arg.any(),  # ctx
            requests.post,
            'model_weights_hashes/{model_weights_hash}/metrics'.format(model_weights_hash=model_weights_hash),
            self.user_sent_metrics
        ).returns({})

        runner = CliRunner()
        result = runner.invoke(cli, ['experiments', 'updateModelMetrics', '--weightsHash', model_weights_hash,
                                     '--metrics', json.dumps(self.user_sent_metrics)], catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)
