from procgraph import Block
from . import np  # @PydevCodeAnalysisIgnore

class Minimum(Block):
    ''' Computes the minimum of a signal over time. '''

    Block.alias('minimum_over_time')

    Block.input('x', 'Any numpy array.')
    Block.output('min_x', 'Minimum of input.')

    def init(self):
        self.state.min_x = None

    def update(self):
        # TODO: check shape did not change
        if self.state.min_x is None:
            self.state.min_x = self.input.x
        else:
            self.state.min_x = np.minimum(self.state.min_x, self.input.x)
        self.output.min_x = self.state.min_x


class Maximum(Block):
    ''' Computes the minimum of a signal over time. '''

    Block.alias('maximum_over_time')

    Block.input('x', 'Any numpy array.')
    Block.output('max_x', 'Maximum of input over time.')

    def init(self):
        self.state.max_x = None

    def update(self):
        # TODO: check shape did not change
        if self.state.max_x is None:
            self.state.max_x = self.input.x
        else:
            self.state.max_x = np.maximum(self.state.max_x, self.input.x)
        self.output.max_x = self.state.max_x

