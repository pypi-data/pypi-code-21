from procgraph import Generator, Block, ModelExecutionError, BadConfig
import os
import traceback

__all__ = [
    'TextLog',
]

class TextLog(Generator):
    ''' 
        This represents a generic log reader that reads
        from a file line-by-line. 
        
        Subclasses should overload the parse_format() static method.
        Also they should put the adequate output() methods.
    '''

    Block.config('file', 'File to read. If it ends with ``bz2``, it is treated'
                         ' as compressed.')

    def init(self):
        filename = self.config.file
        filename = os.path.expandvars(filename)
        filename = os.path.expanduser(filename)

        if not os.path.exists(filename):
            raise BadConfig('File %r does not exist.' % filename, self, 'file')

        # TODO: add .gz
        if filename.endswith('bz2'):
            import bz2
            self.stream = bz2.BZ2File(filename)
        else:
            self.stream = open(filename, 'r')

        self.state.line = 0  # line counter
        self.read_next_line()

        if self.timestamp is None:
            raise Exception('Empty file %s' % filename)

    def read_next_line(self):
        line = self.state.line
        while True:
            next_line = self.stream.readline()
            # skip empty lines
            if next_line == '\n':
                continue
            else:
                break

        # check end of file
        if not next_line:
            self.timestamp = None
            self.values = None
            return

        # strip newline
        next_line = next_line.rstrip('\n')

        try:
            result_tuple = self.parse_format(next_line)
            # if the line is valid, result_tuple is a tuple
            if result_tuple is not None:
                # TODO: add explicit check
                if not isinstance(result_tuple, tuple) or len(result_tuple) != 2:
                    msg = 'Expected tuple of len 2, got %s' % result_tuple
                    raise ValueError(msg)
                self.timestamp, self.values = result_tuple
                
                if not isinstance(self.values, list):
                    msg = 'Expected a list'
                    raise ValueError(self.values)
                for x in self.values:
                    if not isinstance(x, tuple) or len(x) != 2:
                        msg = 'Expected a tuple name/value'
                        raise ValueError(self.values)
                    
                self.state.line = line + 1
            else:
                # If the result is None, it means the line did not contain
                # data relevant for us; skip to the next one
                self.state.line = line + 1
                self.read_next_line()
        except Exception as e:
            traceback.print_exc()
            msg = ("While reading line %s of file %s (='%s'): %s" % 
                   (line, self.get_config('file'), next_line, e))
            raise ModelExecutionError(msg, self)

    def next_data_status(self):
        # TODO: put new interface
        if self.timestamp is None:  # EOF
            return (False, None)
        else:
            return (True, self.timestamp)

    def update(self):
        for signal, value in self.values:
            self.set_output(signal, value, timestamp=self.timestamp)

        self.read_next_line()

    def parse_format(self, line):
        """ 
            Function implemented by subclasses to interpret one line from 
            the log.
        
            Return None is the line should be ignored (for example it is 
            a comment). Otherwise, return a tuple (timestamp, array of 
            (name, value) ).
        """
        raise ValueError("Function parse_format() not implemented.")

