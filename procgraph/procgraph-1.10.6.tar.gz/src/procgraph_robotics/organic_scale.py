from procgraph import Block
from procgraph_images.copied_from_reprep import skim_top_and_bottom, skim_top

from numpy import maximum, minimum
import numpy


class OrganicScale(Block):
    ''' A (almost failed!) attempt to scale a signal into [-1,1] 
        according to the history. 
        
        This one is a mess.
    '''

    Block.alias('organic_scale')

    Block.input('value')
    Block.output('value_scaled')

    Block.config('skim', default=5)
    Block.config('skim_hist', default=5)
    Block.config('hist', 'How many steps of history to use.', default=100)
    Block.config('tau', default=0.1)

    def init(self):
        self.state.max = []
        self.state.M = None

    def update(self):
        y = numpy.array(self.input.value)
        # first skim it
        y = skim_top_and_bottom(y, self.config.skim)
        # put the max in the history
        self.state.max.insert(0, max(abs(y)))
        # prune the history
        self.state.max = self.state.max[:self.config.hist]
        # get the history percent
        M = max(skim_top(numpy.array(self.state.max), self.config.skim_hist))

        if self.state.M is None:
            self.state.M = M
        else:
            self.state.M += self.config.tau * (M - self.state.M)

        y = minimum(y, self.state.M)
        y = maximum(y, -self.state.M)

        y = y / self.state.M
        self.output.value_scaled = y


