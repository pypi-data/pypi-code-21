import sys
import warnings

from pyparsing import lineno, col

from .block_meta import split_docstring, BlockInput, BlockOutput, BlockConfig
from .constants import FIXED
from .exceptions import SemanticError, x_not_found


class Where():
    ''' An object of this class represents a place in a file. 
    
    All parsed elements contain a reference to a :py:class:`Where` object
    so that we can output pretty error messages.
    '''
    def __init__(self, filename, string,
                 character=None, line=None, column=None):
        self.filename = filename
        self.string = string
        if character is None:
            assert line is not None and column is not None
            self.line = line
            self.col = column
            self.character = None
        else:
            assert line is None and column is None
            self.character = character
            self.line = lineno(character, string)
            self.col = col(character, string)

    def __str__(self):
        s = ''
        s += 'In file %s:\n' % self.filename
        context = 3
        lines = self.string.split('\n')
        start = max(0, self.line - context)
        pattern = 'line %2d >'
        for i in range(start, self.line):
            s += ("%s%s\n" % (pattern % (i + 1), lines[i]))

        fill = len(pattern % (i + 1))
        space = ' ' * fill + ' ' * (self.col - 1)
        s += space + '^\n'
        s += space + '|\n'
        s += space + 'here or nearby'
        return s

    def print_where(self, s=sys.stdout):
        # XXX: repeated code
        s.write('\n\n')
        prefix = '    '
        write = lambda x: s.write(prefix + x)
        write('In file %s:\n' % self.filename)
        context = 3
        lines = self.string.split('\n')
        start = max(0, self.line - context)
        pattern = 'line %2d >'
        for i in range(start, self.line):
            write("%s%s\n" % (pattern % (i + 1), lines[i]))

        fill = len(pattern % (i + 1))
        space = ' ' * fill + ' ' * (self.col - 1)
        write(space + '^\n')
        write(space + '|\n')
        write(space + 'here or nearby')


class ParsedElement:
    def __init__(self):
        self.where = None


class ParsedSignalList(ParsedElement):
    def __init__(self, signals):
        ParsedElement.__init__(self)
        self.signals = signals

    def __repr__(self):
        return 'Signals%s' % self.signals

    @staticmethod
    def from_tokens(tokens):
        return ParsedSignalList(list(tokens))


class ImportStatement(ParsedElement):
    def __init__(self, package):
        ParsedElement.__init__(self)
        self.package = package

    def __repr__(self):
        return 'import(%s)' % self.package

    @staticmethod
    def from_tokens(tokens):
        package = "".join(tokens.asList())
        return ImportStatement(package)


class ParsedSignal(ParsedElement):
    ''' Note that the convention is tricky: :: 
    
             --> [local_input] name [local_output] -->
    '''
    def __init__(self, name, block_name, local_input, local_output):
        ParsedElement.__init__(self)
        self.name = name
        self.block_name = block_name
        self.local_input = local_input
        self.local_output = local_output

    def __repr__(self):
        s = 'Signal('
        if self.local_input is not None:
            s += "[%s]" % self.local_input
        if self.block_name is not None:
            s += "%s." % self.block_name
        s += str(self.name)
        if self.local_output is not None:
            s += "[%s]" % self.local_output
        s += ')'
        return s

    @staticmethod
    def from_tokens(tokens):
        name = tokens.get('name')
        block_name = tokens.get('block_name', None)
        local_input = tokens.get('local_input', None)
        local_output = tokens.get('local_output', None)
        return ParsedSignal(name, block_name, local_input, local_output)


class ParsedBlock(ParsedElement):
    def __init__(self, name, operation, config):
        ParsedElement.__init__(self)
        if operation in ['input', 'output']:
            if not isinstance(config.get("name"), str):
                raise ValueError("Invalid port name %r." % name)
        self.name = name
        self.operation = operation
        self.config = config

    def __repr__(self):
        return ('Block(op=%s,name=%s,config=%s)' %
                (self.operation, self.name, self.config))

    @staticmethod
    def from_tokens(tokens):
        blocktype = tokens['blocktype']
        config = tokens.get('config', {})
        name = tokens.get('name', None)
        return ParsedBlock(name, blocktype, config)

def parse_input_port(tokens):
    blocktype = 'input'
    port_name = tokens.get("port_name")
    assert isinstance(port_name, str)
    config = dict(name=port_name)
    name = None
    return ParsedBlock(name, blocktype, config)

def parse_output_port(tokens):
    blocktype = 'output'
    port_name = tokens.get("port_name")
    config = dict(name=port_name)
    name = None
    return ParsedBlock(name, blocktype, config)


class ParsedAssignment(ParsedElement):
    def __init__(self, key, value):
        ParsedElement.__init__(self)

        self.key = key
        self.value = value

    def __repr__(self):
        return 'Assignment(%s=%s)' % (self.key, self.value)

    @staticmethod
    def from_tokens(tokens):
        return ParsedAssignment(tokens['key'], tokens['value'])


def config_from_tokens(tokens):
    variable = tokens.get('variable')
    has_default = 'default' in tokens
    default = tokens.get('default', None)
    docstring = tokens.get('docstring', None)
    desc, desc_rest = split_docstring(docstring)
    # TODO: dtype for BlockConfig
    return BlockConfig(variable, has_default, default, desc, desc_rest, where=None, dtype=None)


def output_from_tokens(tokens):
    name = tokens.get('name')
    docstring = tokens.get('docstring', None)

    desc, desc_rest = split_docstring(docstring)

    return BlockOutput(FIXED, name, desc, desc_rest, None, dtype=None)


def input_from_tokens(tokens):
    name = tokens.get('name')
    docstring = tokens.get('docstring', None)

    desc, desc_rest = split_docstring(docstring)
    return BlockInput(FIXED, name, None, None, desc, desc_rest, None, dtype=None)


class Connection(ParsedElement):
    def __init__(self, elements):
        ParsedElement.__init__(self)
        self.elements = elements

    def __repr__(self):
        return 'Connection(%s)' % self.elements

    @staticmethod
    def from_tokens(tokens):
        return Connection(tokens)


class VariableReference(ParsedElement):
    def __init__(self, variable):
        ParsedElement.__init__(self)
        self.variable = variable

    def __repr__(self):
        return "ref:%s" % self.variable

    @staticmethod
    def from_tokens(tokens):
        return VariableReference(tokens['variable'])


class ParsedModel(ParsedElement):
    # temporary storage while parsing
    static_filename = 'not set'

    def __init__(self, name, docstring, elements):
        ParsedElement.__init__(self)
        assert name is None or isinstance(name, str)
        assert docstring is None or isinstance(docstring, str)
        self.name = name
        self.docstring = docstring

        select = lambda T: [x for x in elements if isinstance(x, T)]

        self.connections = select(Connection)
        self.config = select(BlockConfig)
        self.output = select(BlockOutput)
        self.input = select(BlockInput)
        self.imports = select(ImportStatement)
        self.assignments = select(ParsedAssignment)

        self.elements = elements

        # look for other input/output models
        def look_for_blocks(condition):
            for connection in self.connections:
                for element in connection.elements:
                    if condition(element):
                        yield element

        input_blocks = list(look_for_blocks(
            lambda x: isinstance(x, ParsedBlock) and x.operation == 'input'))
        output_blocks = list(look_for_blocks(
            lambda x: isinstance(x, ParsedBlock) and x.operation == 'output'))

        # print input_blocks
        # print output_blocks

        for block in input_blocks:
            inputs_defined = [x.name for x in self.input]
            input_name = block.config.get('name', None)
            if input_name is not None:
                # if a name is specified, check if some input
                # were specified formally
                # if some inputs were specified, it should be there
                # (we don't mix the two cases)
                if inputs_defined:
                    if not input_name in inputs_defined:
                        msg = x_not_found('input', input_name, inputs_defined)
                        raise SemanticError(msg, block)
                    else:
                        # good! this was already specified
                        pass
                else:
                    # we have a name, and no input was specified,
                    # so we add it (with warning)
                    bi = BlockInput(type=FIXED, name=input_name,
                                min=None, max=None,
                                desc=None, desc_rest=None, where=block.where,
                                dtype=None)
                    # TODO: dtype for BlockInput
                    self.input.append(bi)
            else:
                # we don't have a name

                # if no input was defined then add it
                if not inputs_defined:
                    block.config['name'] = "in%d" % len(self.input)
                    bi = BlockInput(type=FIXED, name=block.config['name'],
                                min=None, max=None,
                                desc=None, desc_rest=None, where=block.where,
                                dtype=None)
                    warnings.warn('check dtype')
                    # TODO add warning
                    self.input.append(bi)
                else:
                    # if exactly 1 input is specified, use that
                    if len(inputs_defined) == 1:
                        block.config['name'] = self.input[0].name
                    else:
                        # otherwise fail
                        msg = ('This input block did not specify a name, and '
                               'I do not know which input it refers to.')
                        raise SemanticError(msg, block)

        for block in output_blocks:
            outputs_defined = [x.name for x in self.output]
            output_name = block.config.get('name', None)
            if output_name is not None:
                # if a name is specified, check if some output
                # were specified formally
                # if some outputs were specified, it should be there
                if outputs_defined:
                    if not output_name in outputs_defined:
                        msg = x_not_found('output', output_name,
                                          outputs_defined)
                        raise SemanticError(msg, block)
                    else:
                        # good! this was already specified
                        pass
                else:
                    # we have a name, and no output was specified,
                    # so we add it (with warning)
                    bo = BlockOutput(type=FIXED, name=output_name,
                                desc=None, desc_rest=None, where=block.where, dtype=None)
                    # TODO add warning
                    self.output.append(bo)
            else:
                # we don't have a name

                # if no output was defined then add it
                if not outputs_defined:
                    block.config['name'] = "out%d" % len(self.output)
                    bo = BlockOutput(type=FIXED, name=block.config['name'],
                                desc=None, desc_rest=None, where=block.where, dtype=None)
                    self.output.append(bo)
                else:
                    # if exactly 1 output is specified, use that
                    if len(outputs_defined) == 1:
                        block.config['name'] = self.output[0].name
                    else:
                        # otherwise fail
                        msg = ('This output block did not specify a name, and '
                               'I do not know which output it refers to.')
                        raise SemanticError(msg, block)

    def __repr__(self):
        s = 'Model %r: %d elements\n' % (self.name, len(self.elements))

        parts = [
            ('config parameters', self.config),

            ('input signals', self.input),
            ('output signals', self.output),
            ('import statements', self.imports),
            ('assignments', self.assignments),
            ('blocks connections', self.connections),
        ]

        for (part, elements) in parts:
            if len(elements) == 0:
                s += '- No %s.\n' % part
            else:
                s += '- %d %s:\n' % (len(elements), part)
                for e in elements:
                    s += '  * %r\n' % e
        return s

    @staticmethod
    def from_named_model(tokens):
        name = tokens['model_name']
        elements = list(tokens['content'])
        docstring = tokens.get('docstring', None)

        return ParsedModel(name, docstring, elements)

    @staticmethod
    def from_anonymous_model(tokens):
        elements = list(tokens)
        return ParsedModel(name=None, docstring=None, elements=elements)

