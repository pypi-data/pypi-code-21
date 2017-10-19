from procgraph import Block

__all__ = ['Gain']

class Gain(Block):
    ''' A simple example of a gain block. '''

    Block.alias('gain')

    Block.config('k', 'Multiplicative gain')

    Block.input('in', 'Input value')
    Block.output('out', 'Output multiplied by k.')

    def update(self):
        self.output[0] = self.input[0] * self.config.k

