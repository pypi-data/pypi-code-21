from contracts import ContractsMeta

from .constants import FIXED, VARIABLE, DEFINED_AT_RUNTIME
from .exceptions import BlockWriterError, ModelWriterError


class BlockConfig(object):
    def __init__(self, variable, has_default, default, desc, desc_rest, dtype,
                 where=None):
        self.variable = variable
        self.has_default = has_default
        self.default = default
        self.desc = desc
        self.desc_rest = desc_rest
        self.where = where
        self.dtype = dtype

    def __repr__(self):
        return ('BlockConfig(%r,%r,%r,%r,%r)' % 
                (self.variable, self.has_default, self.default,
                  self.desc, self.desc_rest))


class BlockInput(object):
    def __init__(self, type, name, min, max,  # @ReservedAssignment
                 desc, desc_rest, where, dtype):
        self.type = type  # FIXED, VARIABLE, DEFINED_AT_RUNTIME
        self.name = name
        self.min = min
        self.max = max
        self.desc = desc
        self.desc_rest = desc_rest
        self.where = where
        self.dtype = dtype

    # TODO: add repr


class BlockOutput(object):
    def __init__(self, type, name,  # @ReservedAssignment
                 desc, desc_rest, where, dtype):
        self.type = type  # FIXED, VARIABLE, DEFINED_AT_RUNTIME
        self.name = name
        self.desc = desc
        self.desc_rest = desc_rest
        self.where = where
        self.dtype = dtype

    def __repr__(self):
        return "BlockOutput(%s,%s)" % (self.type, self.name)


def block_alias(name):
    assert isinstance(name, str)
    BlockMeta.aliases.append(name)


def block_config(name, description=None, default='not-given', dtype=None):
    assert isinstance(name, str)
    assert description is None or isinstance(description, str)
    desc, desc_rest = split_docstring(description)
    has_default = default != 'not-given'
    if [x for x in BlockMeta.tmp_config if x.variable == name]:
        cleanup()
        msg = 'Already described config variable %r.' % name
        raise BlockWriterError(msg)
    BlockMeta.tmp_config.append(BlockConfig(name, has_default, default,
                                            desc, desc_rest, dtype=dtype, where=None))


def block_input(name, description=None, dtype=None):
    assert isinstance(name, str)
    assert description is None or isinstance(description, str)
    desc, desc_rest = split_docstring(description)
    if [x for x in BlockMeta.tmp_input if x.name == name]:
        cleanup()
        msg = 'Already described input variable "%s".' % name
        raise BlockWriterError(msg)
    if BlockMeta.tmp_input and BlockMeta.tmp_input[-1].type == VARIABLE:
        cleanup()
        msg = 'Cannot mix variable and fixed input.'
        raise BlockWriterError(msg)
    BlockMeta.tmp_input.append(BlockInput(FIXED, name, None, None,
                                          desc, desc_rest, None, dtype=None))


def block_input_is_variable(description=None,
                             min=None, max=None):  # @ReservedAssignment
    assert description is None or isinstance(description, str)
    desc, desc_rest = split_docstring(description)
    if BlockMeta.tmp_input:
        cleanup()
        msg = 'Cannot mix variable and fixed input or variable with variable.'
        raise BlockWriterError(msg)
    BlockMeta.tmp_input.append(BlockInput(VARIABLE, None, min, max,
                                          desc, desc_rest, None, dtype=None))


def block_output(name, description=None, dtype=None):
    assert isinstance(name, str)
    assert description is None or isinstance(description, str)
    desc, desc_rest = split_docstring(description)
    if [x for x in BlockMeta.tmp_output if x.name == name]:
        cleanup()
        msg = 'Already described output variable %r.' % name
        raise BlockWriterError(msg)
    if BlockMeta.tmp_output and BlockMeta.tmp_output[-1].type == VARIABLE:
        cleanup()
        msg = 'Cannot mix variable and fixed output.'
        raise BlockWriterError(msg)

    BlockMeta.tmp_output.append(BlockOutput(FIXED, name,
                                             desc, desc_rest, None, dtype=dtype))


def block_output_is_variable(description=None, suffix=None):
    assert description is None or isinstance(description, str)
    desc, desc_rest = split_docstring(description)
    if BlockMeta.tmp_output:
        cleanup()
        msg = ('Cannot mix variable and fixed output or variable with variable. '
              '(added already: %s)' % (BlockMeta.tmp_output))
        raise BlockWriterError(msg)
    bo = BlockOutput(VARIABLE, suffix, desc, desc_rest, None, dtype=None)
    BlockMeta.tmp_output.append(bo)


def block_output_is_defined_at_runtime(description=None):
    assert description is None or isinstance(description, str)
    desc, desc_rest = split_docstring(description)
    if BlockMeta.tmp_output:
        cleanup()
        raise BlockWriterError('Cannot mix variable and fixed output'
                            ' or variable with variable. (added already: %s)'
                               % (BlockMeta.tmp_output))
    BlockMeta.tmp_output.append(BlockOutput(DEFINED_AT_RUNTIME, None,
                                            desc, desc_rest, None, dtype=None))


def cleanup():
    ''' Cleans up temporary data for the meta-sugar, if the construction 
        is aborted '''
    BlockMeta.tmp_config = []
    BlockMeta.tmp_output = []
    BlockMeta.tmp_input = []
    BlockMeta.aliases = []


class BlockMeta(ContractsMeta):
    aliases = []
    tmp_config = []
    tmp_input = []
    tmp_output = []

    def __init__(cls, clsname, bases, clsdict):  # @UnusedVariable @NoSelf
        ContractsMeta.__init__(cls, clsname, bases, clsdict)
        # Do not do this for the superclasses 
        if clsname in ['Generator', 'Block']:
            return

        setattr(cls, 'defined_in', cls.__module__)

        setattr(cls, 'config', BlockMeta.tmp_config)
        setattr(cls, 'output', BlockMeta.tmp_output)
        setattr(cls, 'input', BlockMeta.tmp_input)
        BlockMeta.tmp_config = []
        BlockMeta.tmp_output = []
        BlockMeta.tmp_input = []

        has_variable_input = [x
                              for x in BlockMeta.tmp_input
                              if x.type == VARIABLE]
        has_variable_output = [x
                               for x in BlockMeta.tmp_output
                               if x.type == VARIABLE]

        if has_variable_output and not has_variable_input:
            raise ModelWriterError('Cannot have variable output without '
                                   'variable input.')

        if len(BlockMeta.aliases) > 1:
            raise ModelWriterError("We don't support multiple aliases yet. "
                                   "Tried to set  %r." % BlockMeta.aliases)

        if BlockMeta.aliases:
            name = BlockMeta.aliases[0]
        else:
            name = cls.__name__

        from .registrar import default_library
        default_library.register(name, cls)

        BlockMeta.aliases = []


class BlockMetaSugar(object):

    @staticmethod
    def alias(*arg, **kwargs):
        block_alias(*arg, **kwargs)

    @staticmethod
    def config(*arg, **kwargs):
        block_config(*arg, **kwargs)

    @staticmethod
    def input(*arg, **kwargs):  # @ReservedAssignment
        block_input(*arg, **kwargs)

    @staticmethod
    def output(*arg, **kwargs):
        block_output(*arg, **kwargs)

    @staticmethod
    def output_is_variable(*arg, **kwargs):
        block_output_is_variable(*arg, **kwargs)

    @staticmethod
    def output_is_defined_at_runtime(description=None):
        """ If this is used, then one must implement get_output_signals() """
        block_output_is_defined_at_runtime(description)

    @staticmethod
    def input_is_variable(description=None,
                          min=None, max=None):  # @ReservedAssignment
        ''' Declares that this block can accept a variable number
            of inputs. You can specify minimum and maximum number. '''
        block_input_is_variable(description, min, max)


# TODO: move this somewhere else

def trim(docstring):
    if not docstring:
        return ''
    lines = docstring.expandtabs().splitlines()

    # Determine minimum indentation (first line doesn't count):
    maxi = 10000
    indent = maxi
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))

    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < maxi:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())

    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)

    result = '\n'.join(trimmed)

    # print 'input: """%s"""' % docstring
    # print 'result: """%s"""' % result
    return result

# TODO: remove space on the right


def split_docstring(s):
    ''' Splits a docstring in a tuple (first, rest). '''
    if s is None:
        return None, None
    s = trim(s)
    all_lines = s.split('\n')
    stripped = [l.strip() for l in all_lines]
    valid_lines = [l for l in stripped if l]
    if valid_lines:
        for i in range(len(all_lines)):
            if all_lines[i]:  # found first
                # join all non-empty lines with the first
                j = i
                while j < len(all_lines) - 1 and all_lines[j].strip():
                    j += 1
                first = ' '.join(all_lines[i:(j + 1)])
                rest = '\n'.join(all_lines[j + 1:])
                return first, rest
        assert False
    else:
        return None, None

