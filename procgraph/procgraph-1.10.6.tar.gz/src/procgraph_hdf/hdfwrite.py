from hdflog import PGHDFLogWriter
from procgraph import Block, BadInput
import numpy


__all__ = ['HDFwrite']


class HDFwrite(Block):
    ''' This block writes the incoming signals to a file in HDF_ format.
     
    The HDF format is organized as follows: ::
    
         /            (root)
         /procgraph             (group with name procgraph)
         /procgraph/signal1     (table)
         /procgraph/signal2     (table)
         ...
         
    Each table has the following fields:
    
         time         (float64 timestamp)
         value        (the datatype of the signal)
         
    If a signal changes datatype, then an exception is raised.
    
    '''

    Block.alias('hdfwrite')
    Block.input_is_variable('Signals to be written', min=1)
    Block.config('file', 'HDF file to write')
    Block.config('compress', 'Whether to compress the hdf table.', 1)
    Block.config('complib', 'Compression library (zlib, bzip2, blosc, lzo).',
                 default='zlib')
    Block.config('complevel', 'Compression level (0-9)', 9)

    def init(self):
        self.writer = PGHDFLogWriter(self.config.file,
                                     compress=self.config.compress,
                                     complevel=self.config.complevel,
                                     complib=self.config.complib)
        
    def update(self):
        signals = self.get_input_signals_names()
        for signal in signals:
            if self.input_update_available(signal):
                self.log_signal(signal)

    def log_signal(self, signal):
        timestamp = self.get_input_timestamp(signal)
        value = self.get_input(signal)
        # only do something if we have something 
        if value is None:
            return
        assert timestamp is not None

        if not isinstance(value, numpy.ndarray):
            # TODO: try converting
            try:
                value = numpy.array(value)
            except:
                msg = 'I can only log numpy arrays, not %r' % value.__class__
                raise BadInput(msg, self, signal)

        self.writer.log_signal(timestamp, signal, value)
        
    def finish(self):
        self.writer.finish()
        
