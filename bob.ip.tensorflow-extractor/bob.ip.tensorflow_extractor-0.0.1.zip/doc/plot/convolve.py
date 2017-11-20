import numpy
import bob.ip.tensorflow_extractor
import bob.db.mnist
from bob.ip.tensorflow_extractor import scratch_network
import os
import pkg_resources
import tensorflow as tf


def norm_image(image):
    return (255 * ((image - numpy.min(image)) / (numpy.max(image) - numpy.min(image)))).astype("uint8")


# Loading some samples from mnist
db = bob.db.mnist.Database()
images = db.data(groups='train', labels=[0,1,2,3,4,5,6,7,8,9])[0][0:1]
images = numpy.reshape(images, (1, 28, 28, 1)) * 0.00390625 # Normalizing the data

# preparing my inputs
inputs = tf.placeholder(tf.float32, shape=(None, 28, 28, 1))
graph = scratch_network(inputs, end_point="conv1")

# loading my model and projecting
filename = os.path.join(pkg_resources.resource_filename("bob.ip.tensorflow_extractor", 'data'), 'model.ckp.meta')
extractor = bob.ip.tensorflow_extractor.Extractor(filename, inputs, graph)

# Getting the convolved images
convs = extractor(images)

from matplotlib import pyplot

pyplot.subplot(2, 3, 1)
pyplot.imshow(norm_image(images[0, :, :, 0]), cmap='Greys_r')

pyplot.subplot(2, 3, 2)
pyplot.imshow(norm_image(convs[0, :, :, 0]), cmap='Greys_r')

pyplot.subplot(2, 3, 3)
pyplot.imshow(norm_image(convs[0, :, :, 5]), cmap='Greys_r')

pyplot.subplot(2, 3, 4)
pyplot.imshow(norm_image(convs[0, :, :, 2]), cmap='Greys_r')

pyplot.subplot(2, 3, 5)
pyplot.imshow(norm_image(convs[0, :, :, 3]), cmap='Greys_r')

pyplot.subplot(2, 3, 6)
pyplot.imshow(norm_image(convs[0, :, :, 4]), cmap='Greys_r')

