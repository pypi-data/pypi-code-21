from procgraph import Block
import numpy as np

class TimeSlice(Block):
    ''' 
    This block collects the history of a quantity for a given
    interval length, and it outputs a list of values when the 
    buffer is full. Then it resets the buffer.
    
    See also :ref:`block:historyt` and :ref:`block:last_n_samples`.
    '''
    Block.alias('time_slice')

    Block.config('interval', 'Length of the interval to record.', default=10)

    Block.input('values', 'Any signal.')

    Block.output('grouped', 'List of the values in a given interval.')
    
    def init(self):
        self.x = []
        self.t = []

    def update(self):
        sample = self.get_input(0)
        timestamp = self.get_input_timestamp(0)
        
        self.x.append(sample)
        self.t.append(timestamp)

        delta = self.t[-1] - self.t[0]
#        self.info('Delta: %.10f sec  n = %6d' % (delta, len(self.t)))
        if np.abs(delta) >= self.config.interval:
            self.set_output(0, value=self.x, timestamp=self.t[0])
            self.x = []
            self.t = []
            
        
