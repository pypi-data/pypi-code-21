from procgraph import Block


class ToFile(Block):
    ''' Prints the input line by line to a given file.'''
    Block.alias('to_file')

    Block.config('file', 'File to write.')

    Block.input('values', 'Anything you wish to print to file.')

    def init(self):
        self.file = open(self.config.file, 'w')

    def update(self):
        s = str(self.input[0])
        self.file.write(s)
        self.file.write('\n')
        self.file.flush()
