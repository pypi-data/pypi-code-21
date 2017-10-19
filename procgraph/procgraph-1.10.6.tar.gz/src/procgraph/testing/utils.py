from ..core.block import Block
from ..core.exceptions import SemanticError, PGSyntaxError, add_prefix
from ..core.model_loader import model_from_string
from ..core.parsing import parse_model
from ..core.registrar import default_library, Library
import procgraph.components #@UnusedImport
import unittest
import traceback


# load standard components

def define_generic(nin, nout):
    class Generic(Block):
        Block.alias('generic_in%d_out%d' % (nin, nout))
        for i in range(nin):
            Block.input(str(i))
        for i in range(nout):
            Block.output(str(i))


for nin in range(0, 6):
    for nout in range(0, 6):
        define_generic(nin, nout)


class PGTestCase(unittest.TestCase):

    def check_syntax_ok(self, model_spec):
        ''' Tests that the given string can parse OK. 
            Returns parsed models. '''
        try:
            parsed = parse_model(model_spec)
            return parsed
        except Exception as e:
            traceback.print_exc()
            self.fail("Could not parse model:\n%s\nGot error: %s" %
                  (self.write_fancy(model_spec), e))

    def check_semantic_ok(self, model_spec, config={}):
        ''' Tests that the given string can parse OK and we can create a model.
             Note that a syntax error is translated into a test Error, 
             not a failure.
        '''
        # Don't pollute the main library with unit tests    
        library = Library(parent=default_library)

        try:
            model = model_from_string(model_spec,
                                      config=config, library=library)
            model.init()
            return model
        except SemanticError as e:
            traceback.print_exc()
            self.fail("Semantic error for not parse model:\n%s\n"
                      "Got error: %s" % (self.write_fancy(model_spec), e))

    def check_syntax_error(self, model_spec):
        ''' Tests that the given string parsing gives a syntax error. '''
        try:
            parsed = parse_model(model_spec)
            self.fail('Expected SemanticError for model:\n%s\nParsed as:\n%s' %
                      (self.write_fancy(model_spec), parsed))
        except PGSyntaxError as e:
            e.__str__()
            return e

    def check_semantic_error(self, model_spec, config={}):
        ''' Tests that the given string parses ok 
            but gives a semantic error. '''
        # make sure we can parse it, before
        parsed = parse_model(model_spec)

        try:
            library = Library(parent=default_library)
            model = model_from_string(model_spec,
                                      config=config, library=library)
            model.init()
            # Note: we only have check_semantic_error, perhaps we need
            # another for the tests that do need init()?
            self.fail('Expected SemanticError for model:\n%s\n%s' %
                      (self.write_fancy(model_spec), parsed))

        except SemanticError as e:
            pass
            # make sure we can write it as a string 
            e.__str__()
            return e

    def check_execution_throws(self, possible_errors, model_spec, config={}):
        ''' Tests that the model execution throws the specific error
            semantic error. Returns the exception if it is thrown. '''
        library = Library(parent=default_library)
        model = model_from_string(model_spec, config=config, library=library)
        try:
            model.init()
            while model.has_more():
                model.update()
            model.finish()
            self.fail('Expected one of %s for model:\n%s' %
                      (str(possible_errors), self.write_fancy(model_spec)))
        except possible_errors as e:
            # make sure we can write e as a string:
            str(e)
            return e

    def write_fancy(self, model_spec):
        return add_prefix(model_spec, '  |')


class VerifyBlock(Block):
    ''' 
        This debug block verifies that config.x == config.y 
        and throws an exception if that's not the case.
    '''

    Block.alias('verify')

    Block.config('x')
    Block.config('y')

    def init(self):
        if self.config.x != self.config.y:
            raise SemanticError('Oops: "%s" != "%s".' % \
                                (self.config.x, self.config.y), self)

