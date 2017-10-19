from procgraph import Block

__all__ = ['Wait']

class Wait(Block):
    ''' 
        This block waits a given number of updates before transmitting the 
        output signal.
    '''
    Block.alias('wait')

    Block.config('n', 'Number of updates to wait at the beginning.')

    Block.input_is_variable('Arbitrary signals.')
    Block.output_is_variable('Copy of the signals, minus the first '
                             '*n* updates.')

    def init(self):
        self.state.count = 0

    def update(self):
        count = self.state.count

        # make something happen after we have waited enough
        if count >= self.config.n:
            # Just copy the input to the output
            for i in range(self.num_input_signals()):
                self.set_output(i, self.get_input(i),
                                self.get_input_timestamp(i))

        self.state.count = count + 1
