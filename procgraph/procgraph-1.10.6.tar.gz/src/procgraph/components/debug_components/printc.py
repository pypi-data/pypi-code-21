from procgraph import Block


class Print(Block):
    ''' 
        Print a representation of the input values along with 
        their timestamp. 
    '''

    Block.alias('print')

    Block.input_is_variable('Signals to print.', min=1)

    def update(self):
        for i in range(self.num_input_signals()):
            print('P %s %s %s' % (self.canonicalize_input(i),
                                  self.get_input_timestamp(i),
                                  self.get_input(i)))

