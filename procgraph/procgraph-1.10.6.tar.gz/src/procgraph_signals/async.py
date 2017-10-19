from procgraph import Block


class ASync(Block):
    ''' 
      The first signal is the "master".
      Waits that all signals are perceived once.
      Then it creates one event every time the master arrives.
    '''
    Block.alias('async')

    Block.input_is_variable('Signals to (a)synchronize. The first is the master.', min=2)
    Block.output_is_variable('Synchronized signals.')

    def init(self):
        self.state.last_sent_timestamp = None

    def update(self):
        self.state.last_timestamp = None

        # No signal until everybody is ready
        if not self.all_input_signals_ready():
            return

        # No signal unless the master is ready
        master_timestamp = self.get_input_timestamp(0)
        if self.state.last_timestamp == master_timestamp:
            return

        self.state.last_timestamp = master_timestamp

        # Write all signals using master's timestamp 
        for s in self.get_input_signals_names():
            self.set_output(s, self.get_input(s), master_timestamp)


