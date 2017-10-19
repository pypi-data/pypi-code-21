from .block import Block


class ModelInput(Block):
    ''' This represents one input to the model. '''

    Block.alias('input')

    Block.config('name', 'Input signal name.')

    Block.output('dummy')

    def init(self):
        self.signal_name = self.config.name

    def update(self):
        pass


class ModelOutput(Block):
    ''' This represents one output to the model. '''

    Block.alias('output')

    Block.config('name', 'Output signal name')

    Block.input('dummy')

    def init(self):
        self.signal_name = self.config.name

    def update(self):
        pass



