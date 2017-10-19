from procgraph import Block

__all__ = ['Retime', 'RewriteTimestamps']

class Retime(Block):
    ''' 
        Multiplies timestamps by give factor
    '''
    Block.alias('retime')

    Block.config('factor', 'Factor')

    Block.input('x')
    Block.output('y')

    def init(self):
        pass

    def update(self):
        value = self.get_input(0)
        t = self.get_input_timestamp(0)
        t_ = t * self.config.factor
        self.set_output(0, value, t_)


class RewriteTimestamps(Block):
    ''' 
        Retims the timestamps equally spaced.
        
        [0, interval, interval*2, interval*3, ...]
    '''
    Block.alias('rewrite_timestamps')

    Block.config('interval', 'interval')

    Block.input('x')
    Block.output('y')

    def init(self):
        self.i = 1
    
    def update(self):        
        value = self.get_input(0)
        t = self.i * self.config.interval
        self.i += 1
        self.set_output(0, value, t)
