# -*- coding: utf-8 -*-

class AleWrapper(WrapperBase):
    """Wrapper for the ale library"""
    def __init__(self, rom_path):
        raise NotImplementedError('Emulator currently not supported.')
        EmuWrapper.__init__(self)

        self._rom_path = os.path.expanduser(rom_path)
        self._ale = ale_python_interface.ALEInterface()

        # Set USE_SDL to true to display the screen. ALE must be compiled
        # with SDL enabled for this to work.
        USE_SDL = True
        if USE_SDL:
            self._ale.setBool('sound', False)
            self._ale.setBool('display_screen', True)

    def seed(self, seed):
        self._ale.setInt(b'random_seed', seed)

    def load_env(self, env, *args, **kwargs):
        rom = glob.glob(os.path.join(self._rom_path, env) + '*')
        if rom:
            self._ale.loadROM(rom[0])
        else:
            raise ValueError('Environment not found.')

    def get_output_dimensions(self, as_tuple=False):
        if as_tuple:
            return (self._ale.getScreenDims()[1], self._ale.getScreenDims()[0])
        else:
            return self._ale.getScreenDims()[0] * self._ale.getScreenDims()[1]

    def reset(self):
        self._ale.reset_game()

    def execute_action(self, action):
        self._reward = self._ale.act(action[0])
        self._done_buffer[0] = self._ale.game_over()
        return self._reward

    def update_output_buffer(self):
        assert(self._output_buffer is not None)
        self._output_buffer[0] = list(np.array(self._ale.getScreen().flatten(), dtype=np.float))

    def get_command_buffer(self):
        if self._command_buffer is None:
            self._command_buffer = [[0]]
        return self._command_buffer

    def get_output_buffer(self):
        if self._output_buffer is None:
            self._output_buffer = [list(np.zeros(self.get_output_dimensions(), dtype=np.float))]
        return self._output_buffer

