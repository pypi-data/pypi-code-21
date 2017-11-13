from ..base import DatasetTFRecords
import tensorflow as tf


class PhantomSinograms(DatasetTFRecords):
    def __init__(self, name='dataset', **config):
        super().__init__(name, **config)

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
        files = [fmt.format(i) for i in range(500)]
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

    @classmethod
    def _reshape_tensors(cls, data):
        return {'image': tf.reshape(tf.cast(data['image'], tf.float32), data['shape']),
                'shape': data['shape']}

    # def _pre_processing(self):
        # self._add_normalizer()

    # def _normalize(self, data):
    #     if self._normalizer is None:
    #         sinogram = data['sinogram']
    #     else:
    #         sinogram = self._normalizer(data['sinogram'])['data']
    #     return {'phantom': data['phantom'], 'sinogram': sinogram}

    # def _add_normalizer(self):
    #     from ...model import normalizer
    #     self._normalizer = None
    #     if self.param('normalization')['method'].lower() != 'pass':
    #         self._normalizer = normalizer.get_normalizer(
    #             self.param('normalization')['method'].lower())

    def _processing(self):
        return (super()._processing()
                .map(self._parse_example)
                .map(self._decode_image)
                .map(self._reshape_tensors)
                # .map(self._normalize)
                .batch(self.c['batch_size'])
                .cache()
                .repeat())
