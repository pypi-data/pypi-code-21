from procgraph import Generator, Block

__all__ = ['Clock']

class Clock(Generator):
    Block.alias('clock')
    Block.config('interval', 'Delta between ticks.', default=1)
    Block.output('clock', 'Clock signal.')
    Block.config('length', 'Total interval', default=None)
    
    def init(self):
        self.state.clock = 0.0

    def update(self):
        self.set_output('clock', self.state.clock, timestamp=self.state.clock)
        self.state.clock += self.config.interval

    def next_data_status(self):
        if self.config.length is not None and self.state.clock > self.config.length:
            return (False, None)
        else:
            return (True, self.state.clock + self.config.interval)



