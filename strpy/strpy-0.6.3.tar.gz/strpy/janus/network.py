import sys
import os
import numpy as np
import caffe
from bobo.util import quietprint


class CaffeNet(object):
    """Class to encapsulate testing an image against a Caffe CNN"""
    def __init__(self, model, weights=None, use_gpu=False, gpu_idx=0,
                 batch_size=10, channels=3, height=224, width=224, scale=1,
                 mean_pix=None, mean_image=None, rgb_to_bgr=False):

        self.model = model
        self.weights = weights
        self.channels = channels

        if use_gpu:
            caffe.set_device(gpu_idx)
            caffe.set_mode_gpu()
        else:
            caffe.set_mode_cpu()

        if weights is not None:
            self.net = caffe.Net(model, weights, caffe.TEST)
        else:
            self.net = caffe.Net(model, caffe.TEST)

        self.transformer = caffe.io.Transformer({'data': self.net.blobs['data'].data.shape})
        self.transformer.set_transpose('data', (2,0,1)) # HxWxK -> KxHxW

        if scale != 1:
            raise ValueError, 'DEBUG making sure this is disabled'
            # Raw scaling is done before mean subtraction
            # if reference model operates on images in [0,255] range instead of [0,1]
            self.transformer.set_raw_scale('data', scale)

        if mean_pix is not None:
            self.transformer.set_mean('data', mean_pix)

        # the reference model operates on images in [0,255] range instead of [0,1]
        if scale is not 1:
            self.transformer.set_raw_scale('data', scale)

        if rgb_to_bgr:
            # If the model was trained in BGR order instead of RGB
            self.transformer.set_channel_swap('data', (2,1,0))

        self.net.blobs['data'].reshape(batch_size, channels, height, width)

        self.mean_image = mean_image
        self.height = height
        self.width = width

    def getweights(self):
        weights = []
        for k, cl in enumerate(self.net.layers):
            if cl.type in ['Convolution', 'InnerProduct']:
                quietprint('getweights: found %s layer at [%d], blobs [%d], appending at [%d]' % (cl.type, k, len(cl.blobs), len(weights)), 3)
                weights.append([cl.blobs[0].data, cl.blobs[1].data])
        return weights

    def setweights(self, weights):
        widx = 0
        for k, cl in enumerate(self.net.layers):
            if cl.type in ['Convolution', 'InnerProduct']:
                quietprint('setweights: found %s layer at [%d], blobs [%d], setting at [%d]' % (cl.type, k, len(cl.blobs), widx), 3)
                w,b  = weights[widx]
                cl.blobs[0].data[...] = w
                cl.blobs[1].data[...] = b
                widx += 1
        return self

    def classify(self, media):
        # Resize to cnn input dimensions
        for m in media:
            m.resize(cols=self.width, rows=self.height)
            if self.mean_image is not None:
                # subtract average image
                m.data -= self.mean_image.load()

        # preprocess images
        data = np.vstack([m.data for m in media])
        self.net.blobs['data'].data[...] = self.transformer.preprocess('data', data) # FIXME: See test method for correct support of batch testing

        # run forward pass
        out = self.net.forward()
        argmax = out['prob'].argmax()
        probs = self.net.blobs['prob'].data[0].flatten()

        return (argmax, probs, out)

    def test(self, media, layer_end=None):
        data = np.zeros((len(media),
                           self.width, self.height,
                           self.channels),
                          dtype=np.float32)
        for k, im in enumerate(media):
            # Resize to cnn input dimensions
            im.resize(cols=self.width, rows=self.height)  # anisotropic scaling
            if self.mean_image is not None:
                # subtract average image
                im.data -= self.mean_image.load()
            data[k] = im.data

        caffe_in = np.zeros(np.array(data.shape)[[0, 3, 1, 2]],  # num, channels, height, width
                            dtype=np.float32)
        for k, d in enumerate(data):
            caffe_in[k] = self.transformer.preprocess(self.net.inputs[0], d)
        self.net.blobs['data'].reshape(len(media), self.channels, self.height, self.width)
        self.net.blobs['data'].data[...] = caffe_in
        
        # run forward pass
        if layer_end is not None:
            out = self.net.forward(end=layer_end)
        else:
            out = self.net.forward()

        return out

    def encode(self, media, layer_end=None):
        res = self.test(media, layer_end)
        return res[layer_end].copy()
