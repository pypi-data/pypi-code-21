import tensorflow as tf


class TensorCreator:
    @classmethod
    def create(cls, name, shape, dtype, device=None):
        pass


class GPUTensorCreator:
    """
    A Helper class to create 
    """
    NB_UNNAMED = 0

    @classmethod
    def _get_name(cls, tensor, name=None):
        if name is not None:
            return name
        if tensor is None:
            result = "tensor_{0}".format(cls.NB_UNNAMED)
            cls.NB_UNNAMED += 1
            return result
        return tensor.name

    @classmethod
    def _get_shape(cls, tensor, shape=None):
        if shape is not None:
            return shape
        return tensor.shape.as_list()

    @classmethod
    def _get_dtype(cls, tensor, dtype=None):
        if dtype is not None:
            return dtype
        if tensor is not None:
            return tensor.dtype
        return tf.float32

    @classmethod
    def _get_shape_split(cls, shape, nb_gpus):
        if isinstance(shape, tf.TensorShape):
            shape_gpu = shape.as_list()
        else:
            shape_gpu = list(shape)
        shape_gpu[0] = shape[0] // nb_gpus
        return shape_gpu

    @classmethod
    def _check_campatblity(cls, tensor, shape=None):
        if tensor is None:
            return None
        tensor_shape = tensor.shape
        if len(tensor_shape) > 0:
            if tensor_shape is not None:
                tensor_shape = tensor_shape.as_list()
            if tensor_shape[0] is None:
                tensor_shape[0] = -1
            shape = list(shape)
            if shape[0] is None:
                shape[0] = -1
        if not tensor_shape == shape:
            if not (len(tensor_shape) == 0 and shape == [1]):
                raise ValueError(
                    "shape {0} differnt to tensor {1}.".format(shape, tensor))

    @classmethod
    def _create_main_tensor(cls, shape, dtype, device):
        if device is None:
            return tf.placeholder(dtype=dtype, shape=shape, name='main')
        else:
            with tf.device('/cpu:0'):
                return tf.placeholder(dtype=dtype, shape=shape, name='main')

    @classmethod
    def _slice_tensor_for_gpu(cls, tensor_input, nb_gpus):
        result = []
        shape_input = tensor_input.shape.as_list()
        shape_gpu = cls._get_shape_split(shape_input, nb_gpus)
        batch_size_gpu = shape_gpu[0]
        for id_slice in range(nb_gpus):
            with tf.device('/gpu:{}'.format(id_slice)):
                slice_start = [id_slice * batch_size_gpu] + \
                    [0] * (len(shape_gpu) - 1)
                result.append(tf.slice(tensor_input, slice_start,
                                       shape_gpu, name='part_{}'.format(id_slice)))
        if len(result) == 0:
            result = [tensor_input]
        return result

    @classmethod
    def _get_nb_gpu_and_device_main(cls, nb_gpu):
        if nb_gpu is None:
            nb_gpu = 0
            device_main = '/cpu:0'
        else:
            device_main = None
        return nb_gpu, device_main

    @classmethod
    def _get_tensor_main(cls, tensor, shape, dtype, device_main):
        if tensor is not None:
            return tensor
        else:
            return cls._create_main_tensor(shape, dtype, device_main)

    @classmethod
    def create(cls, tensor, name=None, shape=None, dtype=None, nb_gpu=None):
        name = cls._get_name(tensor, name)
        shape = cls._get_shape(tensor, shape)
        dtype = cls._get_dtype(tensor, dtype)
        cls._check_campatblity(tensor, shape)
        with tf.name_scope(name):
            nb_gpu, device_main = cls._get_nb_gpu_and_device_main(nb_gpu)
            tensor_main = cls._get_tensor_main(
                tensor, shape, dtype, device_main)
            tensors_gpu = cls._slice_tensor_for_gpu(tensor_main, nb_gpu)
        return tensor_main, tensors_gpu
