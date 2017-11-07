
import tensorflow as tf
import time
from datetime import datetime
from model import Model
import cifar10
import numpy as np

def _update_vars(var_lists):
    update_ops = []
    for var_group in zip(*var_lists):
        avg_var = tf.reduce_mean(tf.stack(var_group), 0)
        for i, var in enumerate(var_group):
            op = var.assign(avg_var)
            update_ops.append(op)
    return update_ops



def train(num_gpus, learning_rate, batch_size=32, log_device_placement=False, save_dir='./log'):

    with tf.Graph().as_default():
        with tf.device('/cpu:0'):
            images, labels = cifar10.distorted_inputs()
            batch_queue = tf.contrib.slim.prefetch_queue.prefetch_queue(
                          [images, labels], capacity=2 * num_gpus)
            apply_gradient_ops = []
            tower_grads_vars = []
            var_lists = []
        for i in xrange(num_gpus):
            var_scope = 'GPU_{}'.format(i)
            with tf.device('/gpu:{}'.format(i)), tf.variable_scope(var_scope):
                opt = tf.train.GradientDescentOptimizer(learning_rate)
                # with tf.variable_scope('optimizer'):
                # opt
                # with tf.device('/cpu:0'):
                # opt = tf.train.MomentumOptimizer(learning_rate, momentum=0.9)

                # Dequeues one batch for the GPU
                image_batch, label_batch = batch_queue.dequeue()
                # Calculate the loss for one tower of the CIFAR model. This function
                # constructs the entire CIFAR model but shares the variables across
                # all towers.
                # loss = tower_loss(scope, image_batch, label_batch)
                with tf.name_scope('Model'):
                    model = Model(image_batch, label_batch)
                    train_loss = model.train_loss()
                    train_accu = model.train_accu()

                # print('--------')
                # print(tf.get_variable_scope().name)


                # Reuse variables for the next tower.
                # tf.get_variable_scope().reuse_variables()

                # Retain the summaries from the final tower.
                # summaries = tf.get_collection(tf.GraphKeys.SUMMARIES, scope)

                # Calculate the gradients for the batch of data on this CIFAR tower.
                var_list = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=var_scope)
        # weight_decay = tf.multiply(tf.nn.l2_loss(var), wd, name='weight_loss')
        # tf.add_to_collection('losses', weight_decay)
                # l2_loss = [tf.nn.l2_loss(var) for var in var_list]
                # ls_loss = tf.reduce_mean(l2_loss)
                # import pdb; pdb.set_trace()

                grads_and_vars = opt.compute_gradients(train_loss, var_list=var_list)
                apply_gradient_op = opt.apply_gradients(grads_and_vars)
                # opt.apply_gradients()
                # print('len grads', len(grads))
                # import pdb; pdb.set_trace()
                apply_gradient_ops.append(apply_gradient_op)


                # Keep track of the gradients across all towers.
                tower_grads_vars.append(grads_and_vars)
                var_lists.append(var_list)

        with tf.device('/cpu:1'), tf.name_scope('AverageWeights'):
            update_ops = _update_vars(var_lists)
            # copy_ops = []
            # for _ in xrange(num_gpus):
            #     copy_op = copy_var(avg_vars, var_scope='tower_{}'.format(i))
            #     copy_ops.append(copy_op)



        # Create a saver.
        # saver = tf.train.Saver(tf.global_variables())

        # Build the summary operation from the last tower summaries.
        # summary_op = tf.summary.merge(summaries)

        # Build an initialization operation to run below.
        init = tf.global_variables_initializer()

        # Start running operations on the Graph. allow_soft_placement must be set to
        # True to build towers on GPU, as some of the ops do not have GPU
        # implementations.
        sess = tf.Session(config=tf.ConfigProto(
            allow_soft_placement=True,
            log_device_placement=log_device_placement))
        sess.run(init)


        # Start the queue runners.
        tf.train.start_queue_runners(sess=sess)

        summary_writer = tf.summary.FileWriter(save_dir, sess.graph)

        for step in xrange(1000000):

            # import pdb; pdb.set_trace()
            start_time = time.time()
            #   _, loss_value = sess.run([train_op, loss])
            # train and copy variables
            # val = sess.run(var_lists[0][0])
            # print('total before apply1:', np.sum(val))
            # val = sess.run(var_lists[1][0])
            # print('total before apply2:', np.sum(val))
            sess.run(apply_gradient_ops)

            # val1 = sess.run(var_lists[0][0])
            # print('total after apply1:', np.sum(val1))
            # val2 = sess.run(var_lists[1][0])
            # print('total after apply2:', np.sum(val2))
            #

            sess.run(update_ops)
            # val3 = sess.run(var_lists[0][0])
            # print('total after update1:', np.sum(val3))
            # val4 = sess.run(var_lists[1][0])
            # print('total after update2:', np.sum(val4))
            # print('difference:', np.sum(val1+val2-val3-val4))
            # print('\n')



            loss_value = sess.run(train_loss)
            accu = sess.run(train_accu)
            # import pdb; pdb.set_trace()

            duration = time.time() - start_time
            #
            # assert not np.isnan(loss_value), 'Model diverged with loss = NaN'
            #
            if step % 100 == 0:
                num_examples_per_step = batch_size * num_gpus
                examples_per_sec = num_examples_per_step / duration
                sec_per_batch = duration / num_gpus
                format_str = ('%s: step %d, loss = %.2f, train accu = %.2f (%.1f examples/sec; %.3f '
                              'sec/batch)')
                print (format_str % (datetime.now(), step, loss_value, accu,
                                     examples_per_sec, sec_per_batch))


            # if step % 100 == 0:
            # summary_str = sess.run(summary_op)
            # summary_writer.add_summary(summary_str, step)
            #
            # # Save the model checkpoint periodically.
            # if step % 1000 == 0 or (step + 1) == FLAGS.max_steps:
            # checkpoint_path = os.path.join(FLAGS.save_dir, 'model.ckpt')
            # saver.save(sess, checkpoint_path, global_step=step)


if __name__ == '__main__':
    cifar10.maybe_download_and_extract()
    train(num_gpus=1, learning_rate=0.001, batch_size=32)
