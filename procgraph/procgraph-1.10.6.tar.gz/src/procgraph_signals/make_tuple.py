from procgraph import Block


class MakeTuple(Block):
    ''' Creates a tuple out of the input signals values. 
    
        Often used for plotting two signals as (x,y); see :ref:`block:plot`.
    '''

    Block.alias('make_tuple')

    Block.input_is_variable('Signals to unite in a tuple.')

    Block.output('tuple', 'Tuple containing signals.')

    def update(self):
        values = self.get_input_signals_values()
        self.output.tuple = tuple(values)

