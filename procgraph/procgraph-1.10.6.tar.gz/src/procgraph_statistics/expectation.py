from . import np  # @PydevCodeAnalysisIgnore
from procgraph import Block

class Expectation(Block):
    ''' Computes the sample expectation of a signal. '''
    Block.alias('expectation')

    Block.input('x', 'Any numpy array.')
    Block.output('Ex', 'Expectation of input.')

    def init(self):
        self.state.num_samples = 0

    def update(self):
        N = self.state.num_samples

        if N == 0:
            self.state.Ex = self.input.x.copy()
        else:
            self.state.Ex = (self.state.Ex * N + self.input.x) / float(N + 1)

        self.state.num_samples += 1
        self.output.Ex = self.state.Ex



class ExpectationNorm(Block):
    Block.alias('expectation_norm')

    Block.input('x', 'Any numpy array.')
    Block.output('Ex', 'Expectation of input.')

    def init(self):
        self.value = None
        self.mass = None
        
    def update(self):
        x = self.input.x
        if self.value is None:
            self.value = x
            self.weight = np.zeros(x.shape)
        else:
            if False:
                w = np.abs(x - self.last_x)
            else:
                w = np.abs(x - self.last_x).sum()
            self.weight += w
            self.value += w * x
            
            self.weight[self.weight == 0] = np.inf
            res = self.value / self.weight 
            self.output.Ex = res
        self.last_x = x.copy()
 
