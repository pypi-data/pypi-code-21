import os
import fnmatch
import inspect
import cPickle as pickle

from .model_instantiation import create_from_parsing_results
from .visualization import warning, debug
from .parsing import parse_model, ParsedModel
from .exceptions import SemanticError
from .registrar import default_library, Library
from .constants import PATH_ENV_VAR
from .. import deny_pgc_cache



class ModelSpec(object):
    ''' Class used to register as a block type '''

    def __init__(self, parsed_model, defined_in):
        self.parsed_model = parsed_model

        # each generator should expose this
        self.config = self.parsed_model.config
        self.input = self.parsed_model.input
        self.output = self.parsed_model.output

        # the module to which this model is associated
        self.defined_in = defined_in
        assert defined_in is not None

    def __call__(self, name, config, library):
        parsed_model = self.parsed_model

        parent = self

        # We create a mock library that forbids that this
        # model is created again. This prevents recursion.
        class ForbidRecursion(Library):
            def __init__(self, parent, forbid):
                Library.__init__(self, parent)
                self.forbid = forbid

            def instance(self, block_type, name, config, parent_library=None):
                if block_type == self.forbid:
                    msg = 'Recursion error for model %r.' % self.forbid
                    raise SemanticError(msg, parent.parsed_model)
                else:
                    return Library.instance(self, block_type, name,
                                            config, parent_library)

            def get_generator_for_block_type(self, block_type):
                if block_type == self.forbid:
                    msg = 'Recursion error for model %r.' % self.forbid
                    raise SemanticError(msg, parent.parsed_model)
                else:
                    return Library.get_generator_for_block_type(self,
                                                                block_type)

        sandbox = ForbidRecursion(library, parsed_model.name)
        model = create_from_parsing_results(parsed_model, name, config,
                                            library=sandbox)

        return model


def pg_add_this_package_models(filename, assign_to, subdir='models'):
    ''' Add the models for this package.
        Shortcut to put into the module ``__init__.py``.
        Call with filename = __file__, assign_to= __package__.

        Example: ::

            pg_add_this_package_models(filename__file__, assign_to=__package__)

    '''

    if subdir is not None:
        dirname = os.path.join(os.path.dirname(filename), subdir)
    else:
        dirname = os.path.dirname(filename)

    pg_look_for_models(default_library,
                       additional_paths=[dirname],
                       ignore_env=True,
                       assign_to_module=assign_to)


def pg_look_for_models(library, additional_paths=None, ignore_env=False,
                       ignore_cache=False, assign_to_module=None):
    ''' Call this function at the beginning of the executions.
    It scans the disk for model definitions, and register
    them as available block types.
    Other than the paths that are passed by argument,
    it looks into the ones in the PROCGRAPH_PATH environment
    variable (colon separated list of paths), unless ignore_env is True.

    assign_to_module is a string that gives the nominal module the model
    is associated to -- this is only used for the documentation generation.

    TODO: add global cache in user directory.

    Honors global deny_pgc_cache to disable all caches.

    '''

    paths = []
    if additional_paths:
        paths.extend(additional_paths)

    if not ignore_env:
        if PATH_ENV_VAR in os.environ:
            paths.extend(os.environ[PATH_ENV_VAR].split(':'))

    if not paths:
        if False:
            # TODO: add verbose switch
            warning("No paths given and environment var %r not defined." %
                     PATH_ENV_VAR)

    # enumerate each sub directory
    all_files = set()
    for path in paths:
        if not os.path.isdir(path):
            # XXX: should I use exception?
            raise Exception('Invalid path %r to search for models. ' % path)

        for root, dirs, files in os.walk(path):  # @UnusedVariable
            for f in files:
                if fnmatch.fnmatch(f, '*.pg'):
                    all_files.add((path, os.path.join(root, f)))

    for path, f in all_files:
        split = os.path.splitext(os.path.basename(f))
        base = split[0]

        # logger.debug('Loading models from %r' % f)

        # Make sure we use an absolute filename
        f = os.path.realpath(f)

        if f in library.loaded_files:
            # Skip if already looked at it
            continue

        library.loaded_files.add(f)

        cache = os.path.splitext(f)[0] + '.pgc'

        if deny_pgc_cache:
            # global switch
            ignore_cache = True

        if (not ignore_cache and
            os.path.exists(cache) and
            os.path.getmtime(cache) > os.path.getmtime(f)):
            try:
                models = pickle.load(open(cache))
            except Exception as e:
                debug('Cannot unpickle file %r: %s' % (cache, e))
                # XXX repeated code
                # debug("Parsing %r." % os.path.relpath(f))
                model_spec = open(f).read()

                models = parse_model(model_spec, filename=f)

        else:
            # debug("Parsing %r." % os.path.relpath(f))
            model_spec = open(f).read()
            models = parse_model(model_spec, filename=f)

        try:
            # TODO: make it parallel
            with open(cache, 'w') as f:
                pickle.dump(models, f)
        except Exception as e:
            # Cannot write on the cache for whatever reason
            # debug('Cannot write cache file: %s' % e)
            try:
                if os.path.exists(cache):
                    os.unlink(cache)
            except:
                pass

        if models[0].name is None:
            models[0].name = base

        for parsed_model in models:
            if library.exists(parsed_model.name):
                if parsed_model.name in library.name2block:
                    prev = library.name2block[parsed_model.name].parsed_model.where
                else:
                    prev = '?'
                msg = ('Found model %r in file:\n %r, and already in\n %r. ' %
                       (parsed_model.name, f, prev.filename))
                raise SemanticError(msg, parsed_model)

            if assign_to_module is None:
                assign_to_module = path
            model_spec = ModelSpec(parsed_model, assign_to_module)

            library.register(parsed_model.name, model_spec)


def pg_add_parsed_model_to_library(parsed_model, library, defined_in):
    assert parsed_model.name is not None
    if library.exists(parsed_model.name):
        prev = library.name2block[parsed_model.name].parsed_model.where
        # FIXME: suppose that I have tutorials.pg
        #  and I do:
        #    pg -d . tutorials.pg
        # This will fail because it will try to read tutorials.pg twice
        msg = ('I already have registered model %r from %r. ' %
              (parsed_model.name, prev.filename))
        raise SemanticError(msg, parsed_model)

    model_spec = ModelSpec(parsed_model, defined_in)
    library.register(parsed_model.name, model_spec)


def add_models_to_library(library, string, name=None,
                          filename=None, defined_in=None):
    '''
    defined_in: module NAME (to display in documentation)
        (Compulsory!)
    '''
    if filename is None and defined_in is not None:
        filename = __import__(defined_in, fromlist=['x']).__file__

    models = parse_model(string, filename=filename)
    if models[0].name is None:
        assert name is not None
        models[0].name = name

    for model in models:
        pg_add_parsed_model_to_library(parsed_model=model,
                                       library=library,
                                       defined_in=defined_in)


def model_from_string(model_spec, name=None, config=None,
                      library=None, filename=None):
    ''' Instances a model from a specification. Optional
        attributes can be passed. Returns a Model object.

        Additional models in the spec (after the first) are automatically
        added to the library (defined_in = calling module).

    '''
    if config is None:
        config = {}
    if library is None:
        library = default_library
    assert isinstance(model_spec, str)
    assert isinstance(config, dict)
    assert name is None or isinstance(name, str)

    parsed_models = parse_model(model_spec, filename)

    assert isinstance(parsed_models, list)
    for x in parsed_models:
        assert isinstance(x, ParsedModel)

    # Get the first one
    parsed_model = parsed_models[0]

    if len(parsed_models) > 1:
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])

        for support in parsed_models[1:]:
            pg_add_parsed_model_to_library(support, library, defined_in=mod)

            # TODO: introduce the concept of submodels?
            # support.parent = parsed_model
            # parsed_model.children.append(support)

    model = create_from_parsing_results(parsed_model, name=name,
                                        config=config, library=library)

    return model
