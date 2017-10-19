# conx - a neural network library
#
# Copyright (c) Douglas S. Blank <doug.blank@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301  USA

"""
The network module contains the code for the Network class.
"""

import collections
import operator
import importlib
from functools import reduce
import signal
import numbers
import random
import pickle
import base64
import html
import copy
import io
import os
import re
import PIL
from typing import Any

import numpy as np
import keras

from .utils import *
from .layers import Layer
from .dataset import Dataset


try:
    from IPython import get_ipython
except:
    get_ipython = lambda: None

#------------------------------------------------------------------------

class Network():
    """
    The main class for the conx neural network package.

    Arguments:
        name: Required. The name of the network. Should not contain special HTML
           characters.
        sizes: Optional numbers. Defines the sizes of layers of a sequential
           network. These will be created, added, and connected automatically.
        config: Configuration overrides for the network.

    Note:
        To create a complete, operating network, you must do the following items:

        1. create a network
        2. add layers
        3. connect the layers
        4. compile the network
        5. set the dataset
        6. train the network

        See also :any:`Layer`, :any:`Network.add`, :any:`Network.connect`,
        and :any:`Network.compile`.

    Examples:
        >>> net = Network("XOR1", 2, 5, 2)
        >>> len(net.layers)
        3

        >>> net = Network("XOR2")
        >>> net.add(Layer("input", 2))
        >>> net.add(Layer("hidden", 5))
        >>> net.add(Layer("output", 2))
        >>> net.connect()
        >>> len(net.layers)
        3

        >>> net = Network("XOR3")
        >>> net.add(Layer("input", 2))
        >>> net.add(Layer("hidden", 5))
        >>> net.add(Layer("output", 2))
        >>> net.connect("input", "hidden")
        >>> net.connect("hidden", "output")
        >>> len(net.layers)
        3

        >>> net = Network("NMIST")
        >>> net.name
        'NMIST'
        >>> len(net.layers)
        0

        >>> net = Network("NMIST", 10, 5, 1)
        >>> len(net.layers)
        3

        >>> net = Network("NMIST", 10, 5, 5, 1, activation="sigmoid")
        >>> net.config["activation"]
        'sigmoid'
        >>> net["output"].activation == "sigmoid"
        True
        >>> net["hidden1"].activation == "sigmoid"
        True
        >>> net["hidden2"].activation == "sigmoid"
        True
        >>> net["input"].activation is None
        True
        >>> net.layers[0].name == "input"
        True
    """
    OPTIMIZERS = ("sgd", "rmsprop", "adagrad", "adadelta", "adam",
                  "adamax", "nadam", "tfoptimizer")
    def __init__(self, name: str, *sizes: int, **config: Any):
        if not isinstance(name, str):
            raise Exception("first argument should be a name for the network")
        self.debug = False
        self.config = {
            "font_size": 12, # for svg
            "font_family": "monospace", # for svg
            "border_top": 25, # for svg
            "border_bottom": 25, # for svg
            "hspace": 150, # for svg
            "vspace": 30, # for svg, arrows
            "image_maxdim": 200, # for svg
            "image_pixels_per_unit": 50, # for svg
            "activation": "linear", # Dense default, if none specified
            "arrow_color": "black",
            "arrow_width": "2",
            "border_width": "2",
            "border_color": "black",
            "show_targets": False,
            "show_errors": False,
            "minmax": None,
            "colormap": None,
            "pixels_per_unit": 1,
            "precision": 2,
            "svg_height": 780, # for svg
        }
        if not isinstance(name, str):
            raise Exception("conx layers need a name as a first parameter")
        self.input_bank_order = []
        self.output_bank_order = []
        self.config.update(config)
        self.dataset = Dataset(self)
        self.compile_options = {}
        self.train_options = {}
        self.name = name
        self.layers = []
        self.layer_dict = {}
        # If simple feed-forward network:
        for i in range(len(sizes)):
            if i > 0:
                self.add(Layer(autoname(i, len(sizes)), shape=sizes[i],
                               activation=self.config["activation"]))
            else:
                self.add(Layer(autoname(i, len(sizes)), shape=sizes[i]))
        # Connect them together:
        for i in range(len(sizes) - 1):
            self.connect(autoname(i, len(sizes)), autoname(i+1, len(sizes)))
        self.epoch_count = 0
        self.acc_history = []
        self.loss_history = []
        self.val_percent_history = []
        self.visualize = get_ipython() is not None
        self._comm = None
        self.model = None
        self.prop_from_dict = {}
        self._svg_counter = 1

    def __getitem__(self, layer_name):
        if layer_name not in self.layer_dict:
            return None
        else:
            return self.layer_dict[layer_name]

    def _repr_html_(self):
        if all([layer.model for layer in self.layers]):
            return self.build_svg()
        else:
            return None

    def __repr__(self):
        return "<Network name='%s' (%s)>" % (
            self.name, ("uncompiled" if not self.model else "compiled"))

    def snapshot(self, inputs=None, class_id=None, ):
        from IPython.display import HTML
        if class_id is None:
            r = random.randint(1,1000000)
            class_id = "snapshot-%s-%s" % (self.name, r)
        return HTML(self.build_svg(class_id=class_id, inputs=inputs))

    def add(self, layer: Layer):
        """
        Add a layer to the network layer connections. Order is not
        important, unless calling :any:`Network.connect` without any
        arguments.

        Arguments:
            layer: A layer instance.

        Examples:
            >>> net = Network("XOR2")
            >>> net.add(Layer("input", 2))
            >>> len(net.layers)
            1

            >>> net = Network("XOR3")
            >>> net.add(Layer("input", 2))
            >>> net.add(Layer("hidden", 5))
            >>> net.add(Layer("output", 2))
            >>> len(net.layers)
            3

        Note:
            See :any:`Network` for more information.
        """
        if layer.name in self.layer_dict:
            raise Exception("duplicate layer name '%s'" % layer.name)
        self.layers.append(layer)
        self.layer_dict[layer.name] = layer

    def connect(self, from_layer_name:str=None, to_layer_name:str=None):
        """
        Connect two layers together if called with arguments. If
        called with no arguments, then it will make a sequential
        run through the layers in order added.

        Arguments:
            from_layer_name: Name of layer where connect begins.
            to_layer_name: Name of layer where connection ends.

            If both from_layer_name and to_layer_name are None, then
            all of the layers are connected sequentially in the order
            added.

        Examples:
            >>> net = Network("XOR2")
            >>> net.add(Layer("input", 2))
            >>> net.add(Layer("hidden", 5))
            >>> net.add(Layer("output", 2))
            >>> net.connect()
            >>> [layer.name for layer in net["input"].outgoing_connections]
            ['hidden']
        """
        if len(self.layers) == 0:
            raise Exception("no layers have been added")
        if from_layer_name is None and to_layer_name is None:
            if (any([layer.outgoing_connections for layer in self.layers]) or
                any([layer.incoming_connections for layer in self.layers])):
                raise Exception("layers already have connections")
            for i in range(len(self.layers) - 1):
                self.connect(self.layers[i].name, self.layers[i+1].name)
        else:
            ## FIXME: check for cycle here
            if from_layer_name == to_layer_name:
                raise Exception("self connections are not allowed")
            if from_layer_name not in self.layer_dict:
                raise Exception('unknown layer: %s' % from_layer_name)
            if to_layer_name not in self.layer_dict:
                raise Exception('unknown layer: %s' % to_layer_name)
            from_layer = self.layer_dict[from_layer_name]
            to_layer = self.layer_dict[to_layer_name]
            ## NOTE: these could be allowed, I guess:
            if to_layer in from_layer.outgoing_connections:
                raise Exception("attempting to duplicate connection: %s to %s" % (from_layer_name, to_layer_name))
            from_layer.outgoing_connections.append(to_layer)
            if from_layer in to_layer.incoming_connections:
                raise Exception("attempting to duplicate connection: %s to %s" % (to_layer_name, from_layer_name))
            to_layer.incoming_connections.append(from_layer)
            input_layers = [layer for layer in self.layers if layer.kind() == "input"]
            self.num_input_layers = len(input_layers)
            target_layers = [layer for layer in self.layers if layer.kind() == "output"]
            self.num_target_layers = len(target_layers)

    def summary(self):
        """
        Print out a summary of the network.
        """
        print("Network Summary")
        print("---------------")
        print("Network name:", self.name)
        for layer in self.layers:
            layer.summary()

    def reset(self):
        """
        Reset all of the weights/biases in a network.
        The magnitude is based on the size of the network.
        """
        self.epoch_count = 0
        self.acc_history = []
        self.loss_history = []
        self.val_percent_history = []
        if self.model:
            # Compile the whole model again:
            self.compile(**self.compile_options)

    def test(self, batch_size=32, tolerance=0.1, force=False):
        """
        """
        if self.dataset._split == len(self.dataset.inputs):
            inputs = self.dataset._train_inputs
            dataset_name = "training"
        else:
            inputs = self.dataset._test_inputs
            dataset_name = "testing"
        if self.dataset._split == len(self.dataset.targets):
            targets = self.dataset._train_targets
        else:
            targets = self.dataset._test_targets
        print("Testing on %s dataset..." % dataset_name)
        outputs = self.model.predict(inputs, batch_size=batch_size)
        ## FIXME: outputs not shaped
        in_formatted = self.pf_matrix(inputs, force)
        targ_formatted = self.pf_matrix(targets, force)
        out_formatted = self.pf_matrix(outputs, force)
        correct = self.compute_correct(outputs, targets, tolerance)
        print("# | inputs | targets | outputs | result")
        print("---------------------------------------")
        for i in range(len(out_formatted)):
            print(i, "|", in_formatted[i], "|", targ_formatted[i], "|", out_formatted[i], "|", "correct" if correct[i] else "X")
        print("Total count:", len(correct))
        print("Total percentage correct:", list(correct).count(True)/len(correct))

    def compute_correct(self, outputs, targets, tolerance):
        """
        Both are np.arrays. Return [True, ...].
        """
        if isinstance(outputs, list): ## multiple output banks
            correct = []
            for r in range(len(outputs[0])):
                row = []
                for c in range(len(outputs)):
                    row.extend(list(map(lambda v: v <= tolerance, np.abs(outputs[c][r] - targets[c][r]))))
                correct.append(all(row))
            return correct
        else:
            outs = outputs.flatten()
            tars = targets.flatten()
            correct = list(map(lambda v: v <= tolerance, np.abs(outs - tars)))
        return correct

    def train_one(self, inputs, targets, batch_size=32):
        """
        Train on one input/target pair. Requires internal format.

        Examples:

            >>> from conx import Network, Layer, SGD, Dataset
            >>> net = Network("XOR", 2, 2, 1, activation="sigmoid")
            >>> net.compile(error='mean_squared_error',
            ...             optimizer=SGD(lr=0.3, momentum=0.9))
            >>> ds = [[[0, 0], [0]],
            ...       [[0, 1], [1]],
            ...       [[1, 0], [1]],
            ...       [[1, 1], [0]]]
            >>> net.dataset.load(ds)
            >>> out, err = net.train_one({"input": [0, 0]},
            ...                          {"output": [0]})
            >>> len(out)
            1
            >>> len(err)
            1

            >>> from conx import Network, Layer, SGD, Dataset
            >>> net = Network("XOR2")
            >>> net.add(Layer("input1", shape=1))
            >>> net.add(Layer("input2", shape=1))
            >>> net.add(Layer("hidden1", shape=2, activation="sigmoid"))
            >>> net.add(Layer("hidden2", shape=2, activation="sigmoid"))
            >>> net.add(Layer("shared-hidden", shape=2, activation="sigmoid"))
            >>> net.add(Layer("output1", shape=1, activation="sigmoid"))
            >>> net.add(Layer("output2", shape=1, activation="sigmoid"))
            >>> net.connect("input1", "hidden1")
            >>> net.connect("input2", "hidden2")
            >>> net.connect("hidden1", "shared-hidden")
            >>> net.connect("hidden2", "shared-hidden")
            >>> net.connect("shared-hidden", "output1")
            >>> net.connect("shared-hidden", "output2")
            >>> net.compile(error='mean_squared_error',
            ...             optimizer=SGD(lr=0.3, momentum=0.9))
            >>> ds = [([[0],[0]], [[0],[0]]),
            ...       ([[0],[1]], [[1],[1]]),
            ...       ([[1],[0]], [[1],[1]]),
            ...       ([[1],[1]], [[0],[0]])]
            >>> net.dataset.load(ds)
            >>> net.compile(error='mean_squared_error',
            ...             optimizer=SGD(lr=0.3, momentum=0.9))
            >>> out, err = net.train_one({"input1": [0], "input2": [0]},
            ...                          {"output1": [0], "output2": [0]})
            >>> len(out)
            2
            >>> len(err)
            2
            >>> net.dataset._num_input_banks
            2
            >>> net.dataset._num_target_banks
            2
        """
        if isinstance(inputs, dict):
            inputs = [inputs[name] for name in self.input_bank_order]
            if self.num_input_layers == 1:
                inputs = inputs[0]
        if isinstance(targets, dict):
            targets = [targets[name] for name in self.output_bank_order]
            if self.num_target_layers == 1:
                targets = targets[0]
        pairs = [(inputs, targets)]
        if self.num_input_layers == 1:
            ins = np.array([x for (x, y) in pairs], "float32")
        else:
            ins = []
            for i in range(len(pairs[0][0])):
                ins.append(np.array([x[i] for (x,y) in pairs], "float32"))
        if self.num_target_layers == 1:
            targs = np.array([y for (x, y) in pairs], "float32")
        else:
            targs = []
            for i in range(len(pairs[0][1])):
                targs.append(np.array([y[i] for (x,y) in pairs], "float32"))
        history = self.model.fit(ins, targs, epochs=1, verbose=0, batch_size=batch_size)
        ## may need to update history?
        outputs = self.propagate(inputs, batch_size=batch_size, visualize=False)
        errors = (np.array(targets) - np.array(outputs)).tolist() # FIXME: multi outputs?
        if self.visualize and get_ipython():
            if self.config["show_targets"]:
                self.display_component([targets], "targets") # FIXME: use output layers' minmax
            if self.config["show_errors"]:
                self.display_component([errors], "errors", minmax=(-1, 1), colormap="RdGy")
        return (outputs, errors)

    def retrain(self, **overrides):
        """
        Call network.train() again with same options as last call, unless overrides.
        """
        self.train_options.update(overrides)
        self.train(**self.train_options)

    def train(self, epochs=1, accuracy=None, batch_size=None,
              report_rate=1, tolerance=0.1, verbose=1, shuffle=True,
              class_weight=None, sample_weight=None):
        """
        Train the network.
        """
        ## IDEA: train_options could be a history of dicts
        ## to keep track of a schedule of learning over time
        self.train_options = {
            "epochs": epochs,
            "accuracy": accuracy,
            "batch_size": batch_size,
            "report_rate": report_rate,
            "tolerance": tolerance,
            "verbose": verbose,
            "shuffle": shuffle,
            "class_weight": class_weight,
            "sample_weight": sample_weight,
            }
        if batch_size is None:
            batch_size = len(self.dataset.train_inputs)
        if not (isinstance(batch_size, numbers.Integral) or batch_size is None):
            raise Exception("bad batch size: %s" % (batch_size,))
        if accuracy is None and epochs > 1 and report_rate > 1:
            print("Warning: report_rate is ignored when in epoch mode")
        if self.dataset._split == len(self.dataset.inputs):
            validation_inputs = self.dataset._train_inputs
            validation_targets = self.dataset._train_targets
        else:
            validation_inputs = self.dataset._test_inputs
            validation_targets = self.dataset._test_targets
        if verbose: print("Training...")
        with _InterruptHandler() as handler:
            if accuracy is None: # train them all using fit
                result = self.model.fit(self.dataset._train_inputs,
                                        self.dataset._train_targets,
                                        batch_size=batch_size,
                                        epochs=epochs,
                                        verbose=verbose,
                                        shuffle=shuffle,
                                        class_weight=class_weight,
                                        sample_weight=sample_weight)
                outputs = self.model.predict(validation_inputs, batch_size=batch_size)
                ## FIXME: outputs not shaped
                correct_list = self.compute_correct(outputs, validation_targets, tolerance)
                correct = correct_list.count(True)
                self.epoch_count += epochs
                acc = 0
                # In multi-outputs, acc is given by output layer name + "_acc"
                for key in result.history:
                    if key.endswith("acc"):
                        acc += result.history[key][0]
                #acc = result.history['acc'][0]
                self.acc_history.append(acc)
                loss = result.history['loss'][0]
                self.loss_history.append(loss)
                val_percent = correct/len(validation_targets)
                self.val_percent_history.append(val_percent)
            else:
                for e in range(1, epochs+1):
                    result = self.model.fit(self.dataset._train_inputs, self.dataset._train_targets,
                                            batch_size=batch_size,
                                            epochs=1,
                                            verbose=0,
                                            shuffle=shuffle,
                                            class_weight=class_weight,
                                            sample_weight=sample_weight)
                    outputs = self.model.predict(validation_inputs, batch_size=batch_size)
                    ## FIXME: outputs not shaped
                    if self.num_target_layers == 1:
                        correct = [all(x) for x in map(lambda v: v <= tolerance,
                                                       np.abs(outputs - validation_targets))].count(True)
                    else:
                        correct = [all(x) for x in map(lambda v: v <= tolerance,
                                                       np.abs(np.array(outputs) - np.array(validation_targets)))].count(True)
                    self.epoch_count += 1
                    acc = 0
                    # In multi-outputs, acc is given by output layer name + "_acc"
                    for key in result.history:
                        if key.endswith("acc"):
                            acc += result.history[key][0]
                    #acc = result.history['acc'][0]
                    self.acc_history.append(acc)
                    loss = result.history['loss'][0]
                    self.loss_history.append(loss)
                    val_percent = correct/len(validation_targets)
                    self.val_percent_history.append(val_percent)
                    if self.epoch_count % report_rate == 0:
                        if verbose: print("Epoch #%5d | train error %7.5f | train accuracy %7.5f | validate%% %7.5f" %
                                          (self.epoch_count, loss, acc, val_percent))
                    if val_percent >= accuracy or handler.interrupted:
                        break
            if handler.interrupted:
                print("=" * 72)
                print("Epoch #%5d | train error %7.5f | train accuracy %7.5f | validate%% %7.5f" %
                      (self.epoch_count, loss, acc, val_percent))
                raise KeyboardInterrupt
        if verbose:
            print("=" * 72)
            print("Epoch #%5d | train error %7.5f | train accuracy %7.5f | validate%% %7.5f" %
                  (self.epoch_count, loss, acc, val_percent))
        else:
            return (self.epoch_count, loss, acc, val_percent)

        # # evaluate the model
        # print('Evaluating performance...')
        # loss, accuracy = self.model.evaluate(self.test_inputs, self.test_targets, verbose=0)
        # print('Test loss:', loss)
        # print('Test accuracy:', accuracy)
        # #print('Most recent weights saved in model.weights')
        # #self.model.save_weights('model.weights')

    def get_weights(self, layer_name):
        """
        Get the weights from the model in an easy to read format.
        """
        weights = [layer.get_weights() for layer in self.model.layers
                   if layer_name == layer.name][0]
        return [m.tolist() for m in weights]

    def propagate(self, input, batch_size=32, visualize=None):
        """
        Propagate an input (in human API) through the network.
        If visualizing, the network image will be updated.
        """
        import keras.backend as K
        visualize = visualize if visualize is not None else self.visualize
        if isinstance(input, dict):
            input = [input[name] for name in self.input_bank_order]
            if self.num_input_layers == 1:
                input = input[0]
        elif isinstance(input, PIL.Image.Image):
            input = image2array(input)
        if self.num_input_layers == 1:
            outputs = self.model.predict(np.array([input]), batch_size=batch_size)
        else:
            inputs = [np.array([x], "float32") for x in input]
            outputs = self.model.predict(inputs, batch_size=batch_size)
        ## Shape the outputs:
        if self.num_target_layers == 1:
            shape = self[self.output_bank_order[0]].shape
            outputs = outputs[0].reshape(shape).tolist()
        else:
            shapes = [self[layer_name].shape for layer_name in self.output_bank_order]
            outputs = [outputs[i].reshape(shapes[i]).tolist() for i in range(len(self.output_bank_order))]
        if visualize and get_ipython():
            if not self._comm:
                from ipykernel.comm import Comm
                self._comm = Comm(target_name='conx_svg_control')
            if self._comm.kernel:
                for layer in self.layers:
                    image = self.propagate_to_image(layer.name, input, batch_size, visualize=False)
                    data_uri = self._image_to_uri(image)
                    self._comm.send({'class': "%s_%s" % (self.name, layer.name), "href": data_uri})
        return outputs

    def propagate_from(self, layer_name, input, output_layer_names=None, batch_size=32, visualize=None):
        """
        Propagate activations from the given layer name to the output layers.
        """
        visualize = visualize if visualize is not None else self.visualize
        if layer_name not in self.layer_dict:
            raise Exception("No such layer '%s'" % layer_name)
        if isinstance(input, dict):
            input = [input[name] for name in self.input_bank_order]
            if self.num_input_layers == 1:
                input = input[0]
        elif isinstance(input, PIL.Image.Image):
            input = image2array(input)
        if output_layer_names is None:
            if self.num_target_layers == 1:
                output_layer_names = [layer.name for layer in self.layers if layer.kind() == "output"]
            else:
                output_layer_names = self.output_bank_order
        else:
            if isinstance(output_layer_names, str):
                output_layer_names = [output_layer_names]
        outputs = []
        for output_layer_name in output_layer_names:
            prop_model = self.prop_from_dict.get((layer_name, output_layer_name), None)
            if prop_model is None:
                path = topological_sort(self, self[layer_name].outgoing_connections)
                # Make a new Input to start here:
                k = input_k = keras.layers.Input(self[layer_name].shape, name=self[layer_name].name)
                # So that we can display activations here:
                self.prop_from_dict[(layer_name, layer_name)] = keras.models.Model(inputs=input_k,
                                                                                   outputs=input_k)
                for layer in path:
                    k = self.prop_from_dict.get((layer_name, layer.name), None)
                    if k is None:
                        k = input_k
                        fs = layer.make_keras_functions()
                        for f in fs:
                            k = f(k)
                    self.prop_from_dict[(layer_name, layer.name)] = keras.models.Model(inputs=input_k,
                                                                                       outputs=k)
                # Now we should be able to get the prop_from model:
                prop_model = self.prop_from_dict.get((layer_name, output_layer_name), None)
            inputs = np.array([input])
            outputs.append([list(x) for x in prop_model.predict(inputs)][0])
            ## FIXME: outputs not shaped
        if visualize and get_ipython():
            if not self._comm:
                from ipykernel.comm import Comm
                self._comm = Comm(target_name='conx_svg_control')
            ## Update from start to rest of graph
            if self._comm.kernel:
                for layer in topological_sort(self, [self[layer_name]]):
                    model = self.prop_from_dict[(layer_name, layer.name)]
                    vector = model.predict(inputs)[0]
                    ## FIXME: outputs not shaped
                    image = layer.make_image(vector, self.config)
                    data_uri = self._image_to_uri(image)
                    self._comm.send({'class': "%s_%s" % (self.name, layer.name), "href": data_uri})
        if len(output_layer_names) == 1:
            return outputs[0]
        else:
            return outputs

    def display_component(self, vector, component, **opts): #minmax=None, colormap=None):
        """
        vector is a list, one each per output layer. component is "errors" or "targets"
        """
        config = copy.copy(self.config)
        config.update(opts)
        ## FIXME: this doesn't work on multi-targets/outputs
        output_names = self.output_bank_order
        if self._comm.kernel:
            for (target, layer_name) in zip(vector, output_names):
                array = np.array(target)
                image = self[layer_name].make_image(array, config) # minmax=minmax, colormap=colormap)
                data_uri = self._image_to_uri(image)
                self._comm.send({'class': "%s_%s_%s" % (self.name, layer_name, component), "href": data_uri})

    def propagate_to(self, layer_name, inputs, batch_size=32, visualize=None):
        """
        Computes activation at a layer. Side-effect: updates visualized SVG.
        """
        visualize = visualize if visualize is not None else self.visualize
        if layer_name not in self.layer_dict:
            raise Exception('unknown layer: %s' % (layer_name,))
        if isinstance(inputs, dict):
            inputs = [inputs[name] for name in self.input_bank_order]
            if self.num_input_layers == 1:
                inputs = inputs[0]
        elif isinstance(inputs, PIL.Image.Image):
            inputs = image2array(inputs)
        if self.num_input_layers == 1:
            outputs = self[layer_name].model.predict(np.array([inputs]), batch_size=batch_size)
        else:
            # get just inputs for this layer, in order:
            vector = [np.array([inputs[self.input_bank_order.index(name)]]) for name in
                      self._get_sorted_input_names(self[layer_name].input_names)]
            outputs = self[layer_name].model.predict(vector, batch_size=batch_size)
        ## output shaped below:
        if visualize and get_ipython():
            if not self._comm:
                from ipykernel.comm import Comm
                self._comm = Comm(target_name='conx_svg_control')
            # Update path from input to output
            if self._comm.kernel:
                for layer in self.layers: # FIXME??: update all layers for now
                    out = self.propagate_to(layer.name, inputs, visualize=False)
                    image = self[layer.name].make_image(np.array(out), self.config) # single vector, as an np.array
                    data_uri = self._image_to_uri(image)
                    self._comm.send({'class': "%s_%s" % (self.name, layer.name), "href": data_uri})
        ## Shape the outputs:
        shape = self[layer_name].shape
        outputs = outputs[0].reshape(shape).tolist()
        return outputs

    def propagate_to_features(self, layer_name, inputs, cols=5, scale=1.0):
        from IPython.display import HTML
        if isinstance(inputs, dict):
            inputs = [inputs[name] for name in self.input_bank_order]
            if self.num_input_layers == 1:
                inputs = inputs[0]
        elif isinstance(inputs, PIL.Image.Image):
            inputs = image2array(inputs)
        output_shape = self[layer_name].keras_layer.output_shape
        retval = """<table><tr>"""
        if (isinstance(output_shape, tuple) and len(output_shape) == 4):
            for i in range(output_shape[3]):
                self[layer_name].feature = i
                image = self.propagate_to_image(layer_name, inputs, visualize=False)
                if scale != 1.0:
                    image = image.resize((int(image.size[0] * scale), int(image.size[1] * scale)))
                data_uri = self._image_to_uri(image)
                retval += """<td><img src="%s"/><br/><center>Feature %s</center></td>""" % (data_uri, i)
                if (i + 1) % cols == 0:
                    retval += """</tr><tr>"""
            retval += "</tr></table>"
            return HTML(retval)

    def propagate_to_image(self, layer_name, input, batch_size=32, scale=1.0, visualize=None):
        """
        Gets an image of activations at a layer.
        """
        if isinstance(input, dict):
            input = [input[name] for name in self.input_bank_order]
            if self.num_input_layers == 1:
                input = input[0]
        elif isinstance(input, PIL.Image.Image):
            input = image2array(input)
        outputs = self.propagate_to(layer_name, input, batch_size, visualize=visualize)
        array = np.array(outputs)
        image = self[layer_name].make_image(array, self.config)
        if scale != 1.0:
            image = image.resize((int(image.size[0] * scale), int(image.size[1] * scale)))
        return image

    def propagate_to_plot(self, output_layer, output_index,
                          input_layer, input_index1, input_index2,
                          colormap="RdGy", default_input_value=0.0,
                          resolution=0.1):
        ## FIXME: work on multi-input banks
        from .graphs import plot_activations
        return plot_activations(self, output_layer, output_index,
                                input_layer, input_index1, input_index2,
                                colormap, default_input_value, resolution)

    def plot(self, *whats):
        """
        whats - "error", "accuracy", and/or "test"
        symbols are matplotlib markers or colors:

        https://matplotlib.org/api/markers_api.html
        https://matplotlib.org/api/colors_api.html
        """
        from .graphs import plot
        symbols = {"error": "r", # red
                   "accuracy": "g", # green
                   "test": "m"} # magenta
        lines = []
        for i in range(len(whats)):
            what = whats[i]
            symbol = symbols[what]
            if what == "error":
                lines.append(["Error", symbol, self.loss_history])
            elif what == "accuracy":
                lines.append(["Accuracy", symbol, self.acc_history])
            elif what == "test":
                lines.append(["Test %", symbol, self.val_percent_history])
        return plot(lines, ylabel="value", xlabel="epoch")

    def compile(self, **kwargs):
        """
        Check and compile the network.

        See https://keras.io/ `Model.compile()` method for more details.
        """
        ## Error checking:
        if len(self.layers) == 0:
            raise Exception("network has no layers")
        for layer in self.layers:
            if layer.kind() == 'unconnected':
                raise Exception("'%s' layer is unconnected" % layer.name)
        if "error" in kwargs: # synonym
            kwargs["loss"] = kwargs["error"]
            del kwargs["error"]
        if "optimizer" in kwargs:
            optimizer = kwargs["optimizer"]
            if (not ((isinstance(optimizer, str) and optimizer in self.OPTIMIZERS) or
                     (isinstance(optimizer, object) and issubclass(optimizer.__class__, keras.optimizers.Optimizer)))):
                raise Exception("invalid optimizer '%s'; use valid function or one of %s" %
                                (optimizer, Network.OPTIMIZERS,))
        input_layers = [layer for layer in self.layers if layer.kind() == "input"]
        self.input_bank_order = [layer.name for layer in input_layers]
        output_layers = [layer for layer in self.layers if layer.kind() == "output"]
        self.output_bank_order = [layer.name for layer in output_layers]
        ## FIXME: redo checks to separate dataset:
        # if len(input_layers) == 1 and len(self.input_layer_order) == 0:
        #     pass # ok!
        # elif len(input_layers) == len(self.dataset._input_layer_order):
        #     # check to make names all match
        #     for layer in input_layers:
        #         if layer.name not in self.dataset._input_layer_order:
        #             raise Exception("layer '%s' is not listed in dataset._input_layer_order" % layer.name)
        # else:
        #     raise Exception("improper dataset._input_layer_order names")
        ## FIXME: add new dataset-based checks:
        # if len(output_layers) == 1 and len(self.output_layer_order) == 0:
        #     pass # ok!
        # elif len(output_layers) == len(self.output_layer_order):
        #     # check to make names all match
        #     for layer in output_layers:
        #         if layer.name not in self.output_layer_order:
        #             raise Exception("layer '%s' is not listed in set_output_layer_order()" % layer.name)
        # else:
        #     raise Exception("improper set_output_layer_order() names")
        self._build_intermediary_models()
        output_k_layers = self._get_output_ks_in_order()
        input_k_layers = self._get_input_ks_in_order(self.input_bank_order)
        self.model = keras.models.Model(inputs=input_k_layers, outputs=output_k_layers)
        kwargs['metrics'] = ['accuracy']
        self.compile_options = copy.copy(kwargs)
        self.model.compile(**kwargs)
        # set each conx layer to point to corresponding keras model layer
        for layer in self.layers:
            layer.keras_layer = self._find_keras_layer(layer.name)
        self.dataset.set_bank_counts()

    def _find_keras_layer(self, layer_name):
        """
        Find the associated keras layer.
        """
        return [x for x in self.model.layers if x.name == layer_name][0]

    def _delete_intermediary_models(self):
        """
        Remove these, as they don't pickle.
        """
        for layer in self.layers:
            layer.k = None
            layer.input_names = []
            layer.model = None

    def _build_intermediary_models(self):
        """
        Construct the layer.k, layer.input_names, and layer.model's.
        """
        sequence = topological_sort(self, self.layers)
        if self.debug: print("topological sort:", [l.name for l in sequence])
        for layer in sequence:
            if layer.kind() == 'input':
                if self.debug: print("making input layer for", layer.name)
                layer.k = layer.make_input_layer_k()
                layer.input_names = [layer.name]
                layer.model = keras.models.Model(inputs=layer.k, outputs=layer.k) # identity
            else:
                if self.debug: print("making layer for", layer.name)
                if len(layer.incoming_connections) == 0:
                    raise Exception("non-input layer '%s' with no incoming connections" % layer.name)
                kfuncs = layer.make_keras_functions()
                if len(layer.incoming_connections) == 1:
                    if self.debug: print("single input", layer.incoming_connections[0])
                    k = layer.incoming_connections[0].k
                    layer.input_names = layer.incoming_connections[0].input_names
                else: # multiple inputs, need to merge
                    if self.debug: print("Merge detected!", [l.name for l in layer.incoming_connections])
                    k = keras.layers.Concatenate()([incoming.k for incoming in layer.incoming_connections])
                    # flatten:
                    layer.input_names = [item for sublist in
                                         [incoming.input_names for incoming in layer.incoming_connections]
                                         for item in sublist]
                if self.debug: print("input names for", layer.name, layer.input_names)
                if self.debug: print("applying k's", kfuncs)
                for f in kfuncs:
                    k = f(k)
                layer.k = k
                ## get the inputs to this branch, in order:
                input_ks = self._get_input_ks_in_order(layer.input_names)
                layer.model = keras.models.Model(inputs=input_ks, outputs=layer.k)

    def _get_input_ks_in_order(self, layer_names):
        """
        Get the Keras function for each of a set of layer names.
        [in3, in4] sorted by input bank ordering
        """
        sorted_layer_names = self._get_sorted_input_names(set(layer_names))
        layer_ks = [self[layer_name].k for layer_name in sorted_layer_names]
        if len(layer_ks) == 1:
            layer_ks = layer_ks[0]
        return layer_ks

    def _get_sorted_input_names(self, layer_names):
        """
        Given a set of input names, give them back in order.
        """
        return [name for (index, name) in sorted([(self.input_bank_order.index(name), name)
                                                  for name in layer_names])]

    def _get_output_ks_in_order(self):
        """
        Get the Keras function for each output layer, in order.
        """
        layer_ks = [self[layer_name].k for layer_name in self.output_bank_order]
        if len(layer_ks) == 1:
            layer_ks = layer_ks[0]
        return layer_ks

    def _image_to_uri(self, img_src):
        # Convert to binary data:
        b = io.BytesIO()
        try:
            img_src.save(b, format='gif')
        except:
            return ""
        data = b.getvalue()
        data = base64.b64encode(data)
        if not isinstance(data, str):
            data = data.decode("latin1")
        return "data:image/gif;base64,%s" % html.escape(data)

    def build_struct(self, inputs, class_id, config):
        ordering = list(reversed(self._get_level_ordering())) # list of names per level, input to output
        ### find max_width, image_dims, and row_height
        max_width = 0
        images = {}
        image_dims = {}
        row_height = []
        # Go through and build images, compute max_width:
        for level_tups in ordering: ## output to input:
            # first make all images at this level
            total_width = 0 # for this row
            max_height = 0
            for (layer_name, anchor, fname) in level_tups:
                if not self[layer_name].visible or anchor: # not need to handle anchors here
                    continue
                if inputs is not None:
                    v = inputs
                elif len(self.dataset.inputs) > 0:
                    v = self.dataset.inputs[0]
                else:
                    if self.num_input_layers > 1:
                        v = []
                        for in_name in self.input_bank_order:
                            v.append(self[in_name].make_dummy_vector())
                    else:
                        in_layer = [layer for layer in self.layers if layer.kind() == "input"][0]
                        v = in_layer.make_dummy_vector()
                image = self.propagate_to_image(layer_name, v, visualize=False)
                (width, height) = image.size
                images[layer_name] = image ## little image
                max_dim = max(width, height)
                ### Layer settings:
                if self[layer_name].image_maxdim:
                    image_maxdim = self[layer_name].image_maxdim
                else:
                    image_maxdim = config["image_maxdim"]
                if self[layer_name].image_pixels_per_unit:
                    image_pixels_per_unit = self[layer_name].image_pixels_per_unit
                else:
                    image_pixels_per_unit = config["image_pixels_per_unit"]
                ## First, try based on shape:
                pwidth, pheight = np.array(image.size) * image_pixels_per_unit
                if max(pwidth, pheight) < image_maxdim:
                    width, height = pwidth, pheight
                else:
                    width, height = (int(width/max_dim * image_maxdim),
                                     int(height/max_dim * image_maxdim))
                # make sure not too small:
                if min(width, height) < 25:
                    width, height = (image_maxdim, 25)
                image_dims[layer_name] = (width, height)
                total_width += width + config["hspace"] # space between
                max_height = max(max_height, height)
            row_height.append(max_height)
            max_width = max(max_width, total_width)
        ### Now that we know the dimensions:
        struct = []
        ## Draw the title:
        struct.append(["label_svg", {"x": max_width/2,
                                     "y": config["border_top"]/2,
                                     "label": self.name,
                                     "font_size": config["font_size"] + 3,
                                     "font_family": config["font_family"],
                                     "text_anchor": "middle",
        }])
        cheight = config["border_top"] # top border
        ## Display targets?
        if config["show_targets"]:
            # Find the spacing for row:
            for (layer_name, anchor, fname) in ordering[0]:
                if not self[layer_name].visible:
                    continue
                image = images[layer_name]
                (width, height) = image_dims[layer_name]
            spacing = max_width / (len(ordering[0]) + 1)
            # draw the row of targets:
            cwidth = 0
            for (layer_name, anchor, fname) in ordering[0]: ## no anchors in output
                image = images[layer_name]
                (width, height) = image_dims[layer_name]
                cwidth += (spacing - width/2)
                struct.append(["image_svg", {"name": layer_name + "_targets",
                                             "svg_counter": self._svg_counter,
                                             "x": cwidth,
                                             "y": cheight,
                                             "image": self._image_to_uri(image),
                                             "width": width,
                                             "height": height,
                                             "tooltip": self[layer_name].tooltip(),
                                             "rx": cwidth - 1, # based on arrow width
                                             "ry": cheight - 1,
                                             "rh": height + 2,
                                             "rw": width + 2}])
                ## show a label
                struct.append(["label_svg", {"x": cwidth + width + 5,
                                             "y": cheight + height/2 + 2,
                                             "label": "targets",
                                             "font_size": config["font_size"],
                                             "font_family": config["font_family"],
                                             "text_anchor": "start",
                }])
                cwidth += width/2
            ## Then we need to add height for output layer again, plus a little bit
            cheight += row_height[0] + 10 # max height of row, plus some
        ## Display error?
        if config["show_errors"]:
            # Find the spacing for row:
            for (layer_name, anchor, fname) in ordering[0]: # no anchors in output
                if not self[layer_name].visible:
                    continue
                image = images[layer_name]
                (width, height) = image_dims[layer_name]
            spacing = max_width / (len(ordering[0]) + 1)
            # draw the row of errors:
            cwidth = 0
            for (layer_name, anchor, fname) in ordering[0]: # no anchors in output
                image = images[layer_name]
                (width, height) = image_dims[layer_name]
                cwidth += (spacing - (width/2))
                struct.append(["image_svg", {"name": layer_name + "_errors",
                                             "svg_counter": self._svg_counter,
                                             "x": cwidth,
                                             "y": cheight,
                                             "image": self._image_to_uri(image),
                                             "width": width,
                                             "height": height,
                                             "tooltip": self[layer_name].tooltip(),
                                             "rx": cwidth - 1, # based on arrow width
                                             "ry": cheight - 1,
                                             "rh": height + 2,
                                             "rw": width + 2}])
                ## show a label
                struct.append(["label_svg", {"x": cwidth + width + 5,
                                             "y": cheight + height/2 + 2,
                                             "label": "errors",
                                             "font_size": config["font_size"],
                                             "font_family": config["font_family"],
                                             "text_anchor": "start",
                }])
                cwidth += width/2
            ## Then we need to add height for output layer again, plus a little bit
            cheight += row_height[0] + 10 # max height of row, plus some
        # Now we go through again and build SVG:
        positioning = {}
        level_num = 0
        for level_tups in ordering:
            spacing = max_width / (len(level_tups) + 1)
            cwidth = 0
            # See if there are any connections up:
            any_connections_up = False
            last_connections_up = False
            for (layer_name, anchor, fname) in level_tups:
                if not self[layer_name].visible or anchor:
                    continue
                for out in self[layer_name].outgoing_connections:
                    if out.name not in positioning:
                        continue
                    any_connections_up = True
            if any_connections_up:
                cheight += config["vspace"] # for arrows
            else: # give a bit of room:
                if not last_connections_up:
                    cheight += 5
            last_connections_up = any_connections_up
            max_height = 0 # for row of images
            for (layer_name, anchor, fname) in level_tups:
                if not self[layer_name].visible:
                    continue
                if anchor:
                    anchor_name = "%s-%s-anchor%s" % (layer_name, fname, level_num)
                    cwidth += spacing
                    positioning[anchor_name] = {"x": cwidth, "y": cheight}
                    x1 = cwidth
                    ## now we are at an anchor. Is the thing that it anchors in the
                    ## lower row? level_num is increasing
                    prev = [(oname, oanchor, lfname) for (oname, oanchor, lfname) in ordering[level_num - 1] if
                            (((layer_name == oname) and (oanchor is False)) or
                             ((layer_name == oname) and (oanchor is True) and (fname == lfname)))]
                    if prev:
                        tooltip = html.escape(self.describe_connection_to(self[fname], self[layer_name]))
                        if prev[0][1]: # anchor
                            anchor_name2 = "%s-%s-anchor%s" % (layer_name, fname, level_num - 1)
                            ## draw a line to this anchor point
                            x2 = positioning[anchor_name2]["x"]
                            y2 = positioning[anchor_name2]["y"]
                            struct.append(["line_svg", {"x1":cwidth,
                                                        "y1":cheight,
                                                        "x2":x2,
                                                        "y2":y2,
                                                        "arrow_color": config["arrow_color"] if self[fname].dropout == 0 else "red",
                                                        "tooltip": tooltip
                            }])
                        else:
                            ## draw a line to this bank
                            x2 = positioning[layer_name]["x"] + positioning[layer_name]["width"]/2
                            y2 = positioning[layer_name]["y"] + positioning[layer_name]["height"]
                            tootip ="TODO"
                            struct.append(["arrow_svg", {"x1":cwidth,
                                                         "y1":cheight,
                                                         "x2":x2,
                                                         "y2":y2,
                                                         "arrow_color": config["arrow_color"] if self[fname].dropout == 0 else "red",
                                                         "tooltip": tooltip
                            }])
                    else:
                        print("that's weird!", layer_name, "is not in", prev)
                    continue
                else:
                    image = images[layer_name]
                    (width, height) = image_dims[layer_name]
                    cwidth += (spacing - (width/2))
                    positioning[layer_name] = {"name": layer_name,
                                               "svg_counter": self._svg_counter,
                                               "x": cwidth,
                                               "y": cheight,
                                               "image": self._image_to_uri(image),
                                               "width": width,
                                               "height": height,
                                               "tooltip": self[layer_name].tooltip(),
                                               "rx": cwidth - 1, # based on arrow width
                                               "ry": cheight - 1,
                                               "rh": height + 2,
                                               "rw": width + 2}
                    x1 = cwidth + width/2
                y1 = cheight - 1
                #### Background rects for arrow mouseovers
                # for out in self[layer_name].outgoing_connections:
                #     if out.name not in positioning:
                #         continue
                #     # draw background to arrows to allow mouseover tooltips:
                #     x2 = positioning[out.name]["x"] + positioning[out.name]["width"]/2
                #     y2 = positioning[out.name]["y"] + positioning[out.name]["height"]
                #     rect_width = abs(x1 - x2)
                #     rect_extra = 0
                #     if rect_width < 20:
                #         rect_extra = 10
                #     tooltip = html.escape(self.describe_connection_to(self[layer_name], out))
                #     svg += arrow_rect.format(**{"tooltip": tooltip,
                #                                 "rx": min(x2, x1) - rect_extra,
                #                                 "ry": min(y2, y1) + 2, # bring down
                #                                 "rw": rect_width + rect_extra * 2,
                #                                 "rh": abs(y1 - y2) - 2})
                # Draw all of the connections up from here:
                for out in self[layer_name].outgoing_connections:
                    if out.name not in positioning:
                        continue
                    # draw an arrow between layers:
                    anchor_name = "%s-%s-anchor%s" % (out.name, layer_name, level_num - 1)
                    ## Don't draw this error, if there is an anchor in the next level
                    if anchor_name in positioning:
                        tooltip = html.escape(self.describe_connection_to(self[layer_name], out))
                        x2 = positioning[anchor_name]["x"]
                        y2 = positioning[anchor_name]["y"]
                        struct.append(["line_svg", {"x1":x1,
                                                    "y1":y1,
                                                    "x2":x2,
                                                    "y2":y2,
                                                    "arrow_color": config["arrow_color"] if self[layer_name].dropout == 0 else "red",
                                                    "tooltip": tooltip
                        }])
                        continue
                    else:
                        tooltip = html.escape(self.describe_connection_to(self[layer_name], out))
                        x2 = positioning[out.name]["x"] + positioning[out.name]["width"]/2
                        y2 = positioning[out.name]["y"] + positioning[out.name]["height"]
                        struct.append(["arrow_svg", {"x1":x1,
                                                     "y1":y1,
                                                     "x2":x2,
                                                     "y2":y2 + 2,
                                                     "arrow_color": config["arrow_color"] if self[layer_name].dropout == 0 else "red",
                                                     "tooltip": tooltip
                        }])
                struct.append(["image_svg", positioning[layer_name]])
                struct.append(["label_svg", {"x": positioning[layer_name]["x"] + positioning[layer_name]["width"] + 5,
                                             "y": positioning[layer_name]["y"] + positioning[layer_name]["height"]/2 + 2,
                                             "label": layer_name,
                                             "font_size": config["font_size"],
                                             "font_family": config["font_family"],
                                             "text_anchor": "start",
                }])
                output_shape = self[layer_name].keras_layer.output_shape
                if (isinstance(output_shape, tuple) and len(output_shape) == 4 and
                    "ImageLayer" != self[layer_name].__class__.__name__):
                    features = str(output_shape[3])
                    feature = str(self[layer_name].feature)
                    struct.append(["label_svg", {"x": positioning[layer_name]["x"] + positioning[layer_name]["width"] + 5,
                                                 "y": positioning[layer_name]["y"] + 5,
                                                 "label": features,
                                                 "font_size": config["font_size"],
                                                 "font_family": config["font_family"],
                                                 "text_anchor": "start",
                    }])
                    struct.append(["label_svg", {"x": positioning[layer_name]["x"] - (len(feature) * 7) - 5,
                                                 "y": positioning[layer_name]["y"] + positioning[layer_name]["height"] - 5,
                                                 "label": feature,
                                                 "font_size": config["font_size"],
                                                 "font_family": config["font_family"],
                                                 "text_anchor": "start",
                    }])
                cwidth += width/2
                max_height = max(max_height, height)
                self._svg_counter += 1
            cheight += max_height
            level_num += 1
        cheight += config["border_bottom"]
        struct.append(["svg_head", {
            "svg_height": config["svg_height"],
            "width": max_width,  # view port width
            "height": cheight,   # view port height
            "netname": self.name,
            "arrow_color": config["arrow_color"],
            "arrow_width": config["arrow_width"],
        }])
        return struct

    def _initialize_javascript(self):
        from IPython.display import Javascript, display
        js = """
require(['base/js/namespace'], function(Jupyter) {
    Jupyter.notebook.kernel.comm_manager.register_target('conx_svg_control', function(comm, msg) {
        comm.on_msg(function(msg) {
            var data = msg["content"]["data"];
            var images = document.getElementsByClassName(data["class"]);
            for (var i = 0; i < images.length; i++) {
                images[i].setAttributeNS(null, "href", data["href"]);
            }
        });
    });
});
"""
        display(Javascript(js))

    def build_svg(self, inputs=None, class_id=None, opts={}):
        """
        opts - temporary override of config

        includes:
            "font_size": 12,
            "border_top": 25,
            "border_bottom": 25,
            "hspace": 100,
            "vspace": 50,
            "image_maxdim": 200
            "image_pixels_per_unit": 50

        See .config for all options.
        """
        if any([(layer.kind() == "unconnected") for layer in self.layers]):
            raise Exception("can't build display with layers that aren't connected; use Network.connect(...)")
        if self.model is None:
            raise Exception("can't build display before Network.compile(...) as been run")
        self.visualize = False # so we don't try to update previously drawn images
        # defaults:
        config = copy.copy(self.config)
        config.update(opts)
        struct = self.build_struct(inputs, class_id, config)
        ### Define the SVG strings:
        image_svg = """<rect x="{{rx}}" y="{{ry}}" width="{{rw}}" height="{{rh}}" style="fill:none;stroke:{border_color};stroke-width:{border_width}"/><image id="{netname}_{{name}}_{{svg_counter}}" class="{netname}_{{name}}" x="{{x}}" y="{{y}}" height="{{height}}" width="{{width}}" preserveAspectRatio="none" href="{{image}}"><title>{{tooltip}}</title></image>""".format(
            **{
                "netname": class_id if class_id is not None else self.name,
                "border_color": config["border_color"],
                "border_width": config["border_width"],
            })
        line_svg = """<line x1="{{x1}}" y1="{{y1}}" x2="{{x2}}" y2="{{y2}}" stroke="{{arrow_color}}" stroke-width="{arrow_width}"><title>{{tooltip}}</title></line>""".format(**self.config)
        arrow_svg = """<line x1="{{x1}}" y1="{{y1}}" x2="{{x2}}" y2="{{y2}}" stroke="{{arrow_color}}" stroke-width="{arrow_width}" marker-end="url(#arrow)"><title>{{tooltip}}</title></line>""".format(**self.config)
        arrow_rect = """<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" style="fill:white;stroke:none"><title>{tooltip}</title></rect>"""
        label_svg = """<text x="{x}" y="{y}" font-family="{font_family}" font-size="{font_size}" text-anchor="{text_anchor}" alignment-baseline="central">{label}</text>"""
        svg_head = """<svg id='{netname}' xmlns='http://www.w3.org/2000/svg' viewBox="0 0 {width} {height}" height="{svg_height}" image-rendering="pixelated">
    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,6 L9,3 z" fill="{arrow_color}" />
        </marker>
    </defs>"""
        templates = {
            "image_svg": image_svg,
            "line_svg": line_svg,
            "arrow_svg": arrow_svg,
            "arrow_rect": arrow_rect,
            "label_svg": label_svg,
            "svg_head": svg_head,
        }
        ## get the header:
        svg = None
        for (template_name, dict) in struct:
            if template_name == "svg_head":
                svg = svg_head.format(**dict)
        ## build the rest:
        for (template_name, dict) in struct:
            if template_name != "svg_head":
                t = templates[template_name]
                svg += t.format(**dict)
        svg += """</svg>"""
        self.visualize = True
        if get_ipython():
            self._initialize_javascript()
        return svg

    def _get_level_ordering(self):
        """
        Returns a list of lists of tuples from
        input to output of levels.

        Each tuple contains: (layer_name, anchor?, from_name/None)

        If anchor is True, this is just an anchor point.
        """
        ## First, get a level for all layers:
        levels = {}
        for layer in topological_sort(self, self.layers):
            if not hasattr(layer, "model"):
                continue
            level = max([levels[lay.name] for lay in layer.incoming_connections] + [-1])
            levels[layer.name] = level + 1
        max_level = max(levels.values())
        ordering = []
        for i in range(max_level + 1): # input to output
            layer_names = [layer.name for layer in self.layers if levels[layer.name] == i]
            ordering.append([(name, False, None) for name in layer_names]) # (going_to/layer_name, anchor, coming_from)
        ## promote all output banks to last row:
        for level in range(len(ordering)): # input to output
            tuples = ordering[level]
            for (name, anchor, none) in tuples[:]: # go through copy
                if self[name].kind() == "output":
                    ## move it to last row
                    ## find it and remove
                    index = tuples.index((name, anchor, None))
                    ordering[-1].append(tuples.pop(index))
        ## insert anchor points for any in next level
        ## that doesn't go to a bank in this level
        for level in range(len(ordering)): # input to output
            tuples = ordering[level]
            for (name, anchor, fname) in tuples:
                if anchor:
                    ## is this in next? if not add it
                    next_level = [(n, hfname) for (n, anchor, hfname) in ordering[level + 1]]
                    if (name, None) not in next_level and (name, fname) not in next_level:
                        ordering[level + 1].append((name, True, fname)) # add anchor point
                    else:
                        pass ## finally!
                else:
                    ## if next level doesn't contain an outgoing
                    ## connection, add it to next level as anchor point
                    for layer in self[name].outgoing_connections:
                        next_level = [(n,fname) for (n, anchor, fname) in ordering[level + 1]]
                        if (layer.name, None) not in next_level:
                            ordering[level + 1].append((layer.name, True, name)) # add anchor point
            ## replace level with sorted level:
            def input_index(name):
                return min([self.input_bank_order.index(iname) for iname in self[name].input_names])
            lev = sorted([(input_index(fname if anchor else name), name, anchor, fname) for (name, anchor, fname) in ordering[level]])
            ordering[level] = [(name, anchor, fname) for (index, name, anchor, fname) in lev]
        return ordering

    def describe_connection_to(self, layer1, layer2):
        """
        Returns a textual description of the weights for the SVG tooltip.
        """
        retval = "Weights from %s to %s" % (layer1.name, layer2.name)
        for klayer in self.model.layers:
            if klayer.name == layer2.name:
                weights = klayer.get_weights()
                for w in range(len(klayer.weights)):
                    retval += "\n %s has shape %s" % (
                        klayer.weights[w].name, weights[w].shape)
        ## FIXME: how to show merged layer weights?
        return retval

    def save(self, foldername=None, save_all=True):
        """
        Save the network to a folder.
        """
        if foldername is None:
            foldername = "%s.conx" % self.name
        if not os.path.isdir(foldername):
            os.makedirs(foldername)
        if self.model and save_all:
            self.save_model(foldername)
            self.save_weights(foldername)
            self._delete_intermediary_models()
        self.model, tmp_model = None, self.model
        self._comm, tmp_comm = None, self._comm
        self.compile_options, tmp_co = {}, self.compile_options
        for layer in self.layers:
            layer.keras_layer = None
        try:
            with open("%s/network.pickle" % foldername, "wb") as fp:
                pickle.dump(self, fp)
        except:
            raise
        finally:
            self.model = tmp_model
            self._comm = tmp_comm
            self.compile_options = tmp_co
            if self.model and save_all:
                self._build_intermediary_models()
                for layer in self.layers:
                    layer.keras_layer = self._find_keras_layer(layer.name)

    ## classmethod or method
    def load(self=None, foldername=None):
        """
        Load the network from a folder.

        Network.load()
        network.load()
        """
        if self is None:
            if foldername is None:
                raise Exception("foldername is required")
            if isinstance(foldername, str) and os.path.isdir(foldername):
                net = Network("Temp")
                net.load_model(foldername)
                net.load_weights(foldername)
                if os.path.isfile("%s/network.pickle" % foldername):
                    with open("%s/network.pickle" % foldername, "rb") as fp:
                        net = pickle.load(fp)
                    net._build_intermediary_models()
                return net
            else:
                raise Exception("Network.load() did not find folder '%s'" % foldername)
        else:
            if foldername is None:
                foldername = "%s.conx" % self.name
            if isinstance(foldername, str) and os.path.isdir(foldername):
                self.load_model(foldername)
                self.load_weights(foldername)
            else:
                raise Exception("Network.load() did not find folder '%s'" % foldername)

    def save_weights(self, foldername=None):
        """
        Save the model weights to a folder.
        """
        if self.model:
            if foldername is None:
                foldername = "%s.conx" % self.name
            if not os.path.isdir(foldername):
                os.makedirs(foldername)
            self.model.save_weights("%s/weights.h5" % foldername)
        else:
            raise Exception("need to compile network first")

    def save_model(self, foldername=None):
        """
        Save the model to a folder.
        """
        if self.model:
            if foldername is None:
                foldername = "%s.conx" % self.name
            if not os.path.isdir(foldername):
                os.makedirs(foldername)
            self.model.save("%s/model.h5" % foldername)
        else:
            raise Exception("need to compile network first")

    def load_weights(self, foldername=None):
        """
        Load the model weights from a folder.
        """
        if self.model:
            if foldername is None:
                foldername = "%s.conx" % self.name
            if os.path.isfile("%s/model.h5" % foldername):
                self.model.load_weights("%s/weights.h5" % foldername)

    def load_model(self, foldername=None):
        """
        Load and set the model from a folder.
        """
        if foldername is None:
            foldername = "%s.conx" % self.name
        if os.path.isfile("%s/model.h5" % foldername):
            self.model = keras.models.load_model("%s/model.h5" % foldername)

    def dashboard(self, width="95%", height="550px"):
        """
        Build the dashboard for Jupyter widgets. Requires running
        in a notebook/jupyterlab.
        """
        from ipywidgets import (HTML, Button, VBox, HBox, IntSlider, Select, Text,
                                Layout, Tab, Label, FloatSlider, Checkbox, IntText,
                                Box, Accordion)

        def dataset_move(position):
            if len(self.dataset.inputs) == 0 or len(self.dataset.targets) == 0:
                return
            if control_select.value == "Train":
                length = len(self.dataset.train_inputs)
            elif control_select.value == "Test":
                length = len(self.dataset.test_inputs)
            #### Position it:
            if position == "begin":
                control_slider.value = 0
            elif position == "end":
                control_slider.value = length - 1
            elif position == "prev":
                if control_slider.value - 1 < 0:
                    control_slider.value = length - 1 # wrap around
                else:
                    control_slider.value = max(control_slider.value - 1, 0)
            elif position == "next":
                if control_slider.value + 1 > length - 1:
                    control_slider.value = 0 # wrap around
                else:
                    control_slider.value = min(control_slider.value + 1, length - 1)

        def update_control_slider(change=None):
            if len(self.dataset.inputs) == 0 or len(self.dataset.targets) == 0:
                total_text.value = "of 0"
                control_slider.disabled = True
                for child in control_buttons.children:
                    child.disabled = True
                return
            if control_select.value == "Test":
                total_text.value = "of %s" % len(self.dataset.test_inputs)
                control_slider.value = 0
                control_slider.min = 0
                control_slider.max = max(len(self.dataset.test_inputs) - 1, 0)
                if len(self.dataset.test_inputs) == 0:
                    disabled = True
                else:
                    disabled = False
            elif control_select.value == "Train":
                total_text.value = "of %s" % len(self.dataset.train_inputs)
                control_slider.value = 0
                control_slider.min = 0
                control_slider.max = max(len(self.dataset.train_inputs) - 1, 0)
                if len(self.dataset.train_inputs) == 0:
                    disabled = True
                else:
                    disabled = False
            control_slider.disabled = disabled
            for child in control_buttons.children:
                child.disabled = disabled

        def update_zoom_slider(change):
            if change["name"] == "value":
                self.config["svg_height"] = zoom_slider.value * 780
                refresh()

        def update_slider_control(change):
            if len(self.dataset.inputs) == 0 or len(self.dataset.targets) == 0:
                total_text.value = "of 0"
                return
            if change["name"] == "value":
                if control_select.value == "Train" and len(self.dataset.train_targets) > 0:
                    total_text.value = "of %s" % len(self.dataset.train_inputs)
                    output = self.propagate(self.dataset.train_inputs[control_slider.value])
                    if self.config["show_targets"]:
                        self.display_component([self.dataset.train_targets[control_slider.value]], "targets", minmax=(-1, 1))
                    if self.config["show_errors"]:
                        errors = np.array(self.dataset.train_targets[control_slider.value]) - np.array(output)
                        self.display_component([errors.tolist()], "errors", minmax=(-1, 1), colormap="RdGy")
                elif control_select.value == "Test" and len(self.dataset.test_targets) > 0:
                    total_text.value = "of %s" % len(self.dataset.test_inputs)
                    output = self.propagate(self.dataset.test_inputs[control_slider.value])
                    if self.config["show_targets"]:
                        self.display_component([self.dataset.test_targets[control_slider.value]], "targets", minmax=(-1, 1))
                    if self.config["show_errors"]:
                        errors = np.array(self.dataset.test_targets[control_slider.value]) - np.array(output)
                        self.display_component([errors.tolist()], "errors", minmax=(-1, 1), colormap="RdGy")

        def train_one(button):
            if len(self.dataset.inputs) == 0 or len(self.dataset.targets) == 0:
                return
            if control_select.value == "Train" and len(self.dataset.train_targets) > 0:
                outputs = self.train_one(self.dataset.train_inputs[control_slider.value],
                                         self.dataset.train_targets[control_slider.value])
            elif control_select.value == "Test" and len(self.dataset.test_targets) > 0:
                outputs = self.train_one(self.dataset.test_inputs[control_slider.value],
                                         self.dataset.test_targets[control_slider.value])

        def prop_one(button):
            update_slider_control({"name": "value"})

        def refresh(button=None):
            net_svg.value = """<p style="text-align:center">%s</p>""" % (self.build_svg(),)
            update_control_slider()

        ## Hack to center SVG as justify-content is broken:
        net_svg = HTML(value="""<p style="text-align:center">%s</p>""" % (self.build_svg(),), layout=Layout(
            width=width, height=height, overflow_x='auto',
            justify_content="center"))
        button_begin = Button(icon="fast-backward", layout=Layout(width='100%'))
        button_prev = Button(icon="backward", layout=Layout(width='100%'))
        button_next = Button(icon="forward", layout=Layout(width='100%'))
        button_end = Button(icon="fast-forward", layout=Layout(width='100%'))
        #button_prop = Button(description="Propagate", layout=Layout(width='100%'))
        button_train = Button(description="Train", layout=Layout(width='100%'))
        control_buttons = HBox([
            button_begin,
            button_prev,
            button_train,
            button_next,
            button_end,
               ], layout=Layout(width='100%', height="50px"))
        control_select = Select(
            options=['Test', 'Train'],
            value='Train',
            description='Dataset:',
            rows=1
               )
        refresh_button = Button(icon="refresh", layout=Layout(width="40px"))
        length = (len(self.dataset.train_inputs) - 1) if len(self.dataset.train_inputs) > 0 else 0
        control_slider = IntSlider(description="Dataset index",
                                   continuous_update=False,
                                   min=0,
                                   max=max(length, 0),
                                   value=0,
                                   layout=Layout(width='95%'))
        total_text = Label(value="of 0", layout=Layout(width="100px"))
        zoom_slider = FloatSlider(description="Zoom", continuous_update=False, min=.5, max=3,
                                  value=self.config["svg_height"]/780.0)

        ## Hook them up:
        button_begin.on_click(lambda button: dataset_move("begin"))
        button_end.on_click(lambda button: dataset_move("end"))
        button_next.on_click(lambda button: dataset_move("next"))
        button_prev.on_click(lambda button: dataset_move("prev"))
        #button_prop.on_click(prop_one)
        button_train.on_click(train_one)
        control_select.observe(update_control_slider)
        control_slider.observe(update_slider_control)
        refresh_button.on_click(refresh)
        zoom_slider.observe(update_zoom_slider)

        def set_attr(obj, attr, value):
            if value not in [{}, None]: ## value is None when shutting down
                if isinstance(value, dict):
                    value = value["value"]
                if isinstance(obj, dict):
                    obj[attr] = value
                else:
                    setattr(obj, attr, value)
                ## was crashing on Widgets.__del__, if get_ipython() no longer existed
                refresh()

        # Put them together:
        control = VBox([HBox([control_select, refresh_button], layout=Layout(height="40px")),
                        HBox([control_slider, total_text], layout=Layout(height="40px")),
                        control_buttons],
                       layout=Layout(width='95%'))

        layout = Layout()
        style = {"description_width": "initial"}
        checkbox1 = Checkbox(description="Show Targets", value=self.config["show_targets"],
                             layout=layout)
        checkbox1.observe(lambda change: set_attr(self.config, "show_targets", change["new"]))
        checkbox2 = Checkbox(description="Show Errors", value=self.config["show_errors"],
                             layout=layout)
        checkbox2.observe(lambda change: set_attr(self.config, "show_errors", change["new"]))

        hspace = IntText(value=self.config["hspace"], description="Horizontal space between banks:",
                         style=style, layout=layout)
        hspace.observe(lambda change: set_attr(self.config, "hspace", change["new"]))
        vspace = IntText(value=self.config["vspace"], description="Vertical space between layers:",
                         style=style, layout=layout)
        vspace.observe(lambda change: set_attr(self.config, "vspace", change["new"]))

        config_children = [VBox(
            [HTML(value="<p><h3>%s:</h3></p>" % self.name, layout=layout),
             zoom_slider,
             hspace,
             vspace,
             checkbox1,
             checkbox2,
            ])]

        for layer in reversed(self.layers):
            children = []
            children.append(HTML(value="<p><hr/><h3>%s bank:</h3></p>" % layer.name, layout=layout))
            checkbox = Checkbox(description="Visible", value=layer.visible, layout=layout)
            checkbox.observe(lambda change, layer=layer: set_attr(layer, "visible", change["new"]))
            children.append(checkbox)
            colormap = Text(description="Colormap:", value=layer.colormap, layout=layout)
            colormap.observe(lambda change, layer=layer: set_attr(layer, "colormap", change["new"]))
            children.append(colormap)
            output_shape = layer.keras_layer.output_shape
            if (isinstance(output_shape, tuple) and
                len(output_shape) == 4 and
                "ImageLayer" != layer.__class__.__name__):
                ## Allow feature to be selected:
                feature = IntText(value=layer.feature, description="Feature to show:", style=style)
                feature.observe(lambda change, layer=layer: set_attr(layer, "feature", change["new"]))
                children.append(feature)
            config_children.append(VBox(children))

        accordion = Accordion(children=config_children)
        accordion.set_title(0, "%s network" % self.name)
        for i in range(len(self.layers)):
            accordion.set_title(i + 1, "%s bank" % self.layers[len(self.layers) - i - 1].name)

        net_page = VBox([net_svg, control], layout=Layout(width='95%'))
        config_page = VBox([accordion], layout=Layout(width='95%', overflow_y="auto"))
        #graph_page = VBox(layout=Layout(width='100%', height=height))
        #analysis_page = VBox(layout=Layout(width='100%', height=height))
        #camera_page = VBox([Button(description="Turn on webcamera")], layout=Layout(width='100%', height=height))
        help_page = HTML("""<iframe src="https://conx.readthedocs.io" width="100%%" height="%s"></frame>""" % (height,),
                         layout=Layout(width="95%", height=height))
        net_page.on_displayed(lambda widget: update_slider_control({"name": "value"}))
        tabs = [
            ("Network", net_page),
            #("Graphs", graph_page),
            #("Analysis", analysis_page),
            #("Camera", camera_page),
            ("Configuration", config_page),
            ("Help", help_page),
        ]
        tab = Tab([t[1] for t in tabs])
        for i in range(len(tabs)):
            name, widget = tabs[i]
            tab.set_title(i, name)
        return tab

    def pp(self, *args, **opts):
        """
        Pretty-print a vector.
        """
        if isinstance(args[0], str):
            label = args[0]
            vector = args[1]
        else:
            label = ""
            vector = args[0]
        print(label + self.pf(vector[:20], **opts))

    def pf_matrix(self, matrix, force=False, **opts):
        """
        Pretty-fromat a matrix. If a list, then that implies multi-bank.
        """
        if isinstance(matrix, list): ## multiple output banks
            rows = []
            for r in range(len(matrix[0])):
                row = []
                for c in range(len(matrix)):
                    row.append(self.pf(matrix[c][r], **opts))
                    if c > 99 and not force:
                        row.append("...")
                rows.append("[" + (",".join(row)) + "]")
                if r > 99 and not force:
                    rows.append("...")
                    break
            return rows
        else:
            rows = []
            for r in range(len(matrix)):
                rows.append(self.pf(matrix[r], **opts))
                if r > 99 and not force:
                    rows.append("...")
                    break
            return rows

    def pf(self, vector, **opts):
        """
        Pretty-format a vector. Returns string.

        Parameters:
            vector (list): The first parameter.
            precision (int): Number of decimal places to show for each
                value in vector.

        Returns:
            str: Returns the vector formatted as a short string.

        Examples:
            These examples demonstrate the net.pf formatting function:

            >>> import conx
            >>> net = Network("Test")
            >>> net.pf([1.01])
            '[1.01]'

            >>> net.pf(range(10), precision=2)
            '[0,1,2,3,4,5,6,7,8,9]'

            >>> net.pf([0]*10000)
            '[0,0,0,..., 0,0,0]'
        """
        from IPython.lib.pretty import pretty
        if isinstance(vector, collections.Iterable):
            vector = list(vector)
        if isinstance(vector, (list, tuple)):
            vector = np.array(vector)
        config = copy.copy(self.config)
        config.update(opts)
        precision  = "{0:.%df}" % config["precision"]
        return np.array2string(
            vector,
            formatter={'float_kind': precision.format},
            separator=",",
            max_line_width=79).replace("\n", "")

    def to_array(self) -> list:
        """
        Get the weights of a network as a flat, one-dimensional list.

        Example:
            >>> from conx import Network
            >>> net = Network("Deep", 3, 4, 5, 2, 3, 4, 5)
            >>> net.compile(optimizer="adam", error="mse")
            >>> array = net.to_array()
            >>> len(array)
            103

        Returns:
            All of weights and biases of the network in a single, flat list.
        """
        array = []
        for layer in self.model.layers:
            for weight in layer.get_weights():
                array.extend(weight.flatten())
        return array

    def from_array(self, array: list):
        """
        Load the weights from a list.

        Arguments:
            array: a sequence (e.g., list, np.array) of numbers

        Example:
            >>> from conx import Network
            >>> net = Network("Deep", 3, 4, 5, 2, 3, 4, 5)
            >>> net.compile(optimizer="adam", error="mse")
            >>> net.from_array([0] * 103)
            >>> array = net.to_array()
            >>> len(array)
            103
        """
        position = 0
        for layer in self.model.layers:
            weights = layer.get_weights()
            new_weights = []
            for i in range(len(weights)):
                w = weights[i]
                size = reduce(operator.mul, w.shape)
                new_w = np.array(array[position:position + size]).reshape(w.shape)
                new_weights.append(new_w)
                position += size
            layer.set_weights(new_weights)

class _InterruptHandler():
    """
    Class for handling interrupts so that state is not left
    in inconsistant situation.
    """
    def __init__(self, sig=signal.SIGINT):
        self.sig = sig

    def __enter__(self):
        self.interrupted = False
        self.released = False
        self.original_handler = signal.getsignal(self.sig)

        def handler(signum, frame):
            self._release()
            if self.interrupted:
                raise KeyboardInterrupt
            print("\nStopping at end of epoch... (^C again to quit now)...")
            self.interrupted = True

        signal.signal(self.sig, handler)
        return self

    def __exit__(self, type, value, tb):
        self._release()

    def _release(self):
        if self.released:
            return False
        signal.signal(self.sig, self.original_handler)
        self.released = True
        return True
