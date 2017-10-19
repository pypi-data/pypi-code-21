# In the simplest case, you only need to import "Block" from procgraph.
from procgraph import Block


class BlockSimpleExample(Block):
    ''' This is a documented example of the simplest block possible.
    
        This docstring will be included in the generated documentation.
    '''

    # Define a name for the block using `Block.alias`.
    # If not given, the class name ('BlockExample') will be used.
    Block.alias('block_example')

    # Define the inputs for the blocks using `Block.input`.
    # It takes two parameters: name of the signal, and a docstring.
    # ProcGraph will generate wonderful documentation for you, and lets
    # you write documentation for what you are doing at almost every step: 
    # take every chance to document things.
    Block.input('baz', 'Measured baz in the particle accelerator.')

    # This block has one output as well.
    Block.output('baz_compensated',
                 'Compensated baz value according to calibration.')

    # Now define the configuration for the block.
    # Pass the optional 'default' argument to define a default for the
    # parameter.
    # Without the default, the user *must* pass the configuration parameter.
    Block.config('bias', 'Bias for the accelerator.', default=0)

    # Now let's write the logic for the block.

    # Very important! Do not use __init__ for initialization. Use init().
    # ProcGraph does a lot behind the scenes to let you have a streamlined
    # experiences, but sometimes there is a price to pay. 
    # 
    # def __init__(self):
    #     ...
    #
    # Initialize the block in the init() function.
    def init(self):
        # For this example, we have nothing to do here.
        pass

    # You will write the main logic in the update() function.
    # It is called whenever the input signals are updated.
    # In update() you do your computations, and update the value 
    # of the output signals.
    def update(self):
        # You can access the value of the configuration parameters
        # using  `self.config.<parameter name>`
        bias = self.config.bias

        # You read the input signals using `self.input.<signal name>`: 
        baz = self.input.baz

        baz_compensated = baz + bias

        # Finally, you set the output using `self.output.<signal name> = ...`.
        self.output.baz_compensated = baz_compensated
        # You're done: ProcGraph will propagate this value to the other blocks 
        # connected...

        # Note that for stateless computations such as this, creating a Block
        # class is likely overkill -- use register_simple_block() with an 
        # instantaneous function instead -- see next example. 

    # Finish is called at the end of the execution.
    def finish(self):
        # For this example, we have nothing to do here.
        pass





