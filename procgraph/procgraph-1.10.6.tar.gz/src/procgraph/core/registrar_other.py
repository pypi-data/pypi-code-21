import inspect
import types

from .block import Block
from .constants import COMPULSORY, TIMESTAMP
from .constants import NO_OUTPUT
from .docstring_parsing import parse_docstring_annotations, DocStringInfo
from .exceptions import BadConfig, BadInput
from .model_loader import add_models_to_library
from .registrar import default_library


def make_generic(name, inputs, num_outputs,
                 operation, params={}, docs=None):
    # XXX: This is not pickable
    # make a copy
    parameters = dict(params)

    if docs is None:
        docstring = operation.__doc__
    else:
        docstring = docs

    try:
        if docstring is not None:
            annotations = parse_docstring_annotations(docstring)
            docstring = annotations.docstring
        else:
            annotations = DocStringInfo(docstring)
    except Exception as e:
        # print('Malformed annotation for %r: %s' % (operation, e))
        # print docstring
        raise

    def get_param_annotation(key):
        if key in annotations.params:
            arg = annotations.params[key]
            description = arg.desc
            if description is None:
                description = ""
            if arg.type is not None:
                description += ' (%s)' % arg.type

        else:
            description = None
        return description

    class GenericOperation(Block):
        Block.alias(name)

        # filled out later
        defined_in = None

        # XXX: does it work this way?
        __doc__ = docstring  # @ReservedAssignment
        my_operation = operation

        for key, value in parameters.items():
            description = get_param_annotation(key)

            if not value in [TIMESTAMP]:
                if value == COMPULSORY:
                    Block.config(key, description=description)
                else:
                    Block.config(key, description=description, default=value)

        for input_signal in inputs:
            description = get_param_annotation(input_signal)
            Block.input(input_signal, description=description)

        for i in range(num_outputs):
            output_name = str(i)
            if i < len(annotations.returns):
                arg = annotations.returns[i]
                description = arg.desc
                if description is None:
                    description = ""
                if arg.type is not None:
                    description += ' (%s)' % arg.type
                tokens = description.split(':')
                if len(tokens) == 2:
                    output_name = tokens[0]
                    description = tokens[1]
                    # TODO: check good name
            else:
                description = None

            Block.output(output_name, description=description)

        def update(self):
            args = []
            for input_signal in inputs:
                args.append(self.get_input(input_signal))

            params = {}
            for key in parameters:
                if parameters[key] == TIMESTAMP:
                    params[key] = max(self.get_input_signals_timestamps())
                else:
                    params[key] = self.get_config(key)

            try:
                result = operation(*args, **params)
            # Functions can throw BadInput and BadConfig, but we have to fill
            # in the block reference for them.
            except (BadInput, BadConfig) as e:
                e.block = self
                raise e

            no_out = isinstance(result, str) and str == NO_OUTPUT

            if not no_out:
                if num_outputs == 1:
                    self.set_output(0, result)
                else:
                    for i in range(num_outputs):
                        self.set_output(i, result[i])

    return GenericOperation


# TODO: add num_inputs, so that we can get rid of COMPULSORY. 
def simple_block(alias=None, num_outputs=1):
    ''' Decorator for turning functions into simple blocks. '''

    # OK, this is black magic. You are not expected to understand this.
    if type(alias) is types.FunctionType:
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])
        defined_in = mod.__name__

        function = alias
        alias = None
        num_outputs = 1
        # print "Registering %s: %s (no params) " % (defined_in, function)
        register_simple_block(function, name=alias, num_outputs=num_outputs,
                              defined_in=defined_in)
        return function
    else:
        def wrap(function):
            frm = inspect.stack()[1]
            mod = inspect.getmodule(frm[0])
            defined_in = mod.__name__

            # print("Registering %s: %s (with params %s %s)" % 
            #      (defined_in, function, alias, num_outputs))
            register_simple_block(function, name=alias,
                                  num_outputs=num_outputs,
                                  defined_in=defined_in)
            return function
        return wrap


def register_simple_block(function, name=None, num_inputs=1, num_outputs=1,
                          params={}, doc=None, defined_in=None):
    # Get a module to which we can associate this block
    if defined_in is None:
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])
        defined_in = mod.__name__

    try:
        args, _, _, defaults = inspect.getargspec(function)
        # TODO: use varwk for variable signals
        num_defaults = len(defaults) if defaults else 0
        num_no_argument = len(args) - num_defaults
        args_no_argument = args[:num_no_argument]
        args_with_default = args[num_no_argument:]
        config = dict([(args_with_default[i], defaults[i])
                        for i in range(num_defaults)])
        inputs = args_no_argument
    except Exception as e:  # @UnusedVariable
        # TODO: add switch to show this
#         print("Does not work with %s: %s " % (function, e))
        config = params
        inputs = [str(i) for i in range(num_inputs)]

    assert name is None or isinstance(name, str)
    if name is None:
        name = function.__name__

    block = make_generic(name, inputs, num_outputs, function,
                         params=config, docs=doc)

    block.defined_in = defined_in

    assert isinstance(block.defined_in, str)


def register_block(block_class, name=None):
    assert name is None or isinstance(name, str)
    if name is None:
        name = block_class.__name__
    default_library.register(name, block_class)


already = set()
def register_model_spec(model_spec, defined_in=None):
    if model_spec in already:
        return
    already.add(model_spec)
    if defined_in is None:
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])
        if mod is None:
            msg = 'Could not find module name.\nfrm[0]=%r' % frm[0]
            raise ValueError(msg)
        defined_in = mod.__name__
    add_models_to_library(default_library, model_spec, defined_in=defined_in)


