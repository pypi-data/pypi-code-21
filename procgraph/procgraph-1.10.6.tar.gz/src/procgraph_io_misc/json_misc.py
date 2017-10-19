from . import json

from procgraph import Block


class AsJSON(Block):
    ''' Converts the input into a JSON string. 
    
        TODO: add example
    '''

    Block.alias('as_json')

    Block.input_is_variable('Inputs to transcribe as JSON.')

    Block.output('json', 'JSON string.')

    def update(self):
        data = {}
        data['timestamp'] = max(self.get_input_signals_timestamps())
        for i in range(self.num_input_signals()):
            name = self.canonicalize_input(i)
            value = self.input[name]
            data[name] = value

        self.output.json = json.dumps(data)

