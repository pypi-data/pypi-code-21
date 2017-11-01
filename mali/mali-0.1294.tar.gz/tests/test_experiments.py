# coding=utf-8
import requests
import fudge
import json

from fudge.inspector import arg

from click.testing import CliRunner

from tests.base import BaseCliTest
from mali import cli


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
            'model_weights_hashes/{model_weights_hash}/metrics?experiment_only=1'.format(model_weights_hash=model_weights_hash),
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
                                        'Error: Invalid value: The metrics supplied is not a valid JSON dictionary format.\n')

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
