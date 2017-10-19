import string
import traceback

from contracts import contract, describe_value

from procgraph.utils import indent, levenshtein_best_match


class PGException(Exception):
    pass


class BlockWriterError(PGException):
    ''' An error by who wrote the block (e.g.: did not define signals).'''
    pass


class ModelWriterError(PGException):
    ''' An error by who wrote the model, can be either Syntax or Semantic '''
    pass


class SemanticError(ModelWriterError):
    ''' A semantic error by who wrote the model spec.
       (and, as a platypus case, when wrong config is passed.'''
    def __init__(self, error, element=None):
        # http://web.archiveorange.com/archive/v/jbUwzgEaecaPQftfkITO
        Exception.__init__(self, error, element)

        self.error = error
        if element is not None:
            assert hasattr(element, 'where')
        self.element = element

    def __str__(self):
        s = self.error
        if self.element is not None:
            s += '\n' + format_where(self.element).strip()
        return s


class PGSyntaxError(ModelWriterError):
    ''' A syntactic error by who wrote the model spec.'''
    def __init__(self, error, where=None):
        # http://web.archiveorange.com/archive/v/jbUwzgEaecaPQftfkITO
        Exception.__init__(self, error, where)

        self.error = error
        self.where = where

    def __str__(self):
        s = self.error
        s += "\n\n" + add_prefix(self.where.__str__(), ' ')
        return s


class ModelInstantionError(SemanticError):
    pass


class ModelExecutionError(PGException):
    ''' 
        Runtime errors, including misuse by the user.
    
    '''
    # XXX: code is repeated above
    def __init__(self, error, element=None):
        # http://web.archiveorange.com/archive/v/jbUwzgEaecaPQftfkITO
        Exception.__init__(self, error, element)
        
        self.error = error
        if element is not None:
            assert hasattr(element, 'where')
        self.element = element


    def __str__(self):
        s = string.strip(self.error)
        if self.element is not None:
            s += format_where(self.element)
        return string.strip(s)


class BadMethodCall(ModelExecutionError):

    def __init__(self, method, block, user_exception):
        self.method = method
        self.blocks = [block]
        self.user_exception = traceback.format_exc(user_exception)
 
    def __str__(self):
        block = self.blocks[-1]
        s = ('User-thrown exception while calling %s() in block %r.' 
             % (self.method, block.name))
        for b in self.blocks[::-1]:
            s += '\n- %s %s' % (b, id(b))
        s += '\n' + indent(str(self.user_exception).strip(), '> ')
        return s



class BadInput(ModelExecutionError):
    ''' Exception thrown to communicate a problem with one
        of the inputs to the block. '''
    def __init__(self, error, block, input_signal):
        # http://web.archiveorange.com/archive/v/jbUwzgEaecaPQftfkITO
        Exception.__init__(self, error, block, input_signal)

        self.block = block
        self.error = error
        self.input_signal = input_signal
        if block is not None:
            self.bad_value = block.get_input(input_signal)
        else:
            self.bad_value = '??? (block not given)'

    def __str__(self):
        if self.block is not None:
            name = self.block.name
        else:
            name = '(unknown)'

        # TODO: add short bad_value
        s = ("Bad input %r for block %r: %s" % 
             (self.input_signal, name, self.error))
        
        if self.block is not None:
            s += '\n value: %s' % describe_value(self.bad_value)
        
        s += format_where(self.block)
        return s


class BadConfig(ModelExecutionError):
    ''' Exception thrown to communicate a problem with one
        of the configuration values passed to the block. '''

    def __init__(self, error, block, config):
        Exception.__init__(self, error, block, config)

        self.config = config
        self.error = error
        self.block = block
        self.bad_value = block.config[config]

    def __str__(self):
        if self.block is not None:
            name = self.block.name
        else:
            name = '(unknown)'

        s = ("Bad config %r = %r for block %r: %s" % 
             (self.config, self.bad_value, name, self.error))
        s += format_where(self.block)
        return s


# A couple of functions for pretty errors
def aslist(x):
    if isinstance(x, dict):
        x = list(x.keys())
    if x:
        return ", ".join(sorted(x))
    else:
        return "<empty>"


@contract(what='str', x='str', returns='str')
def x_not_found(what, x, iterable):
    ''' Shortcut for creating pretty error messages. '''
    options = list(iterable)
    if not options:
        msg = 'Could not find %s %r; no options available.' % (what, x)
        return msg
    guess, _ = levenshtein_best_match(x, options)
    
    msg = ('Could not find %s %r in %d options. (Did you mean %r?)' % 
            (what, x, len(options), guess))
    return msg


def add_prefix(s, prefix):
    result = ""
    for l in s.split('\n'):
        result += prefix + l + '\n'
    return result


def format_where(element_or_block):
    e = element_or_block
    if e is not None:
        if e.where is not None:
            return "\n\n" + add_prefix(e.where.__str__(), ' ')
        else:
            return " (no position given)"
    else:
        return " (no element/block given)"


