""" Base class definition """
import tensorflow as tf
from dxpy.collections.dicts import DXDict

# On restrict mode, tensors as allocated to CPU memory if not specified.
RESTRICT_MODE = True


class Graph:
    """
    Base class of components.
    A graph is an abstraction of computational graph.
    It supports:
        1. Load configs externally. (By name(path))
        2. Exports some interface nodes.
        3. Supports some tasks, a dict of callables.
        4. A main tensor/graph which will be return by method as_tensor()
    """
    required_configs = []

    def __init__(name):
        from dxpy.collections import TreeDict
        self.name = name
        self.c = self._load_config()
        self._refine_config()
        self.nodes = dict()
        self.tasks = dict()
        self.main = None

    def _load_config(self):
        from ..config import config
        self.c = config[name]
        for k in self.required_configs:
            self.c[k] = config[name][k]

    def _refine_config(self):
        """
        Implement this method if additional configs is required.
        """
        pass

    def reigister_node(self, tensor_or_subgraph, name=None):
        if name is None:
            name = tensor_or_subgraph.name
        self.nodes[name] = tensor_or_subgraph

    def register_task(self, name, func):
        self.tasks[name] = func

    def __getitem__(self, name):
        if name in self.nodes:
            return self.nodes[name]
        elif name in self.tasks:
            return self.tasks[name]
        else:
            return None

    def __call__(self, feed_dict=None):
        return self.run('main', feed_dict)

    def run(self, task_name, feed_dict):
        return self.tasks[name](feed_dict)

    def as_tensor(self):
        return self.main


class Net(Graph):
    """ Base class of nets.
    Net add some special tasks based on graph:        
        1. train
        2. inference
        3. evaluate
        4. save/load
    """

    def __init__(self, name):
        super(__class__, self).__init__(name)

    def __getitem__(self, name):
        """
        Inputs:
            name: str, url like string.
        Returns:
            tensor or subnet.
        """
        from dxpy.filesystem.path import Path
        name = Path(name)
        if name.abs in self.nodes:
            return self.nodes[name.abs]
        else:
            names = name.parts
            return self.nodes[names[0]]['/'.join(names[1:])]
        return None

    def _run_sub_graph(self, sub_graph_name, feed_dict=None, sub_task_name=None):
        if sub_task_name is None:
            return self[sub_graph_name](feed_dict)
        else:
            return self[sub_graph_name].run(sub_task_name, feed_dict)

    def train(self, feed_dict=None, name=None):
        return self._run_sub_graph('train', feed_dict, name)

    def inference(self, feed_dict=None, name=None):
        return self._run_sub_graph('inference', feed_dict, name)

    def evaluate(self, feed_dict=None, name=None):
        return self._run_sub_graph('evaluate', feed_dict, name)

    def save(self, feed_dict=None):
        return self._run_sub_graph('saver', feed_dict, 'save')

    def load(self, feed_dict=None):
        return self._run_sub_graph('saver', feed_dict, 'load')
