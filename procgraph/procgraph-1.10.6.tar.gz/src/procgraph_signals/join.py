import numpy as np

from procgraph import Block


class Join(Block):
    ''' 
    This block joins multiple signals into one.
    '''

    Block.alias('join')

    Block.input_is_variable('Signals to be joined together.')
    Block.output('joined', 'Joined signals.')

    def init(self):
        sizes = {}
        names = self.get_input_signals_names()
        for signal in names:
            sizes[signal] = None

        self.state.sizes = sizes

    def update(self):
        sizes = self.state.sizes
        result = []
        for name in self.get_input_signals_names():
            value = self.get_input(name)
            # workaround for scalar values
            value = np.reshape(value, np.size(value))
            size = len(value)
            if value is None:
                return
            if sizes[name] is None:
                sizes[name] = size
            else:
                if size != sizes[name]:
                    raise Exception('Signal %s changed size from %s to %s.' %
                                    (name, sizes[name], size))

            result.extend(value)

        self.output[0] = np.array(result)


