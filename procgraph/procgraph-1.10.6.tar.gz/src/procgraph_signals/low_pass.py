from procgraph import Block


class LowPass(Block):
    ''' Implements simple low-pass filtering. 
    
    Formula used: ::
    
        y[k] = alpha * u[k] + (1-alpha) * y[k-1]
    
    '''
    # TODO: make a serious low-pass block
    Block.alias('low_pass')

    Block.config('alpha', 'Innovation rate')

    Block.input('value', 'Any numpy array.')
    Block.output('lowpass', 'The lowpass version.')

    def init(self):
        self.state.y = None

    def update(self):
        u = self.input[0]
        alpha = self.config.alpha

        if self.state.y is None:
            self.state.y = u
        else:
            self.state.y = self.state.y * (1 - alpha) + alpha * u

        self.output[0] = self.state.y


