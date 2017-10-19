from procgraph import Block

__all__ = ['AllReady']


class AllReady(Block):
    ''' 
        This block outputs the inputs, unchanged. 
    '''
    
    Block.alias('all_ready')
    
    Block.input_is_variable('Input signals.', min=1)
    Block.output_is_variable('Output signals, equal to input.')

    
    def update(self):
        if not self.all_input_signals_ready():
            return
        
        for i in range(self.num_input_signals()):
            if self.input_update_available(i):
                t, value = self.get_input_ts_and_value(i)
                self.set_output(i, value, t)

