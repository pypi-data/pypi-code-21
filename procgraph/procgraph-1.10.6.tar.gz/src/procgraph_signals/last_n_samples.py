from procgraph import Block


class HistoryN(Block):
    ''' 
    This block collects the last N samples of a signals,
    and outputs two signals ``x`` and ``t``. 
    See also :ref:`block:historyt` and :ref:`block:history`.
    '''
    Block.alias('last_n_samples')

    Block.config('n', 'Number of samples to retain.')

    Block.input('x', 'Any data')

    Block.output('x', 'Sequence of values.')
    Block.output('t', 'Sequence of timestamps.')

    def init(self):
        self.state.x = []
        self.state.t = []

    def update(self):

        sample = self.get_input(0)
        timestamp = self.get_input_timestamp(0)

        x = self.state.x
        t = self.state.t

        x.append(sample)
        t.append(timestamp)

        n = self.config.n
        while len(x) > n:
            t.pop(0)
            x.pop(0)

        if len(x) == n:
            self.output.x = x
            self.output.t = t
