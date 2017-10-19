from procgraph import Block, ETERNITY


__all__ = ['Constant']

class Constant(Block):
    ''' Output a numerical constant that never changes.
    
        Example: ::
    
            |constant value=42| -> ...
            
    '''

    Block.alias('constant')

    Block.config('value', 'Constant value to output.')
    Block.output('constant', 'The constant value.')

    def update(self):
        # XXX: are you sure we need ETERNITY?
        self.set_output(0, self.config.value, timestamp=ETERNITY)

    def __repr__(self):
        return 'Constant(%s)' % self.config.value

