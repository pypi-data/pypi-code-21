from procgraph import Block

__all__ = ['History']

class History(Block):
    ''' 
    This block collects the history of a quantity,
    and outputs two signals ``x`` and ``t``. 
    See also :ref:`block:historyt` and :ref:`block:last_n_samples`.
    '''
    Block.alias('history')

    Block.config('interval', 'Length of the interval to record.', default=10)

    Block.input('values', 'Any signal.')

    Block.output('x', 'Sequence of values.')
    Block.output('t', 'Sequence of timestamps.')

    def init(self):
        self.history = HistoryInterval(self.config.interval)

    def update(self):
        sample = self.get_input(0)
        timestamp = self.get_input_timestamp(0)

        self.history.push(timestamp, sample)
        ts, xs = self.history.get_ts_xs()
        self.output.x = xs
        self.output.t = ts


class HistoryInterval(object):
    def __init__(self, interval):
        self.interval = interval
        self.x = []
        self.t = []
        
    def push(self, timestamp, value):
        
        self.x.append(value)
        self.t.append(timestamp)

        while abs(self.t[0] - self.t[-1]) > self.interval:
            self.t.pop(0)
            self.x.pop(0)

    def get_ts_xs(self):
        return list(self.t), list(self.x)
    
