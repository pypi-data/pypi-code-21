import traceback

from contracts import describe_type, indent, contract


__all__ = [
    'Library',
    'default_library',
]


class Library(object):

    def __init__(self, parent=None):
        self.parent = parent

        self.name2block = {}

        # Set of filenames already looked into
        self.loaded_files = set()

    def exists(self, block_type):
        if block_type in self.name2block:
            return True
        else:
            if self.parent is not None:
                return self.parent.exists(block_type)
            else:
                return False

    def register(self, block_type, generator):
        if self.exists(block_type):
            msg = 'Type %r already registered.' % block_type
            raise ValueError(msg)
            
        self.name2block[block_type] = generator

    def instance(self, block_type, name, config, library=None):
        from procgraph.core.exceptions import ModelInstantionError, SemanticError
        if library is None:
            library = self
        generator = self.get_generator_for_block_type(block_type)
        try:
            block = generator(name=name, config=config, library=library)
        except Exception as e:
            msg = 'Could not instance block from generator.\n'
            msg += '        name: %s  \n' % name
            msg += '      config: %s  \n' % config
            msg += '   generator: %s  \n' % generator
            msg += '     of type: %s  \n' % describe_type(generator)
            msg += 'Because of this exception:\n'
            if isinstance(e, (SemanticError, ModelInstantionError)):
                msg += indent('%s' % e, '| ')
            else:
                msg += indent('%s\n%s' % (e, traceback.format_exc(e)), '| ')
            raise ModelInstantionError(msg)  # TODO: use Procgraph own exception

        block.__dict__['generator'] = generator
        return block

    def get_generator_for_block_type(self, block_type):
        ''' Returns the generator object for the block type.
        
            A generator can instance using:
            
                generator(name, config, library)
                
            and it can provide (before instancing) the properties:
            
                generator.config
                generator.input
                generator.output
        '''

        if not self.exists(block_type):
            msg = 'Block %r does not exist.' % block_type

            msg += '\n Known: %s' % self.get_known_blocks()
            raise ValueError(msg)

        if block_type in self.name2block:
            generator = self.name2block[block_type]
            return generator
        else:
            assert self.parent
            return self.parent.get_generator_for_block_type(block_type)

    @contract(returns='list(str)')
    def get_known_blocks(self):
        blocks = list(self.name2block.keys())
        if self.parent:
            blocks.extend(self.parent.get_known_blocks())
        return blocks


default_library = Library()



