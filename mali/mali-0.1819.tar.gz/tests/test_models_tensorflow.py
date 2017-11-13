# coding=utf-8
import tensorflow as tf

from click.testing import CliRunner

from tests.base import BaseCliTest
from mali import cli
from mali_commands.models import get_tensorflow_weights_hash


class TestModelsWithTensorFlow(BaseCliTest):
    def tearDown(self):
        super(BaseCliTest, self).tearDown()

        # HACK: reset tf.Session monkey patching
        from missinglink_kernel.callback import tensorflow_callback

        # Reset all the monkey patching with tf.Session
        if tensorflow_callback.base_init is not None:
            tf.Session.__init__ = tensorflow_callback.base_init

        tensorflow_callback.base_init = None
        tensorflow_callback.base_run = None

    def testGetWeightsHash(self):
        tf.reset_default_graph()

        runner = CliRunner()
        result = runner.invoke(cli, ['models', 'getWeightsHash',
                                     '--framework', 'tf',
                                     '--model', 'tests/assets/tensorflow_model/model.ckpt'], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)

    def testGetTensorFlowWeightsHash(self):
        tf.reset_default_graph()

        model_filepath = 'tests/assets/tensorflow_model/model.ckpt'
        weights_hash = get_tensorflow_weights_hash(model_filepath)
        self.assertEqual(weights_hash, 'v1_0eadc7f05dc2ffb1bf0b3429dab4f32f27d86c3e')
