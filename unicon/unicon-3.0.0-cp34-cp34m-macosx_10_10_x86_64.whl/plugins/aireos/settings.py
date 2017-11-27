from unicon.settings import Settings


class AireosSettings(Settings):
    def __init__(self):
        super().__init__()
        self.EXEC_TIMEOUT = 100
        self.SIZE = 8096
        self.HA_INIT_EXEC_COMMANDS = []
        self.HA_INIT_CONFIG_COMMANDS = [
            'paging disable',
            'sessions timeout 0',
            'serial timeout 0'
        ]
        self.RELOAD_TIMEOUT = 400
