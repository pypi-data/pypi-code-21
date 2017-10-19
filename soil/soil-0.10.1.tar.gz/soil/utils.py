import os
import yaml
import logging
from time import time
from glob import glob
from random import random
from copy import deepcopy

import networkx as nx

from contextlib import contextmanager


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def load_network(network_params, dir_path=None):
    if network_params is None:
        return nx.Graph()
    path = network_params.get('path', None)
    if path:
        if dir_path and not os.path.isabs(path):
            path = os.path.join(dir_path, path)
        extension = os.path.splitext(path)[1][1:]
        kwargs = {}
        if extension == 'gexf':
            kwargs['version'] = '1.2draft'
            kwargs['node_type'] = int
        try:
            method = getattr(nx.readwrite, 'read_' + extension)
        except AttributeError:
            raise AttributeError('Unknown format')
        return method(path, **kwargs)

    net_args = network_params.copy()
    net_type = net_args.pop('generator')

    method = getattr(nx.generators, net_type)
    return method(**net_args)


def load_file(infile):
    with open(infile, 'r') as f:
        return list(yaml.load_all(f))


def load_files(*patterns):
    for pattern in patterns:
        for i in glob(pattern):
            for config in load_file(i):
                yield config, os.path.abspath(i)


def load_config(config):
    if isinstance(config, dict):
        yield config, None
    else:
        yield from load_files(config)


@contextmanager
def timer(name='task', pre="", function=logger.info, to_object=None):
    start = time()
    yield start
    end = time()
    function('{}Finished {} in {} seconds'.format(pre, name, str(end-start)))
    if to_object:
        to_object.start = start
        to_object.end = end


def agent_from_distribution(distribution, value=-1):
    """Find the agent """
    if value < 0:
        value = random()
    for d in distribution:
        threshold = d['threshold']
        if value >= threshold[0] and value < threshold[1]:
            state = {}
            if 'state' in d:
                state = deepcopy(d['state'])
            return d['agent_type'], state

    raise Exception('Distribution for value {} not found in: {}'.format(value, distribution))


def repr(v):
    if isinstance(v, bool):
        v = "true" if v else ""
        return v, bool.__name__
    return v, type(v).__name__

def convert(value, type_):
    import importlib
    try:
        # Check if it's a builtin type
        module = importlib.import_module('builtins')
        cls = getattr(module, type_)
    except AttributeError:
        # if not, separate module and class
        module, type_ = type_.rsplit(".", 1)
        module = importlib.import_module(module)
        cls = getattr(module, type_)
    return cls(value)
