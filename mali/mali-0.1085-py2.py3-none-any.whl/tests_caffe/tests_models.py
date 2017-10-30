# coding=utf-8
import caffe

from click.testing import CliRunner

from tests.base import BaseCliTest
from mali import cli
from mali_commands.models import get_pycaffe_weights_hash


class TestModels(BaseCliTest):
    def testGetWeightsHash_withPyCaffe(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['models', 'getWeightsHash',
                                     '--framework', 'caffe',
                                     '--model', 'tests_caffe/assets/train.prototxt',
                                     '--weights', 'tests_caffe/assets/checkpoint.caffemodel'], catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)

    def testGetPyCaffeWeightsHash(self):
        model_filepath = 'tests_caffe/assets/train.prototxt'
        weights_filepath = 'tests_caffe/assets/checkpoint.caffemodel'
        weights_hash = get_pycaffe_weights_hash(model_filepath, weights_filepath)
        self.assertEqual(weights_hash, 'v1_90e25d83a36e3ba183a039fc27fd8b3af969cf54')
