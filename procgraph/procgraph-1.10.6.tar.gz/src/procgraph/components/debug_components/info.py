from procgraph import Block
from datetime import datetime

__all__ = ['Info']

class Info(Block):
    ''' 
        Prints more compact information about the inputs 
        than :ref:`block:print`.
    
        For numpy arrays it prints their shape and dtype 
        instead of their values. 
        
    '''
    Block.alias('info')
    Block.input_is_variable('Signals to describe.', min=1)

    def init(self):
        self.first = {}
        self.counter = {}

    def update(self):
        # Just copy the input to the output 
        for i in range(self.num_input_signals()):
            name = self.canonicalize_input(i)
            val = self.get_input(i)
            ts = self.get_input_timestamp(i)
            
            if ts is None:
                continue
            
            if not i in self.first:
                self.first[i] = ts
                self.counter[i] = 0
            friendly = ts - self.first[i]
#             if isinstance(val, numpy.ndarray):
#                 s = "%s %s" % (str(val.shape), str(val.dtype))
#             else:
            s = str(val)
            if len(s) > 40:
                s = s[:40]
            s = s.replace('\n', '|')
            date = datetime.fromtimestamp(ts).isoformat(' ')[:-4]
            ts = "%.2f" % ts
            self.debug('%s (%8.2fs) %12s %5d  %s' % 
                       (date, friendly, name, self.counter[i], s))
            self.counter[i] += 1

