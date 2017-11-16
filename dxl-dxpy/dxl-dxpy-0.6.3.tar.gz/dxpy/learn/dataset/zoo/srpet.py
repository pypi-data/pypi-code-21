import tensorflow as tf


def pet_image_super_resolution_dataset(dataset_name: str,
                                       image_type: str,
                                       batch_size: int,
                                       nb_down_sample: int,
                                       *,
                                       name: str='dataset',
                                       path_dataset: "str|None"=None):
    """
    Args:
        -   dataset_name: one of the following names:
            1.  analytical_phantoms
            2.  monte_carlo_phantoms [TODO: Impl]
            3.  mice [TODO: Imple]
            4.  mnist

        -   image_type: 'sinogram' or 'image'
        -   batch_size
    Returns:
        a `Graph` object, which has several nodes:
    Raises:
    """
    from ..petsino import PhantomSinograms
    from ...model.normalizer.normalizer import FixWhite, ReduceSum
    from ..super_resolution import SuperResolutionDataset
    from ...model.tensor import ShapeEnsurer
    from ...config import config
    config_origin = {

    }
    config_normalizer = {
        'mean': 4.88,
        'std': 4.36
    }
    config['dataset'] = {
        'origin': config_origin,
        'fix_white': config_normalizer
    }
    with tf.name_scope('{img_type}_dataset'.format(img_type=image_type)):
        dataset_origin = PhantomSinograms(name='dataset/origin',
                                          batch_size=batch_size)
        dataset_summed = ReduceSum('dataset/reduce_sum',
                                   dataset_origin['image'],
                                   fixed_summation_value=1e6).as_tensor()
        dataset = FixWhite(name='dataset/fix_white',
                           inputs=dataset_summed).as_tensor()
        dataset = SuperResolutionDataset('dataset/super_resolution',
                                         lambda: {'image': dataset},
                                         input_key='image',
                                         nb_down_sample=3)
    return dataset
