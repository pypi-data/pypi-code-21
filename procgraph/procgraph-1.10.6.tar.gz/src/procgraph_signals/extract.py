from procgraph import Block, COMPULSORY, simple_block
import numpy as np


class Extract(Block):
    ''' 
    This block extracts some of the components of a vector.
    
    Example: Extracts the first and third component of x. ::
    
        x -> |extract index=[0,2]| -> x_part
        
        
    '''
    Block.alias('extract')
    Block.input('vector', 'Any numpy array')
    Block.output('part', 'The part extracted')
    Block.config('index', 'Index (or indices) to extract.')

    def update(self):
        index = self.config.index
        vector = np.array(self.input.vector)

        part = vector[index]

        self.output.part = part


@simple_block
def slice(signal, start=COMPULSORY, end=COMPULSORY): #@ReservedAssignment
    ''' Slices a signal by extracting from index ``start`` to index ``end``
        (INCLUSIVE).
        
        :param signal: Any 1d numpy array
        :param start:  Slice start.
        :param end:    Slice end (inclusive).
        
        :return: sliced: The sliced signal.
    '''
    assert start != COMPULSORY
    assert end != COMPULSORY
    return signal[start:(end + 1)]


