'''MaskConvNet with Conv2D testcase'''
from unittest import TestCase

import numpy as np
from keras.models import Input, Model
from keras.layers import Conv2D

from yklz import MaskConvNet
from yklz import MaskConv
from test import TestConvBase2DClass

class TestConvolution2DClass(TestConvBase2DClass, TestCase):

    def setUp(self):
        super(TestConvolution2DClass, self).setUp()

        self.model = self.create_model()

    def create_model(self):
        inputs = Input(shape=(self.x, self.y, self.channel_size))
        masked_inputs = MaskConv(self.mask_value)(inputs)
        outputs = MaskConvNet(
            Conv2D(
                self.filters,
                self.kernel,
                strides=self.strides
            )
        )(masked_inputs)
        model = Model(inputs, outputs)
        model.compile('sgd', 'mean_squared_error')
        return model

