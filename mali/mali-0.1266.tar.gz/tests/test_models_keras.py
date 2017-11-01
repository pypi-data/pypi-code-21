# coding=utf-8
from click.testing import CliRunner

from tests.base import BaseCliTest
from mali import cli
from mali_commands.models import get_keras_weights_hash, get_tensorflow_weights_hash


class TestModelsWithKeras(BaseCliTest):
    def testGetWeightsHash(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['models', 'getWeightsHash',
                                     '--framework', 'keras',
                                     '--model', 'tests/assets/keras_full_model.hdf5'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)

    def testGetKerasWeightsHash(self):
        model_filepath = 'tests/assets/keras_full_model.hdf5'
        weights_hash = get_keras_weights_hash(model_filepath)
        self.assertEqual(weights_hash, 'v1_695a3231a3c842902f3f47c1e125c2b259b4bc89')
