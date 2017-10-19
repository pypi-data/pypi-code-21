import numpy

from procgraph import Block, BadInput, register_model_spec


def isiterable(x):
    try:
        iter(x)
        return True
    except TypeError:
        return False


class ForwardDifference12(Block):
    ''' Computes ``x[t+1] - x[t]`` normalized with timestamp. '''

    Block.alias('two_step_difference')

    Block.input('x12', 'An array with the last 2 values of x.')
    Block.input('t12', 'An array with the last 2 values of the timestamp.')

    Block.output('x_dot', 'Derivative of x')

    def update(self):
        x = self.input.x12
        t = self.input.t12
        if not isiterable(x) or len(x) != 2:
            raise BadInput('Expected arrays of 2 elements', self, 'x')
        if not isiterable(t) or len(t) != 2:
            raise BadInput('Expected arrays of 2 elements', self, 't')

        delta = t[1] - t[0]

        if not delta > 0:
            raise BadInput('Bad timestamp sequence % s' % t, self, 't')

        # if this is a sequence of bytes, let's promove them to floats
        if x[0].dtype == numpy.dtype('uint8'):
            diff = x[1].astype('float32') - x[0].astype('float32')
        else:
            diff = x[1] - x[0]
        time = t[0]
        x_dot = diff / numpy.float32(delta)
        self.set_output('x_dot', x_dot, timestamp=time)

# TODO: move this to models/
register_model_spec("""
--- model derivative2
''' Computes the derivative of a quantity with 2 taps (``x[t+1] - x[t]``).
    See also :ref:`block:derivative`.       '''
input x "quantity to derive"
output x_dot "approximate derivative"

|input name=x| --> |last_n_samples n=2| --> x,t

   x, t --> |two_step_difference| --> |output name=x_dot|
    
""")

