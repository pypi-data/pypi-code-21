import tensorflow as tf
from ..net import Net
from ..graph import NodeKeys

def sr_end(res, itp, ip_h, name='sr_end', is_res=True):
    """ Assuming shape(itp) == shape(ip_h)
    reps is center croped shape of itp/ip_h
    """
    with tf.name_scope(name):
        spo = res.shape.as_list()[1:3]
        spi = itp.shape.as_list()[1:3]
        cpx = (spi[0] - spo[0]) // 2
        cpy = (spi[1] - spo[1]) // 2
        crop_size = (cpx, cpy)
        itp_c = Cropping2D(crop_size)(itp)
        with tf.name_scope('output'):
            inf = add([res, itp_c])
        if is_res:
            with tf.name_scope('label_cropped'):
                ip_c = Cropping2D(crop_size)(ip_h)
            with tf.name_scope('res_out'):
                res_inf = sub(ip_c, inf)
            with tf.name_scope('res_itp'):
                res_itp = sub(ip_c, itp_c)
        else:
            res_inf = None
            res_itp = None
        return (inf, crop_size, res_inf, res_itp)


class SRMultiScale(Net):
    """
    Required inputs:
    'input/image2x', ... 'input/image8x'
    'label/image1x', ... 'label/image4x'
    """

    def __init__(self, inputs, name='network', **config):
        super().__init__(name, inputs, **config)

    @classmethod
    def _default_config(cls):
        from dxpy.collections.dicts import combine_dicts
        return combine_dicts({
            'nb_gpu': 2,
            'nb_down_sample': 3,
        }, super()._default_config())

    def _kernel(self, feeds):
        pass

    def _gpu_kernel(self, feeds):
        pass

    def _sr2x_kernel(self, input_images, label_images):
        
