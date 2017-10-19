from procgraph import Block


class FPSDataLimit(Block):
    ''' This block limits the output update to a certain framerate. '''
    Block.alias('fps_data_limit')

    Block.config('fps', 'Maximum framerate.')

    Block.input_is_variable('Signals to decimate.', min=1)
    Block.output_is_variable('Decimated signals.')

    def init(self):
        self.state.last_timestamp = None

    def update(self):
        should_update = False

        last = self.state.last_timestamp
        current = max(self.get_input_signals_timestamps())

        if last is None:
            should_update = True
            self.state.last_timestamp = current
        else:
            fps = self.config.fps
            delta = 1.0 / fps
            difference = current - last
            if difference > delta:
                should_update = True
                self.state.last_timestamp = current

        if not should_update:
            return
        # Just copy the input to the output
        for i in range(self.num_input_signals()):
            self.set_output(i, self.get_input(i), self.get_input_timestamp(i))



