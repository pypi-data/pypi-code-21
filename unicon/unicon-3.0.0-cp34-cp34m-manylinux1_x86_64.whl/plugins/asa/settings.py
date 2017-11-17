from unicon.settings import Settings


class ASASettings(Settings):
    def __init__(self):
        super().__init__()
        self.EXEC_TIMEOUT = 100
        self.SIZE = 8096
        self.HA_INIT_EXEC_COMMANDS = []
        self.HA_INIT_CONFIG_COMMANDS = [
            'terminal pager 0',
        ]

        # When connecting to a device via telnet, how long to pause before
        # checking the spawn buffer.
        self.ESCAPE_CHAR_CALLBACK_PAUSE_SEC = 1

        # sendline is called if the spawn buffer is empty after a pause, or
        # after trying a pause/spawn buffer check this many times.
        self.ESCAPE_CHAR_CALLBACK_PAUSE_CHECK_RETRIES = 5

        # Sometimes a copy operation can fail due to network issues,
        # so copy at most this many times.
        self.MAX_COPY_ATTEMPTS = 2
