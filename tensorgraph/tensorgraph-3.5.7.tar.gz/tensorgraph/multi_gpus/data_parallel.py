
import tensorflow as tf
import time
from datetime import datetime
from model import Model
import cifar10
import numpy as np

# def _update_vars(var_lists):
#     update_ops = []
#     for var_group in zip(*var_lists):
#         avg_var = tf.reduce_mean(tf.stack(var_group), 0)
#         for i, var in enumerate(var_group):
#             op = var.assign(avg_var)
#             update_ops.append(op)
#     return update_ops



def build(model, model_var_list, num_gpus):

    with tf.Graph().as_default():
        # with tf.device('/cpu:0'):
        #     images, labels = cifar10.distorted_inputs()
        #     batch_queue = tf.contrib.slim.prefetch_queue.prefetch_queue(
        #                   [images, labels], capacity=2 * num_gpus)
        apply_gradient_ops = []
        # tower_grads_vars = []
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
                # image_batch, label_batch = batch_queue.dequeue()
                # Calculate the loss for one tower of the CIFAR model. This function
                # constructs the entire CIFAR model but shares the variables across
                # all towers.
                # loss = tower_loss(scope, image_batch, label_batch)
                # with tf.name_scope('Model'):
                model = model(*model_var_list)
                train_loss = model.train_loss()

                    # train_accu = model.train_accu()

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
                # tower_grads_vars.append(grads_and_vars)
                var_lists.append(var_list)

        with tf.device('/cpu:1'), tf.name_scope('AverageWeights'):
            # update_ops = _update_vars(var_lists)
            update_ops = []
            for var_group in zip(*var_lists):
                avg_var = tf.reduce_mean(tf.stack(var_group), 0)
                for i, var in enumerate(var_group):
                    op = var.assign(avg_var)
                    update_ops.append(op)
    return update_ops, apply_gradient_ops, model


def train(log_dir = './log'):
    with tf.Graph().as_default():

        X_train, y_train, X_test, y_test = Cifar10(contrast_normalize=False, whiten=False)
        # X_train, y_train, X_test, y_test = Mnist(flatten=False, onehot=True, binary=True, datadir='.')
        _, h, w, c = X_train.shape
        _, nclass = y_train.shape

        seq = model(nclass=nclass, h=h, w=w, c=c)
        iter_train = tg.SequentialIterator(X_train, y_train, batchsize=batchsize)
        iter_test = tg.SequentialIterator(X_test, y_test, batchsize=batchsize)


        X_ph = tf.placeholder('float32', [None, h, w, c])
        y_ph = tf.placeholder('float32', [None, nclass])

            # from .model import model
            # X = tf.placeholder()
            # y = tf.placeholder()
        model_var_list = [X_ph, y_ph]
        num_gpus = 2
        update_ops, apply_gradient_ops, model = build(Model, model_var_list, num_gpus)
        train_loss = model.train_accu(X_ph, y_ph)


        # return update_ops


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
            # tf.train.start_queue_runners(sess=sess)

        summary_writer = tf.summary.FileWriter(log_dir, sess.graph)

            # for step in xrange(1000000):

                # import pdb; pdb.set_trace()
                # start_time = time.time()
                #   _, loss_value = sess.run([train_op, loss])
                # train and copy variables
                # val = sess.run(var_lists[0][0])
                # print('total before apply1:', np.sum(val))
                # val = sess.run(var_lists[1][0])
                # print('total before apply2:', np.sum(val))
                # sess.run(apply_gradient_ops, feed_dict={X:, y:})

                # val1 = sess.run(var_lists[0][0])
                # print('total after apply1:', np.sum(val1))
                # val2 = sess.run(var_lists[1][0])
                # print('total after apply2:', np.sum(val2))
                #
                # sess.run(update_ops)
                # val3 = sess.run(var_lists[0][0])
                # print('total after update1:', np.sum(val3))
                # val4 = sess.run(var_lists[1][0])
                # print('total after update2:', np.sum(val4))
                # print('difference:', np.sum(val1+val2-val3-val4))
                # print('\n')



        # train_arrs = []
        # valid_arrs = []
        # phs = []
        # for ph, arr in feed_dict.items():
        #     train_arr, valid_arr = split_arr(arr, train_valid_ratio, randomize=randomize_split)
        #     phs.append(ph)
        #     train_arrs.append(train_arr)
        #     valid_arrs.append(valid_arr)
        #
        # iter_train = SequentialIterator(*train_arrs, batchsize=batchsize)
        # iter_valid = SequentialIterator(*valid_arrs, batchsize=batchsize)

        es = EarlyStopper(max_epoch, epoch_look_back, percent_decrease)

        epoch = 0
        while True:
            epoch += 1
            ##############################[ Training ]##############################
            print('\n')
            logger.info('<<<<<[ epoch: {} ]>>>>>'.format(epoch))
            logger.info('..training')
            pbar = ProgressBar(len(iter_train))
            ttl_exp = 0
            mean_train_cost = 0
            for X_batch, y_batch in iter_train:
                # fd = dict(zip(phs, batches))
                fd = {X_ph:X_batch, y_ph:y_batch}
                sess.run(apply_gradient_ops, feed_dict=fd)
                sess.run(update_ops)

                # train_cost, _ = session.run([train_cost_sb, optimizer], feed_dict=fd)
                train_cost = session.run(train_loss, feed_dict=fd)
                mean_train_cost += train_cost * len(X_batch)
                ttl_exp += len(X_batch)
                pbar.update(ttl_exp)

            # print('')
            # mean_train_cost /= ttl_exp
            # logger.info('..average train cost: {}'.format(mean_train_cost))
            #
            # ##############################[ Validating ]############################
            # logger.info('..validating')
            # pbar = ProgressBar(len(iter_valid))
            # ttl_exp = 0
            # mean_valid_cost = 0
            # for batches in iter_valid:
            #     fd = dict(zip(phs, batches))
            #     valid_cost = session.run(valid_cost_sb, feed_dict=fd)
            #     mean_valid_cost += valid_cost * len(batches[0])
            #     ttl_exp += len(batches[0])
            #     pbar.update(ttl_exp)
            #
            # print('')
            # mean_valid_cost /= ttl_exp
            # logger.info('..average valid cost: {}'.format(mean_valid_cost))
            #
            # if es.continue_learning(mean_valid_cost, epoch=epoch):
            #     logger.info('best epoch last update: {}'.format(es.best_epoch_last_update))
            #     logger.info('best valid last update: {}'.format(es.best_valid_last_update))
            # else:
            #     logger.info('training done!')
            #     break

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
