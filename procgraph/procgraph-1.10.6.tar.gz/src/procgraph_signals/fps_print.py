from procgraph import Block


class FPSPrint(Block):
    ''' Prints the fps count for the input signals. '''
    Block.alias('fps_print')

    Block.input_is_variable('Any signal.', min=1)

    def init(self):
        self.state.last_timestamp = None

    def update(self):
        current = max(self.get_input_signals_timestamps())
        last = self.state.last_timestamp
        if last is not None:

            difference = current - last
            fps = 1.0 / difference

            self.info("FPS %s %.1f" % (self.canonicalize_input(0), fps))

        self.state.last_timestamp = current


