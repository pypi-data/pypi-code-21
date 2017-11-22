# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 19:37:12 2016

@author: aeloyq
"""
import numpy as np
import types
import copy
import os
import tools
import extensions
from logger import logger
from collections import OrderedDict
from nnbuilder.kernel import *
from extensions import monitor
from nnbuilder.optimizers import gradientdescent


class Config:
    def __init__(self):
        self.name = 'unamed'
        self.batch_size = 20
        self.valid_batch_size = 64
        self.max_epoch = 50
        self.savelog = True
        self.verbose = 5

    def set(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    def is_log_detail(self):
        return self.verbose < 0 or self.verbose >= 5

    def is_log_inline(self):
        return self.verbose > 1 and self.verbose < 5

    def is_log_silent(self):
        return self.verbose in [0, 1]


config = Config()


class DataStream:
    def __init__(self, size, buffer_size, valid_buffer_size, test_buffer_size):
        '''

        :param size:
        :param valid_size:
        :param test_size:
        :param buffer_size:
        :param valid_buffer_size:
        :param test_buffer_size:
        '''
        self.indices = np.asarray([])
        self.size = size
        self.buffer_x = None
        self.buffer_y = None
        self.buffer_size = buffer_size
        self.buffer_list = []
        self.valid_indices = np.asarray([])
        self.valid_size = 0
        self.valid_buffer_x = None
        self.valid_buffer_y = None
        if valid_buffer_size is None:
            valid_buffer_size = buffer_size
        self.valid_buffer_size = valid_buffer_size
        self.valid_buffer_list = []
        self.test_indices = np.asarray([])
        self.test_size = 0
        self.test_buffer_x = None
        self.test_buffer_y = None
        if test_buffer_size is None:
            test_buffer_size = buffer_size
        self.test_buffer_size = test_buffer_size
        self.test_buffer_list = []
        self.splitted = False

    def read(self, i):
        return []

    def readx(self, buffer, batchindex, size, batch_size, indices=None):
        return [[]]

    def ready(self, buffer, batchindex, size, batch_size, indices=None):
        return [[]]

    def loadx(self, buffer_list, size, buffer_size, batch_size, indices=None):
        return None

    def loady(self, buffer_list, size, buffer_size, batch_size, indices=None):
        return None

    def preload(self, batchindex, buffer_x, buffer_y, buffer_list, readlist, size, buffer_size, batch_size,
                indices=None):
        if batchindex not in buffer_list:
            preread_batch_num = buffer_size
            start = readlist.index(batchindex)
            buffer_list = readlist[start:start + preread_batch_num]
            buffer_x = self.loadx(buffer_list, size, buffer_size, batch_size, indices=None)
            buffer_y = self.loady(buffer_list, size, buffer_size, batch_size, indices=None)
        return buffer_x, buffer_y, buffer_list

    def get_train(self, batchindex, readlist, size, batch_size):
        '''
        Read the train data by given indices in minibatch
        Pre-read data by buffer_size
        :param batch: index of minibatch to load currently
        :param readlist:  entire batch list of train set
        :param batchsize:  size of a single batch
        :return: [train_X, train_Y]
        '''
        self.preload(batchindex, self.buffer_x, self.buffer_y, self.buffer_list, readlist, size, self.buffer_size,
                     batch_size, self.indices)
        train_X = self.readx(self.buffer_x, batchindex, size, batch_size, self.indices)
        train_Y = self.ready(self.buffer_y, batchindex, size, batch_size, self.indices)
        return [train_X, train_Y]

    def get_single_train(self, index):
        '''
        Read the train data by given indices in minibatch
        Pre-read data by buffer_size
        :param batch: index of minibatch to load currently
        :param readlist:  entire batch list of train set
        :param batchsize:  size of a single batch
        :return: [train_X, train_Y]
        '''
        return self.read(self.get_index(index, self.indices))

    def get_valid(self, batchindex, readlist, size, batch_size):
        '''
        Read the train data by given indices in minibatch
        Pre-read data by buffer_size
        :param batch: index of minibatch to load currently
        :param readlist:  entire batch list of train set
        :param batchsize:  size of a single batch
        :return: [train_X, train_Y]
        '''
        self.preload(batchindex, self.valid_buffer_x, self.valid_buffer_y, self.valid_buffer_list, readlist, size,
                     self.valid_buffer_size,
                     batch_size, self.valid_indices)
        valid_X = self.readx(self.valid_buffer_x, batchindex, size, batch_size, self.valid_indices)
        valid_Y = self.ready(self.valid_buffer_y, batchindex, size, batch_size, self.valid_indices)
        return [valid_X, valid_Y]

    def get_single_valid(self, index):
        '''
        Read the train data by given indices in minibatch
        Pre-read data by buffer_size
        :param batch: index of minibatch to load currently
        :param readlist:  entire batch list of train set
        :param batchsize:  size of a single batch
        :return: [train_X, train_Y]
        '''

        return self.read(self.get_index(index, self.valid_indices))

    def get_test(self, batchindex, readlist, size, batch_size):
        '''
        Read the train data by given indices in minibatch
        Pre-read data by buffer_size
        :param batch: index of minibatch to load currently
        :param readlist:  entire batch list of train set
        :param batchsize:  size of a single batch
        :return: [train_X, train_Y]
        '''

        self.preload(batchindex, self.test_buffer_x, self.test_buffer_y, self.test_buffer_list, readlist, size,
                     self.test_buffer_size,
                     batch_size, self.test_indices)
        test_X = self.readx(self.test_buffer_x, batchindex, size, batch_size, self.test_indices)
        test_Y = self.ready(self.test_buffer_y, batchindex, size, batch_size, self.test_indices)
        return [test_X, test_Y]

    def get_single_test(self, index):
        '''
        Read the train data by given indices in minibatch
        Pre-read data by buffer_size
        :param batch: index of minibatch to load currently
        :param readlist:  entire batch list of train set
        :param batchsize:  size of a single batch
        :return: [train_X, train_Y]
        '''

        return self.read(self.get_index(index, self.test_indices))

    def get_split_indices(self, size, portion):
        indices = np.sort(np.random.permutation(size)[:np.round(size * portion)])
        return indices

    def autosplit(self, portion, split):
        self.valid_indices = self.get_split_indices(self.size, portion)
        self.test_indices = self.get_split_indices(self.size, portion)
        if split:
            self.splitted = True
            indices = range(self.size)
            splitted_indices = []
            for i in indices:
                if i not in self.valid_indices:
                    splitted_indices.append(i)
            indices = splitted_indices
            splitted_indices = []
            for i in indices:
                if i not in self.test_indices:
                    splitted_indices.append(i)
            self.indices = splitted_indices

    def get_minibatch_indices(self, batchindex, size, batch_size, indices=None):
        if not self.splitted:
            return DataFrame.get_minibatch_indices(batchindex, size, batch_size)
        else:
            return indices[DataFrame.get_minibatch_indices(batchindex, size, batch_size)]

    def get_index(self, index, indices=None):
        if not self.splitted:
            return index
        else:
            return indices[index]

    def __setattr__(self, key, value):
        self.__dict__[key] = np.asarray(value)
        if key is 'indices':
            self.size = len(self.indices)
        elif key is 'valid_indices':
            self.valid_size = len(self.valid_indices)
        elif key is 'test_indices':
            self.test_size = len(self.test_indices)


class DataFrame:
    def __init__(self, train=None, valid=None, test=None, size=None, portion=0.2, stream=None):
        self.train = train
        self.valid = valid
        self.test = test
        self.size = size
        self.valid_size = 0
        self.test_size = 0
        self.portion = portion
        self.stream = stream
        self.prepare()

    def prepare(self):
        # determine whether to read stream
        if self.train is not None:
            self._read_stream = False
        elif self.stream is not None:
            self._read_stream = True
        else:
            assert AssertionError('Data not given!')
        # prepare data
        if not self._read_stream:
            self.size = len(self.train[1])
            if self.valid is None:
                valid_idx = self.auto_split_indices()
                self.valid = [self.train[0][valid_idx], self.train[1][valid_idx]]
                self.valid_size = len(valid_idx)
                test_idx = self.auto_split_indices()
                self.test = [self.train[0][test_idx], self.train[1][test_idx]]
                self.test_size = len(test_idx)
            else:
                self.valid_size = len(self.valid[1])
                self.test_size = len(self.test[1])
        else:
            self.size = self.stream.size
            if self.valid is None:
                self.valid = self.stream.autosplit()
                self.valid_size = self.stream.valid_size
            else:
                self.valid_size = len(self.valid[1])
            if self.test is None:
                self.test = self.stream.autosplit()
                self.test_size = self.stream.test_size
            else:
                self.test_size = len(self.test[1])

    @staticmethod
    def get_batch_indices(size, batch_size):
        n_minibatches = (size - 1) // batch_size + 1
        return range(n_minibatches)

    @staticmethod
    def get_minibatch_indices(batchindex, size, batch_size):
        return np.arange(batchindex * batch_size, min(size, (batchindex + 1) * batch_size))

    def get_train(self):
        if not self._read_stream:
            return self.train
        else:
            train = []
            batch_list = self.get_batch_indices(self.size, config.batch_size)
            for i in batch_list:
                train.extend(self.stream.get_train(i, batch_list, self.size, config.batch_size))
            return train

    def get_single_train(self, index):
        if not self._read_stream:
            return [self.train[0][[index]], self.train[1][[index]]]
        else:
            return self.stream.get_single_train(index)

    def get_minibatch_train(self, batch_index, batch_list):
        minibatch_indices = self.get_minibatch_indices(batch_index, self.size, config.batch_size)
        if not self._read_stream:
            return [self.train[0][minibatch_indices], self.train[1][minibatch_indices]]
        else:
            return self.stream.get_train(batch_index, batch_list, self.size, config.batch_size)

    def get_valid(self):
        if self.valid is not None:
            return self.valid
        else:
            valid = []
            batch_list = self.get_batch_indices(self.valid_size, config.valid_batch_size)
            for i in batch_list:
                valid.extend(self.stream.get_valid(i, batch_list, self.valid_size, config.valid_batch_size))
            return valid

    def get_single_valid(self, index):
        if self.valid is not None:
            return [self.valid[0][[index]], self.valid[1][[index]]]
        else:
            return self.stream.get_single_valid(index)

    def get_minibatch_valid(self, batch_index):
        minibatch_indices = self.get_minibatch_indices(batch_index, self.valid_size, config.valid_batch_size)
        batch_list = self.get_batch_indices(self.valid_size, config.valid_batch_size)
        if not self._read_stream:
            return [self.valid[0][minibatch_indices], self.valid[1][minibatch_indices]]
        else:
            return self.stream.get_train(batch_index, batch_list, self.size, config.batch_size)

    def get_test(self):
        if self.test is not None:
            return self.test
        else:
            test = []
            batch_list = self.get_batch_indices(self.test_size, config.valid_batch_size)
            for i in batch_list:
                test.extend(self.stream.get_test(i, batch_list, self.test_size, config.valid_batch_size))
            return test

    def get_single_test(self, index):
        if self.test is not None:
            return [self.test[0][[index]], self.test[1][[index]]]
        else:
            return self.stream.get_single_test(index)

    def get_minibatch_test(self, batch_index):
        minibatch_indices = self.get_minibatch_indices(batch_index, self.test_size, config.valid_batch_size)
        batch_list = self.get_batch_indices(self.test_size, config.valid_batch_size)
        if not self._read_stream:
            return [self.test[0][minibatch_indices], self.test[1][minibatch_indices]]
        else:
            return self.stream.get_train(batch_index, batch_list, self.size, config.batch_size)

    def auto_split_indices(self):
        return np.sort(np.random.permutation(self.size)[:np.round(self.size * self.portion)])


class MainLoop:
    def __init__(self):
        '''

        '''
        pass

    @staticmethod
    def train(data, model, optimizer=gradientdescent.sgd, extensions=(monitor,), verbose=None):
        '''

        :param data:
        :param model:
        :param optimizer:
        :param extensions:
        :param stream:
        :param stream_load:
        :return:
        '''
        if verbose is not None:
            config.verbose = verbose
        # Prepare train
        MainLoop.init_nnb()
        MainLoop.init_datas(data)
        model.build()
        model.optimize(optimizer)
        MainLoop.print_config(model, optimizer, extensions)
        model.compile()
        logger("Train   Model", 0, 1)
        max_epoch = config.max_epoch
        train_history = {}
        train_history['name'] = config.name
        train_history['n_epoch'] = 0
        train_history['n_iter'] = 0
        train_history['iter'] = 0
        train_history['stop'] = False
        train_history['train_loss'] = 1
        train_history['train_losses'] = []
        train_history['losses'] = []
        train_history['scores'] = OrderedDict()
        for m in model.metrics:
            train_history['scores'][m.name] = []
        for ex in extensions:
            ex.build(MainLoop, model, data, extensions, config, logger, train_history)

        # Main
        logger('Training Start', 1)
        for ex in extensions:   ex.before_train()
        if train_history['stop']:
            logger("Training Finished", 1, 1)
            return
        while (True):
            # Prepare data
            train_history['minibatch_list'] = DataFrame.get_batch_indices(data.size, config.batch_size)
            # Stop When Timeout
            if train_history['n_epoch'] > max_epoch - 1 and max_epoch != -1:
                logger("Training Finished", 1, 1)
                break
            # Iniate test
            if train_history['n_iter'] == 0:
                for ex in extensions:   ex.before_init_iter()
                MainLoop.test(model, data, train_history)
                for ex in extensions:   ex.after_init_iter()

            # Train model iter by iter

            for ex in extensions:   ex.before_epoch()

            for iter, index in enumerate(train_history['minibatch_list']):
                train_history['iter'] = iter

                for ex in extensions:   ex.before_iteration()

                train_X, train_Y = data.get_minibatch_train(index, train_history['minibatch_list'])
                train_history['train_loss'] = model.train(train_X, train_Y)
                train_history['n_iter'] += 1

                for ex in extensions:   ex.after_iteration()

                # After epoch
                if (iter == (data.size - 1) // config.batch_size):
                    train_history['train_losses'].append(train_history['train_loss'])
                    train_history['n_epoch'] += 1
                    MainLoop.test(model, data, train_history)

                    for ex in extensions:   ex.after_epoch()

                # Stop when needed
                if train_history['stop']:
                    for ex in extensions:   ex.after_train()
                    return

        for ex in extensions:   ex.after_train()

        logger("Finished", 0, 1)

        return train_history

    @staticmethod
    def valid(model, data):
        minibatch_list = DataFrame.get_batch_indices(data.valid_size, config.valid_batch_size)
        result = {'loss': []}
        for i, m in enumerate(model.metrics):
            result[m.name] = []
        for index in minibatch_list:
            valid_X, valid_Y = data.get_minibatch_valid(index)
            valid_result = model.valid(valid_X, valid_Y)
            result['loss'].extend(valid_result['loss'])
            for i, m in enumerate(model.metrics):
                result[m.name].extend(valid_result[m.name])
        result['loss'] = np.mean(result['loss'])
        for i, m in enumerate(model.metrics):
            result[m.name] = np.mean(result[m.name])
        return result

    @staticmethod
    def test(model, data, train_history, write_history=True):
        minibatch_list = DataFrame.get_batch_indices(data.test_size, config.valid_batch_size)
        result = {'loss': []}
        for i, m in enumerate(model.metrics):
            result[m.name] = []
        for index in minibatch_list:
            test_X, test_Y = data.get_minibatch_test(index)
            test_result = model.valid(test_X, test_Y)
            result['loss'].extend(test_result['loss'])
            for i, m in enumerate(model.metrics):
                result[m.name].extend(test_result[m.name])
        result['loss'] = np.mean(result['loss'])
        for i, m in enumerate(model.metrics):
            result[m.name] = np.mean(result[m.name])
        if write_history:
            train_history['losses'].append(result['loss'])
            for i, m in enumerate(model.metrics):
                train_history['scores'][m.name].append(result[m.name])
        return result

    @staticmethod
    def debug(data, model, optimizer=gradientdescent.sgd):
        model.build()
        model.optimize(optimizer)
        model.compile(optimizer)
        extensions.debug.build(MainLoop, model, data, [], config, logger, {})
        return extensions.debug.config.debug()

    @staticmethod
    def init_nnb():
        # generate documents
        if not os.path.exists('./%s' % config.name):
            os.mkdir('./%s' % config.name)
        if not os.path.exists('./%s/log' % config.name):
            os.mkdir('./%s/log' % config.name)
        if not os.path.exists('./%s/save' % config.name):
            os.mkdir('./%s/save' % config.name)
        if not os.path.exists('./%s/save/epoch' % config.name):
            os.mkdir('./%s/save/epoch' % config.name)
        if not os.path.exists('./%s/save/final' % config.name):
            os.mkdir('./%s/save/final' % config.name)
        if not os.path.exists('./%s/save/valid' % config.name):
            os.mkdir('./%s/save/valid' % config.name)
        if not os.path.exists('./%s/save/valid/best' % config.name):
            os.mkdir('./%s/save/valid/best' % config.name)
        if not os.path.exists('./%s/plot' % config.name):
            os.mkdir('./%s/plot' % config.name)
        if not os.path.exists('./%s/plot/model' % config.name):
            os.mkdir('./%s/plot/model' % config.name)
        if not os.path.exists('./%s/plot/progress' % config.name):
            os.mkdir('./%s/plot/progress' % config.name)

    @staticmethod
    def init_datas(data):
        logger("Process Data", 0, 1)
        v_num = data.valid_size
        t_num = data.test_size
        v_batches = (v_num - 1) // config.valid_batch_size + 1
        t_batches = (t_num - 1) // config.valid_batch_size + 1
        info = [['Datasets', '|', 'Train', '|', 'Valid', '|', 'Test']]
        strip = [15, 1, 22, 1, 22, 1, 22]
        info.append(
            ["=" * strip[0], "|" * strip[1], "=" * strip[2], "|" * strip[3], "=" * strip[4], "|" * strip[5],
             "=" * strip[6]])
        num = data.size
        batches = (num - 1) // config.batch_size + 1
        info.append(['Detail', '|', '{}*{}'.format(batches, config.batch_size), '|', '{}*{}'.format(v_batches,
                                                                                                    config.valid_batch_size),
                     '|', '{}*{}'.format(t_batches, config.valid_batch_size)])
        info.append(['Total', '|', '{}'.format(num), '|', '{}'.format(v_num), '|', '{}'.format(t_num)])
        if config.is_log_detail():
            logger(tools.printer.paragraphformatter(info, LengthList=strip, Align='center'), 1)

    @staticmethod
    def print_config(model, optimizer, extension):
        def get_info(key, item, column, truthvalue=True, stringvalue=True):
            if key.startswith('_'):
                pass
            elif type(item) == int or type(item) == float:
                column.append('{} = {}'.format(key, item))
            elif type(item) == types.BooleanType and truthvalue:
                column.append('{} = {}'.format(key, item))
            elif type(item) == types.StringType and stringvalue and item.strip() != "":
                column.append('{} = {}'.format(key, item))

        strip = [0, 0, 28, 1, 28, 1, 28]

        logger('Build   Model', 0, 1)
        info_all = []
        info_all.append(['', ' ', 'Global', '|', 'Graph', '|', 'Extension'])
        info_all.append(
            [" " * strip[0], " " * strip[1], "=" * strip[2], "|" * strip[3], "=" * strip[4], "|" * strip[5],
             "=" * strip[6]])

        first_column_info = []
        for key in config.__dict__:
            if not key.startswith('__'):
                get_info(key, config.__dict__[key], first_column_info)
        first_column_info.extend(["", "Model", "=" * strip[4]])
        tmp_column_info = []
        for key in model.__dict__:
            if not key.startswith('__'):
                get_info(key, model.__dict__[key], tmp_column_info)
        first_column_info.extend(tmp_column_info)

        first_column_info.extend(["", "Optimizer:%s" % (optimizer.__class__.__name__), "=" * strip[-1]])

        for key in optimizer.__dict__:
            if not key.startswith('__'):
                get_info(key, optimizer.__dict__[key], first_column_info)

        second_column_info = []

        for lykey in model.layers:
            second_column_info.extend([lykey + " " * strip[-1], "-" * strip[-1]])
            for key in model.layers[lykey].__dict__:
                if not key.startswith('__'):
                    get_info(key, model.layers[lykey].__dict__[key], second_column_info, truthvalue=False)
            second_column_info.append("")

        third_column_info = []
        for ex in extension:
            third_column_info.extend([ex.__class__.__name__ + " " * strip[-1], "-" * strip[-1]])
            for key in ex.__dict__:
                get_info(key, ex.__dict__[key], third_column_info)
            third_column_info.append("")
        if third_column_info != []:
            third_column_info.pop(-1)

        for i in range(max(len(first_column_info), len(second_column_info), len(third_column_info))):
            info_all.append([''])
            info_all[i + 2].append(' ')
            if i < len(first_column_info):
                info_all[i + 2].append(first_column_info[i])
            else:
                info_all[i + 2].append("")
            info_all[i + 2].append('|')
            if i < len(second_column_info):
                info_all[i + 2].append(second_column_info[i])
            else:
                info_all[i + 2].append("")
            info_all[i + 2].append('|')
            if i < len(third_column_info):
                info_all[i + 2].append(third_column_info[i])
            else:
                info_all[i + 2].append("")
        if config.is_log_detail():
            logger(tools.printer.paragraphformatter(info_all, LengthList=strip, Align='center'), 1)


# Shortcuts
train = MainLoop.train
debug = MainLoop.debug
