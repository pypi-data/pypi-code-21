from procgraph  import Block


class HistoryT(Block):
    ''' 
    This block collects the signals samples of a signals,
    and outputs *one* signal containing a tuple  ``(t,x)``. 
    See also :ref:`block:last_n_samples` and :ref:`block:history`.
    
    If ``natural`` is true, it uses the time from the beginning of the log.
     
    '''
    Block.alias('historyt')

    Block.config('interval', 'Length of interval (seconds).', default=10)
    Block.config('natural', 'If true, set 0 to be timestamp of the log '
                 'beginning. This allows to have prettier graphs',
                 default=True)

    Block.input('x', 'Any signal.')
    Block.output('history', 'Tuple ``(t,x)`` containing two arrays.')

    def init(self):
        self.state.x = []
        self.state.t = []
        self.state.first_timestamp = None

    def update(self):
        sample = self.get_input(0)
        timestamp = self.get_input_timestamp(0)

        if self.state.first_timestamp is None:
            self.state.first_timestamp = timestamp

        if self.config.natural:
            timestamp = timestamp - self.state.first_timestamp

        x = self.state.x
        t = self.state.t

        x.append(sample)
        t.append(timestamp)

        while abs(t[0] - t[-1]) > self.config.interval:
            t.pop(0)
            x.pop(0)

        self.output.history = (t, x)

