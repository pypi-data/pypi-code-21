
import tensorflow as tf
import tensorgraph as tg
from tensorgraph.layers import Conv2D, RELU, MaxPooling, LRN, Tanh, Dropout, \
                               Softmax, Flatten, Linear, TFBatchNormalization, AvgPooling, \
                               Lambda
from tensorgraph.utils import same, valid


class Model(object):
    def __call__(self, X, y):
        self.X = X
        self.y = y
        b, h, w, c = self.X.get_shape()
        h, w, c = int(h), int(w), int(c)
        # import pdb; pdb.set_trace()
        nclass = 10
        self.seq = tg.Sequential()
        self.seq.add(Conv2D(input_channels=c, num_filters=64, kernel_size=(5, 5), stride=(1, 1), padding='SAME'))
        self.seq.add(RELU())
        # self.seq.add(TFBatchNormalization(name='b1'))
        h, w = same(in_height=h, in_width=w, stride=(1,1), kernel_size=(3,3))
        self.seq.add(MaxPooling(poolsize=(3, 3), stride=(2,2), padding='SAME'))
        h, w = same(in_height=h, in_width=w, stride=(2,2), kernel_size=(3,3))
        self.seq.add(LRN(depth_radius=4, bias=1.0, alpha=0.001/9.0, beta=0.75))

        self.seq.add(Conv2D(input_channels=64, num_filters=64, kernel_size=(5, 5), stride=(1, 1), padding='SAME'))
        h, w = same(in_height=h, in_width=w, stride=(1,1), kernel_size=(5,5))
        self.seq.add(LRN(depth_radius=4, bias=1.0, alpha=0.001/9.0, beta=0.75))
        self.seq.add(MaxPooling(poolsize=(3, 3), stride=(2,2), padding='SAME'))
        h, w = same(in_height=h, in_width=w, stride=(2,2), kernel_size=(3,3))
        # self.seq.add(RELU())
        # h, w = same(in_height=h, in_width=w, stride=(1,1), kernel_size=(3,3))
        # self.seq.add(Dropout(0.5))
        #
        # self.seq.add(Conv2D(input_channels=96, num_filters=96, kernel_size=(3, 3), stride=(2, 2), padding='SAME'))
        # self.seq.add(RELU())
        # # self.seq.add(TFBatchNormalization(name='b3'))
        # h, w = same(in_height=h, in_width=w, stride=(2,2), kernel_size=(3,3))
        #
        # self.seq.add(Conv2D(input_channels=96, num_filters=192, kernel_size=(3, 3), stride=(1, 1), padding='SAME'))
        # self.seq.add(RELU())
        # h, w = same(in_height=h, in_width=w, stride=(1,1), kernel_size=(3,3))
        # self.seq.add(Dropout(0.5))

        # self.seq.add(Conv2D(input_channels=96, num_filters=192, kernel_size=(3, 3), stride=(1, 1), padding='SAME'))
        # self.seq.add(RELU())
        # self.seq.add(TFBatchNormalization(name='b5'))
        # h, w = same(in_height=h, in_width=w, stride=(1,1), kernel_size=(3,3))
        #
        # self.seq.add(Conv2D(input_channels=192, num_filters=192, kernel_size=(3, 3), stride=(2, 2), padding='SAME'))
        # self.seq.add(RELU())
        # h, w = same(in_height=h, in_width=w, stride=(2,2), kernel_size=(3,3))
        # self.seq.add(Dropout(0.5))
        #
        # self.seq.add(Conv2D(input_channels=192, num_filters=192, kernel_size=(3, 3), stride=(1, 1), padding='SAME'))
        # self.seq.add(RELU())
        # self.seq.add(TFBatchNormalization(name='b7'))
        # h, w = same(in_height=h, in_width=w, stride=(1,1), kernel_size=(3,3))
        #
        # self.seq.add(Conv2D(input_channels=192, num_filters=192, kernel_size=(1, 1), stride=(1, 1), padding='SAME'))
        # self.seq.add(RELU())
        # h, w = same(in_height=h, in_width=w, stride=(1,1), kernel_size=(1,1))
        # self.seq.add(Dropout(0.5))
        #
        # self.seq.add(Conv2D(input_channels=192, num_filters=nclass, kernel_size=(1, 1), stride=(1, 1), padding='SAME'))
        # self.seq.add(RELU())
        # self.seq.add(TFBatchNormalization(name='b9'))
        # h, w = same(in_height=h, in_width=w, stride=(1,1), kernel_size=(1,1))
        #
        # self.seq.add(AvgPooling(poolsize=(h, w), stride=(1,1), padding='VALID'))
        self.seq.add(Flatten())
        self.seq.add(Linear(h*w*64, 384))
        # self.seq.add(TFBatchNormalization(name='l1'))
        # self.seq.add(Dropout(0.2))
        self.seq.add(RELU())
        self.seq.add(Linear(384, 192))
        # self.seq.add(TFBatchNormalization(name='l2'))
        # self.seq.add(Dropout(0.2))
        self.seq.add(RELU())
        self.seq.add(Linear(192, nclass))
        self.seq.add(Softmax())

    # def train_loss():
    #
    # def train_accu():
    #
    # def valid_loss():
    #
    # def valid_accu():

    #     self.X = X
    #     self.y = y
    #     b, h, w, c = self.X.get_shape()
    #     h, w, c = int(h), int(w), int(c)
    #     # import pdb; pdb.set_trace()
    #     nclass = 10
    #     self.seq = tg.Sequential()
    #     self.seq.add(Conv2D(input_channels=c, num_filters=64, kernel_size=(5, 5), stride=(1, 1), padding='SAME'))
    #     self.seq.add(RELU())
    #     # self.seq.add(TFBatchNormalization(name='b1'))
    #     h, w = same(in_height=h, in_width=w, stride=(1,1), kernel_size=(3,3))
    #     self.seq.add(MaxPooling(poolsize=(3, 3), stride=(2,2), padding='SAME'))
    #     h, w = same(in_height=h, in_width=w, stride=(2,2), kernel_size=(3,3))
    #     self.seq.add(LRN(depth_radius=4, bias=1.0, alpha=0.001/9.0, beta=0.75))
    #
    #     self.seq.add(Conv2D(input_channels=64, num_filters=64, kernel_size=(5, 5), stride=(1, 1), padding='SAME'))
    #     h, w = same(in_height=h, in_width=w, stride=(1,1), kernel_size=(5,5))
    #     self.seq.add(LRN(depth_radius=4, bias=1.0, alpha=0.001/9.0, beta=0.75))
    #     self.seq.add(MaxPooling(poolsize=(3, 3), stride=(2,2), padding='SAME'))
    #     h, w = same(in_height=h, in_width=w, stride=(2,2), kernel_size=(3,3))
    #     # self.seq.add(RELU())
    #     # h, w = same(in_height=h, in_width=w, stride=(1,1), kernel_size=(3,3))
    #     # self.seq.add(Dropout(0.5))
    #     #
    #     # self.seq.add(Conv2D(input_channels=96, num_filters=96, kernel_size=(3, 3), stride=(2, 2), padding='SAME'))
    #     # self.seq.add(RELU())
    #     # # self.seq.add(TFBatchNormalization(name='b3'))
    #     # h, w = same(in_height=h, in_width=w, stride=(2,2), kernel_size=(3,3))
    #     #
    #     # self.seq.add(Conv2D(input_channels=96, num_filters=192, kernel_size=(3, 3), stride=(1, 1), padding='SAME'))
    #     # self.seq.add(RELU())
    #     # h, w = same(in_height=h, in_width=w, stride=(1,1), kernel_size=(3,3))
    #     # self.seq.add(Dropout(0.5))
    #
    #     # self.seq.add(Conv2D(input_channels=96, num_filters=192, kernel_size=(3, 3), stride=(1, 1), padding='SAME'))
    #     # self.seq.add(RELU())
    #     # self.seq.add(TFBatchNormalization(name='b5'))
    #     # h, w = same(in_height=h, in_width=w, stride=(1,1), kernel_size=(3,3))
    #     #
    #     # self.seq.add(Conv2D(input_channels=192, num_filters=192, kernel_size=(3, 3), stride=(2, 2), padding='SAME'))
    #     # self.seq.add(RELU())
    #     # h, w = same(in_height=h, in_width=w, stride=(2,2), kernel_size=(3,3))
    #     # self.seq.add(Dropout(0.5))
    #     #
    #     # self.seq.add(Conv2D(input_channels=192, num_filters=192, kernel_size=(3, 3), stride=(1, 1), padding='SAME'))
    #     # self.seq.add(RELU())
    #     # self.seq.add(TFBatchNormalization(name='b7'))
    #     # h, w = same(in_height=h, in_width=w, stride=(1,1), kernel_size=(3,3))
    #     #
    #     # self.seq.add(Conv2D(input_channels=192, num_filters=192, kernel_size=(1, 1), stride=(1, 1), padding='SAME'))
    #     # self.seq.add(RELU())
    #     # h, w = same(in_height=h, in_width=w, stride=(1,1), kernel_size=(1,1))
    #     # self.seq.add(Dropout(0.5))
    #     #
    #     # self.seq.add(Conv2D(input_channels=192, num_filters=nclass, kernel_size=(1, 1), stride=(1, 1), padding='SAME'))
    #     # self.seq.add(RELU())
    #     # self.seq.add(TFBatchNormalization(name='b9'))
    #     # h, w = same(in_height=h, in_width=w, stride=(1,1), kernel_size=(1,1))
    #     #
    #     # self.seq.add(AvgPooling(poolsize=(h, w), stride=(1,1), padding='VALID'))
    #     self.seq.add(Flatten())
    #     self.seq.add(Linear(h*w*64, 384))
    #     # self.seq.add(TFBatchNormalization(name='l1'))
    #     # self.seq.add(Dropout(0.2))
    #     self.seq.add(RELU())
    #     self.seq.add(Linear(384, 192))
    #     # self.seq.add(TFBatchNormalization(name='l2'))
    #     # self.seq.add(Dropout(0.2))
    #     self.seq.add(RELU())
    #     self.seq.add(Linear(192, nclass))
    #     self.seq.add(Softmax())
    #
    #
    def train_loss(self):
        y_pred = self.seq.train_fprop(self.X)
        # with tf.device('/gpu:0'):
        cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(
                        labels=self.y, logits=y_pred, name='cross_entropy_per_example')
        cross_entropy_mean = tf.reduce_mean(cross_entropy, name='cross_entropy')
            # import pdb; pdb.set_trace()
        return cross_entropy_mean


    def train_accu(self):

        y_pred = self.seq.train_fprop(self.X)
        # with tf.device('/cpu:0'):
            # cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(
            #                 labels=self.y, logits=y_pred, name='cross_entropy_per_example')
            # cross_entropy_mean = tf.reduce_mean(cross_entropy, name='cross_entropy')
            # # import pdb; pdb.set_trace()
            # return cross_entropy_mean
        L = tf.equal(tf.argmax(y_pred, 1), tf.to_int64(self.y))
        L = tf.reduce_mean(tf.to_float(L))
        return L
