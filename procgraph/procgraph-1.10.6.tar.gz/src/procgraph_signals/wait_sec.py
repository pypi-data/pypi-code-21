from procgraph import Block

__all__ = ['WaitSec']

class WaitSec(Block):
    ''' 
        This block only transmits for t > t0.
        If retime is true, then the timestamp starts at 0.
    '''
    Block.alias('wait_sec')

    Block.config('t0', 'Delta to start.')
    Block.config('retime', "If true, retime from t=0", default=False)

    Block.input('x')
    Block.output('y')

    def init(self):
#         self.state.t0 = None
        pass
    
    def update(self):
        
        t = self.get_input_timestamp(0)
#         if self.state.t0 is None:
#             self.state.t0 = t
#             
        delta = t - self.config.t0
#         
#         self.info('config.t0 %.3f t %.3f delta %.3f' % (      self.config.t0,
#                                                               delta,  t))

        if delta > 0:
            if self.config.retime:
                t_ = delta
            else:
                t_ = t
#             self.info('t_: %s' % t_)
            self.set_output(0, value=self.get_input(0), timestamp=t_)
#         else:
#             self.info('skip')
    