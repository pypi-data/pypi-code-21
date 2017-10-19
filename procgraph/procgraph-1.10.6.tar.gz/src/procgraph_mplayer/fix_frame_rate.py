from procgraph import Generator, Block


class FixFrameRate(Generator):
    Block.alias('fix_frame_rate')
    Block.config('fps')

    Block.input('x')
    Block.output('xreg')
    
    def init(self):
        self.first_timestamp = None
        self.dt = 1.0 / self.config.fps
        self.nframes_rec = 0
        self.nframes_sent = 0
        self.current_time = None

    def update(self):
        
        # self.info('updated: T = %s' % self.get_input_timestamp(0))
        if self.first_timestamp is None:
            self.first_timestamp = self.get_input_timestamp(0)
            if self.first_timestamp is None:
                self.info('Strange, the input timestamp is none.')
                return    
            self.next_frame_to_output = self.first_timestamp - self.dt
            self.prev_x = self.get_input(0)
            
        x = self.get_input(0)

        x_updated = self.get_input_timestamp(0) != self.current_time
        if x_updated:
            self.nframes_rec += 1
            self.next_x = x
            
        self.current_time = self.get_input_timestamp(0)

        msg = 'x: %.3f  next: %.3f' % (self.current_time, self.next_frame_to_output)
        
        msg += '   (f in: %5d out: %5d)' % (self.nframes_rec, self.nframes_sent)
        
        if self.current_time > self.next_frame_to_output:
            self.set_output('xreg', self.prev_x, self.next_frame_to_output)    
            self.next_frame_to_output += self.dt
            self.nframes_sent += 1
            msg += ' -> writing'
        else:
            
            msg += ''
            
        # self.info(msg)
        
        
    def next_data_status(self):
        if self.first_timestamp is None:
            res = (False, None)  # changed from True
        else:
            if self.current_time > self.next_frame_to_output:
                res = (True, self.next_frame_to_output)
            else:
                res = (False, None)
                self.prev_x = self.next_x
        
        return res
