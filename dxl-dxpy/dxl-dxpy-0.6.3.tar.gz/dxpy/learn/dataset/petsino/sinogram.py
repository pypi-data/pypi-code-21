from ..base import DatasetTFRecords, NodeKeys
import tensorflow as tf
from ..config import config


class PhantomSinograms(DatasetTFRecords):
    SHAPE_SINOGRAM = [320, 640, 1]
    SHAPE_PHANTOM = [256, 256, 1]

    def __init__(self, name='dataset', **config):
        from dxpy.learn.utils.tensor import ensure_shape
        super().__init__(name, **config)
        self.nodes['image'] = ensure_shape(
            self.nodes['image'], batch_size=self.param('batch_size'))

    @classmethod
    def _parse_example(cls, example):
        return tf.parse_single_example(example, features={
            'shape_phantom': tf.FixedLenFeature([3], tf.int64),
            'shape_sinogram': tf.FixedLenFeature([3], tf.int64),
            'phantom_type': tf.FixedLenFeature([], tf.int64),
            'phantom': tf.FixedLenFeature([], tf.string),
            'sinogram': tf.FixedLenFeature([], tf.string),
        })

    @classmethod
    def _default_config(cls):
        from dxpy.collections.dicts import combine_dicts
        fmt = '/home/hongxwing/Datas/phantom/phantom.{}.tfrecord'
        files = [fmt.format(i) for i in range(1)]
        return combine_dicts({
            'files': files,
            'fields': 'sinogram',
            'batch_size': 32
        }, super()._default_config())

    def _decode_image(self, data):
        if self.param('fields') == 'sinogram':
            return {
                'image': tf.decode_raw(data['sinogram'], tf.uint16),
                'shape': data['shape_sinogram']
            }
        elif self.param('fields') == 'phantom':
            return {
                'image': tf.decode_raw(data['phantom'], tf.uint16),
                'shape': data['shape_phantom']
            }
        else:
            raise ValueError(
                "Unsupported fields: {}.".format(self.param('fields')))

    def _reshape_tensors(self, data):
        if self.param('fields') == 'sinogram':
            shape = self.SHAPE_SINOGRAM
        else:
            shape = self.SHAPE_PHANTOM
        return {'image': tf.reshape(tf.cast(data['image'], tf.float32), shape),
                'shape': data['shape']}

    def _processing(self):
        return (super()._processing()
                .map(self._parse_example)
                .map(self._decode_image)
                .map(self._reshape_tensors)
                .batch(self.c['batch_size'])
                .cache()
                .repeat())
