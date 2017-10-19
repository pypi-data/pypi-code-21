from procgraph import Block

__all__ = ['Identity']


class Identity(Block):
    ''' 
        This block outputs the inputs, unchanged. 
    '''

    Block.alias('identity')
    Block.input_is_variable('Input signals.', min=1)
    Block.output_is_variable('Output signals, equal to input.')

    def update(self):
        # Just copy the input to the output
        for i in range(self.num_input_signals()):
            self.set_output(i, self.get_input(i),
                               self.get_input_timestamp(i))

