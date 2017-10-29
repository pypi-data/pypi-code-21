import importlib
import copy
import json
import commentjson
import logging
import traceback
import utils
import cPickle as pickle
import os.path

logger = logging.getLogger(__name__)

class GraphError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
        
class GraphErrorSpecifiedSubgraph(GraphError):
    def __init__(self, message, subgraph):
        self.message = message
        self.subgraph = subgraph

    def __str__(self):
        return '{} at {}'.format(self.message, self.subgraph)
        
class GraphErrorSpecifiedDep(GraphErrorSpecifiedSubgraph):
    def __init__(self, message, subgraph, dep):
        self.message = message
        self.subgraph = subgraph
        self.dep = dep

    def __str__(self):
        return '{} at {} at {}'.format(self.message, self.subgraph, self.dep)

class Workflow():
    def __init__(self, workflow_file = None, graph = None, main = 'main', graph_args = {}, 
            create_frozens = False, use_frozens = False, use_frozen_only_if_exists = False,
            frozens_dir = './frozens/',
            frozens_id = None):
        '''
        Graph args is dict: var_name -> value
        Example:
        {
            'module': 'dcg_metric',
            'class': 'DCGMetric',
            'deps': [
                {
                    'prefix': 'model1',
                    'graph': {

                    }
                },
                {
                    'arg_name': 'data',
                    'graph': {
                        'module': 'lastfm_data',
                        'class': 'LastFMData',
                        'attrs': {
                            'short': False,
                        }
                    }
                }

            ]
        }
        '''
        self.main = main

        if use_frozen_only_if_exists and not use_frozens:
            raise GraphError('You may not specify use_frozens_only_if_exists without setting use_frozens')

        self.create_frozens = create_frozens
        self.use_frozens = use_frozens
        self.use_frozen_only_if_exists = use_frozen_only_if_exists

        self.frozens_dir = frozens_dir
        if create_frozens or use_frozens:
            if frozens_id is None:
                raise GraphError('You want to create or use frzens but have not spcified frozens_id.')
        self.frozens_id = frozens_id 


        if workflow_file is not None:
            with open(workflow_file) as f:
                graph_json = f.read()
            logger.debug('Graph json: {}'.format(graph_json))
            self.graph = commentjson.loads(graph_json)
        elif isinstance(graph, basestring):
            graph_json = graph
            logger.debug('Graph json: {}'.format(graph_json))
            self.graph = commentjson.loads(graph_json)
        else:
            self.graph = graph

        self.graph_args = self.graph.get('def_vars', {})
        self.graph_args.update(graph_args)

    def get_graph(self, name):
        return self.graph[name]

    def __fold_graph(self, graph_):
        if isinstance(graph_, basestring): # this is graph name
            logger.debug('Folding graph: {}'.format(graph_))
            return self.__fold_graph(self.get_graph(graph_))
        else:
            return graph_
        
    def __substitute_graph_args(self, attrs):
        '''
        Attr format:
         * value (3.14, "foo", true or ['1', 'b'], etc)
         * variable ("$foo"). In this case value from graph_args will be substituted.
         * special dict. Dict must contain key 'cuber' with value true. 
           The dict may specify variable (key "var") and defult value (key "default"), if variable is not set in graph_args.
        '''
        attrs_ = {}
        for key, value in attrs.iteritems():
            if isinstance(value, basestring) and value.startswith('$'):
                graph_args_key = value[1:]
                logger.debug('Substitute param: {}'.format(graph_args_key))
                if graph_args_key not in self.graph_args:
                    raise ValueError('Key {} is not specified in graph args: {}'.format(graph_args_key, self.graph_args))
                attrs_[key] = self.graph_args[graph_args_key] 
            elif isinstance(value, dict) and utils.parse_bool(value.get('cuber', 'false')):
                assert value['var'].startswith('$')
                graph_args_key = value['var'][1:]
                logger.debug('Substitute param: {}'.format(graph_args_key))
                if graph_args_key not in self.graph_args:
                    if 'default' in value:
                        attrs_[key] = value['default']
                    else:
                        raise ValueError('''Key {} is not specified in graph args and default value is not set: 
                            attr: {}, 
                            graph_args: {}'''.format(graph_args_key, value, self.graph_args))
                else:
                    attrs_[key] = self.graph_args[graph_args_key] 
            else:
                attrs_[key] = value
        return attrs_

    def run(self, disable_inmemory_cache = False, disable_file_cache = False, cleanup = False, perfomance_logging = False):
        return self.__run_graph(
            graph_ = self.main, 
            disable_inmemory_cache = disable_inmemory_cache, 
            disable_file_cache = disable_file_cache,
            cleanup = cleanup,
            perfomance_logging = perfomance_logging,
        )

    def eval_expression(self, expr):
        assert isinstance(expr, basestring)
        return eval(expr, self.graph_args)

    def __run_graph(self, graph_, disable_inmemory_cache, disable_file_cache, cleanup, perfomance_logging):
        '''
            TODO: improve excprions for incorrect graph
        '''
        logger.debug('Graph to do: {}'.format(graph_))
        graph_ = self.__fold_graph(graph_)

        graph_descriptor = graph_['name'] if 'name' in graph_ else str(graph_)
        graph_id = graph_['name'] if 'name' in graph_ else utils.universal_hash(graph_)

        for key in {'module', 'class'}:
            if key not in graph_:
                raise GraphErrorSpecifiedSubgraph('Cube description must have {} parameter.'.format(key),
                    subgraph = graph_descriptor)

        for key in graph_.keys():
            graph_possible_params = {'attrs', 'deps', 'class', 'module', 'comment', 'name', 'frozen',
                'disable_inmemory_cache', 'disable_file_cache'}
            if key not in graph_possible_params:
                raise GraphErrorSpecifiedSubgraph('Cube description has param {} that is not allowed. Check for typos. Possible values: {}' \
                    .format(key, graph_possible_params), subgraph = graph_descriptor)

        def get_frozen_path():
            frozen_path = os.path.join(self.frozens_dir, self.frozens_id, '{}.pkl'.format(graph_id))
            frozen_path_dir = os.path.join(self.frozens_dir, self.frozens_id)
            logger.info('Frozen path: {}'.format(frozen_path))
            return frozen_path, frozen_path_dir

        if utils.parse_bool(graph_.get('frozen', 'false')) and self.use_frozens and \
                 not os.path.isfile(get_frozen_path()[0]):
            if not self.use_frozen_only_if_exists:
                raise GraphErrorSpecifiedSubgraph('Frozen {} does not exists, but frozens are enabled and flag "use_frozens_only_if_exists" is not enabled.'.format(get_frozen_path()[0]), subgraph = graph_descriptor)

        if utils.parse_bool(graph_.get('frozen', 'false')) and self.use_frozens and \
                os.path.isfile(get_frozen_path()[0]):
            logger.info('Loading from frozen')
            with open(get_frozen_path()[0], 'rb') as f:
                return pickle.load(f)

        attrs = copy.deepcopy(graph_.get('attrs', {}))
        attrs = self.__substitute_graph_args(attrs)
        for i, dep_ in enumerate(graph_.get('deps', {})):
            dep = dep_ if isinstance(dep_, dict) else {'graph': dep_}
            dep_descriptor = dep['name'] if isinstance(dep, dict) and 'name' in dep else '{}-th dep (zero-based)'.format(i)

            for key in {'graph'}:
                if key not in dep:
                    raise GraphErrorSpecifiedDep('Dep description must have {} parameter.'.format(key),
                        subgraph = graph_descriptor, dep = dep_descriptor)

            for key in dep.keys():
                dep_possible_params = {'fields', 'graph', 'prefix', 'comment', 'name', 'enable_if'}
                if key not in dep_possible_params:
                    raise GraphErrorSpecifiedDep('Dep description has param {} that is not allowed. Check for typos. Possible values: {}' \
                        .format(key, dep_possible_params), subgraph = graph_descriptor, dep = dep_descriptor)

            if 'enable_if' in dep:
                if not self.eval_expression(dep['enable_if']):
                    logger.info('Skip dependecy "{}" of "{}" because if clause is false'.format(dep_descriptor, graph_descriptor))
                    continue

            res = self.__run_graph(dep['graph'], 
                    disable_inmemory_cache = disable_inmemory_cache, 
                    disable_file_cache = disable_file_cache,
                    cleanup = cleanup,
                    perfomance_logging = perfomance_logging,
                )

            if not isinstance(res, dict):
                raise GraphErrorSpecifiedDep('You may not use non-dict-result cube as a dependency. Result data ({}): {}.' \
                    .format(type(res), res), subgraph = graph_descriptor, dep = dep_descriptor)

            if 'fields' not in dep:
                for key in res:
                    attr_key = dep.get('prefix', '') + key
                    if attr_key in attrs:
                        raise GraphErrorSpecifiedDep('Argument "{}" for is not unique.' \
                            .format(attr_key), subgraph = graph_descriptor, dep = dep_descriptor)
                    attrs[attr_key] = res[key]
            else:
                for new_key, old_key_ in dep['fields'].iteritems():
                    attr_key = dep.get('prefix', '') + new_key
                    
                    pack_to_dict = None
                    if isinstance(old_key_, basestring):
                        old_key = old_key_ if old_key_ != '$' else new_key
                    elif isinstance(old_key_, dict):
                        old_key = old_key_['source_field'] if old_key_['source_field']!= '$' else new_key
                        pack_to_dict = old_key_.get('pack_to_dict', None)
                    
                    if pack_to_dict is None:
                        if attr_key in attrs:
                            raise GraphErrorSpecifiedDep('Argument "{}" for is not unique.' \
                                .format(attr_key), subgraph = graph_descriptor, dep = dep_descriptor)
                        if old_key not in res:
                            raise GraphErrorSpecifiedDep('Field "{}" is not got from dependency. Got: {}'.format(old_key, ', '.join(res.keys())),
                                subgraph = graph_descriptor, dep = dep_descriptor)
                        attrs[attr_key] = res[old_key]
                    else:
                        if pack_to_dict not in attrs:
                            attrs[pack_to_dict] = {}
                        if attr_key in attrs[pack_to_dict]:
                            raise GraphErrorSpecifiedDep('Argument "{}" for is not unique for packing dict "{}".' \
                                .format(attr_key, pack_to_dict), subgraph = graph_descriptor, dep = dep_descriptor)
                        if old_key not in res:
                            raise GraphErrorSpecifiedDep('Field "{}" is not got from dependency. Got: {}'.format(old_key, ', '.join(res.keys())),
                                subgraph = graph_descriptor, dep = dep_descriptor)
                        attrs[pack_to_dict][attr_key] = res[old_key]
                        

        module = importlib.import_module(graph_['module'])
        logger.debug('Attrs keys: {}'.format(attrs.keys()))
        try:
            cube_init = getattr(module, graph_['class'])(**attrs)
        except Exception as e:
            logging.error('Faild to init cube:\nCube: {cube}\nGraph part: {graph_part}\nAttrs: {attrs}\nError: {error}\nTraceback: {tb}' \
                .format(
                    cube = graph_['module'],
                    graph_part = str(graph_),
                    attrs = utils.dict_to_string(attrs, brackets = True),
                    error = str(e),
                    tb = traceback.format_exc(),
                )
            )
            raise

        try:
            res = cube_init.get(
                disable_inmemory_cache = disable_inmemory_cache or utils.parse_bool(graph_.get('disable_inmemory_cache', 'false')), 
                disable_file_cache = disable_file_cache or utils.parse_bool(graph_.get('disable_file_cache', 'false')),
                cleanup = cleanup,
                perfomance_logging = perfomance_logging,
            )
        except Exception as e:
            logging.error('Faild to cube.get():\nCube: {cube}\nGraph part: {graph_part}\nAttrs: {attrs}\nError: {error}\nTraceback: {tb}' \
                .format(
                    cube = graph_['module'],
                    graph_part = str(graph_),
                    attrs = utils.dict_to_string(attrs, brackets = True),
                    error = str(e),
                    tb = traceback.format_exc(),
                )
            )
            raise

        if utils.parse_bool(graph_.get('frozen', 'false')) and self.create_frozens:
            frozen_path, frozen_path_dir = get_frozen_path()
            if not os.path.isdir(frozen_path_dir):
                os.makedirs(frozen_path_dir)
            with open(frozen_path, 'wb') as f:
                pickle.dump(res, f)
            logger.info('Frozen point created')

        return res
