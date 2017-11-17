from unicon.patterns import UniconCorePatterns


class AireosReloadPatterns(UniconCorePatterns):
    def __init__(self):
        super().__init__()
        self.force_reboot = r'Do you still want to force a reboot \(y/N\)'
        self.are_you_sure = r'Are you sure you want to start.*\(y/N\)'
        self.system_restart = r'System will now restart'


class AireosPingPatterns(UniconCorePatterns):
    def __init__(self):
        super().__init__()
        self.bad_ping = r'Receive count=0'
        self.incorrect_ping = r'Incorrect'


class AireosCopyPatterns(UniconCorePatterns):
    def __init__(self):
        super().__init__()
        self.tftp_starting = r'TFTP[^\n\r]+transfer starting'
        self.tftp_complete = r'TFTP receive complete'
        self.restart_system = r'Restarting system'
        self.reboot_to_complete = r'Reboot the controller for update to complete..*to reduce network downtime'
        self.are_you_sure_save = r'Are you sure you want to save\? \(y/n\)'


class AireosPatterns(UniconCorePatterns):
    def __init__(self):
        super().__init__()
        self.base = r'\s*\([^\r\n]*\)\s+'
        self.mode = self.base + '[^\n\r]+>\s*$'
        self.bare = self.base + '\s*>\s*$'
        self.user = r'^.*User:\s*$'
        self.password = r'^.*Password:\s?$'
        #self.escape = r'Escape character is.*\..*\r\r\n'
        self.escape = r"Escape character is .*\n"

        self.shell = r'bash.*#'
        self.prompt = r'^.*' + self.base
