import tensorflow as tf
import numpy as np


def test_var():
    with tf.device('/cpu:0'):
        # x = tf.Variable(np.zeros(1e4,1e6), name='x')
        x = tf.get_variable(
            'global_step', [1e4, 1e6],
            initializer=tf.constant_initializer(0), trainable=False)
    with tf.device('/gpu:0'):
        y = x + x
        # z = tf.sqrt(y)
        m = tf.reduce_mean(y)

    init = tf.global_variables_initializer()
    with tf.Session() as sess:
        print('init')
        sess.run(init)
        print('run')
        print(sess.run(m))



def test_scope():
    with tf.variable_scope('test1'):
        with tf.variable_scope('test2'):
            x = tf.Variable([1], name='conv')
            print(x.name)
            y = tf.Variable([2] , name='conv')
            print(y.name)
            print(tf.get_variable_scope().name)
            z = tf.get_variable('var', [1])
            print(z.name)
            tf.get_variable_scope().reuse_variables()
            a = tf.get_variable('var')
            print(a.name)
        tf.get_variable('test1', [])

def concats():
    k1 = tf.constant(np.random.rand(10,3))
    k2 = tf.constant(np.random.rand(10,3))
    tf.stack(axis=0, values=[k1, k2])
        # out = tf.concat([tf.constant(2, 10), tf.constant(2, 10)])
        # print(out)


def scopes():

    import tensorflow as tf

    opt = tf.train.GradientDescentOptimizer(0.01)
    with tf.device('/cpu:0'):
        for i in range(3):
            with tf.variable_scope('variable_scope_cpu1') as scope:
                print('scope1:', scope.name)
                with tf.variable_scope('variable_scope_cpu2') as scope:
                    print('scope2:', scope.name)
                    with tf.name_scope('namescope_{}'.format(i)):
                        with tf.device('gpu:1'):

                            print('====[{}]===='.format(i))
                            print('==scope name:', tf.get_variable_scope().name)
                            a = tf.get_variable('gpuvar1', [2,3])
                            print('var', a)
                            tf.get_variable_scope().reuse_variables()


                            print('scope name:', scope)
                            # a.name
                            x = tf.expand_dims(a, 0)
                            print('tensor', x)
                            # with tf.variable_scope('var'):
                            #     y = tf.get_variable('test', [2,3])
                            #     z = x + y
                            #     print('y', y.name)
                            #     print('z', z.name)
                            #     print(tf.get_variable_scope().name)
                            #     # print(tf.get_collection())


                        # y = tf.get_variable('cpuvar1', [1,2,3])

                        # loss = x - y
                        # var_list = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope='variable_scope_cpu0_{}'.format(i))
                        # grad = opt.compute_gradients(x, var_list=var_list)
                        # print(grad)
                        # print(len(grad))
                        # grad[0][1]

                        # print(scope.name)
                        # print(tf.get_variable_scope().name)
    # opt2 = tf.train.GradientDescentOptimizer(0.01)
    # opt2.apply_gradients(grad)

# scopes()
        # with tf.variable_scope('test', reuse=True):
        #     y = tf.get_variable('myname', [1,2,3])
        #
        # print(tf.GraphKeys.SUMMARIES)
    # with tf.device('/gpu:1'):
    #     with tf.variable_scope('variable_scope_gpu0'):
    #         x = tf.get_variable('var2', [1,2,3])
    # init = tf.global_variables_initializer()
    # with tf.Session(config=tf.ConfigProto(
    #     allow_soft_placement=True,
    #     log_device_placement=True)) as sess:
    #     sess.run(init)
    #     summary_writer = tf.summary.FileWriter('./log', sess.graph)
# concats()

from dicomutils.data_processing import construct3DfromPatient, seriesFlatten

patient_dir = '/data/tiantan/svd/clean/001653359'
seriesgroup = ['OAx T2 FLAIR']
arr = construct3DfromPatient(patient_dir, seriesgroup, resize_shape=None, lower=False)

for i in range(arr.shape[0]):
    plt.figure()
    plt.imshow(arr[i])
    plt.show()


arr.shape
arr.max()
arr.min()
# seriesFlatten(arr).shape
import matplotlib.pyplot as plt
plt.figure()
plt.imshow(seriesFlatten(arr))
plt.show()




if __name__ == '__main__':
    test_var()
