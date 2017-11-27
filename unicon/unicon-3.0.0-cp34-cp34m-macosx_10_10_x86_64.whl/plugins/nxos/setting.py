from unicon.plugins.generic.settings import GenericSettings

class NxosSettings(GenericSettings):

    def __init__(self):
        super().__init__()
        self.HA_INIT_EXEC_COMMANDS = [
            'term length 0',
            'term width 511',
            'terminal session-timeout 0'
        ]
        self.HA_INIT_CONFIG_COMMANDS = [
            'no logging console',
            'line console',
            'exec-timeout 0',
            'terminal width 511'
        ]
        self.SWITCHOVER_TIMEOUT = 700
        self.SWITCHOVER_COUNTER = 50
        self.HA_RELOAD_TIMEOUT = 700
        self.RELOAD_TIMEOUT = 400
