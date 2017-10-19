from procgraph import Block


class Any(Block):
    ''' 
        Joins the stream of multiple signals onto one output signal.
    '''

    Block.alias('any')

    Block.input_is_variable('Signals to be put on the same stream.', min=1)
    Block.output('stream', 'Unified stream.')

    def init(self):
        self.last_ts = {}
        self.buffer = []

    def update(self):
        # DO NOT USE NAMES
        # TODO: check other blocks for this bug
        nsignals = self.num_input_signals()
        for i in range(nsignals):
            value = self.get_input(i)
            ts = self.get_input_timestamp(i)
            if value is None:
                continue
            if not i in self.last_ts or ts != self.last_ts[i]:
                self.buffer.append((ts, value))
            self.last_ts[i] = ts

#        t = [x[0] for x in self.buffer]
#        self.debug(' after1: %s' % t)
#                
        self.buffer = sorted(self.buffer, key=lambda x: x[0])

#        t = [x[0] for x in self.buffer]
#        self.debug(' sort: %s' % t)

        # Make sure we saw every signal before outputing one
#        if len(self.last_ts) == nsignals:
        # FIXME: bug we will send one sample of the last stream

        if self.buffer:
            ts, value = self.buffer.pop(0)
            self.set_output(0, value, ts)

#        t = [x[0] for x in self.buffer]
#        self.debug(' after2: %s' % t)

#        self.debug('Got %s, chose %s' % (),
#                                                timestamp))
#          

