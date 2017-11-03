import tensorflow as tf
from tcs_sdk.tf_task import TcsTFTask
from tensorflow.examples.tutorials.mnist import input_data


class MainTask(TcsTFTask):
    def train(self):
        mnist = input_data.read_data_sets(self.data_storage.path, one_hot=True)
        # Create the model
        x = tf.placeholder(tf.float32, [None, 784])
        W = tf.Variable(tf.zeros([784, 10]))
        b = tf.Variable(tf.zeros([10]))
        y = tf.matmul(x, W) + b

        # Define loss and optimizer
        y_ = tf.placeholder(tf.float32, [None, 10])

        # The raw formulation of cross-entropy,
        #
        #   tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(tf.nn.softmax(y)),
        #                                 reduction_indices=[1]))
        #
        # can be numerically unstable.
        #
        # So here we use tf.nn.softmax_cross_entropy_with_logits on the raw
        # outputs of 'y', and then average across the batch.

        cross_entropy = tf.reduce_mean(
            tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y))
        train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)

        sess = tf.InteractiveSession()
        tf.global_variables_initializer().run()
        # Train
        for _ in range(1000):
            if _ % 100 == 0:
                print("Gradient Training Step %s" % _)
            batch_xs, batch_ys = mnist.train.next_batch(100)
            sess.run(train_step, feed_dict={x: batch_xs, y_: batch_ys})

        return sess
