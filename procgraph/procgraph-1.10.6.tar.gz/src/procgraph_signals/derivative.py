import numpy

from procgraph import Block, BadInput, register_model_spec


def isiterable(x):
    ''' Checks that an object is iterable. '''
    try:
        iter(x)
        return True
    except TypeError:
        return False


class ForwardDifference(Block):
    ''' Computes ``x[t+1] - x[t-1]`` normalized with timestamp. 
    
        You want to attach this to :ref:`block:last_n_samples`.
    '''
    Block.alias('forward_difference')
    
    Block.input('x123', 'An array with the last 3 values of x.')
    Block.input('t123', 'An array with the last 3 values of the timestamp.')
    
    Block.output('x_dot', 'Derivative of x')
        
    def update(self):
        x = self.input.x123
        t = self.input.t123
        if not isiterable(x) or len(x) != 3:
            raise BadInput('Expected arrays of 3 elements', self, 'x')
        if not isiterable(t) or len(t) != 3:
            raise BadInput('Expected arrays of 3 elements', self, 't')
       
        delta = t[2] - t[0]
        
        if not delta > 0:
            raise BadInput('Bad timestamp sequence % s' % t, self, 't')

        # if this is a sequence of bytes, let's promove them to floats
        if x[0].dtype == numpy.dtype('uint8'):
            diff = x[2].astype('float32') - x[0].astype('float32')
        else:
            diff = x[2] - x[0]
        time = t[1]
        x_dot = diff / numpy.float32(delta)
        self.set_output('x_dot', x_dot, timestamp=time)   

# TODO: move this to models/
register_model_spec("""
--- model derivative 
''' Computes the derivative of a quantity with 3 taps  (``x[t+1] - x[t-1]``).
    See also :ref:`block:derivative2`.                   '''
input x "quantity to derive"
output x_dot "approximate derivative"

|input name=x| --> |last_n_samples n=3| --> x,t

   x, t --> |forward_difference| --> |output name=x_dot|
    
""")

