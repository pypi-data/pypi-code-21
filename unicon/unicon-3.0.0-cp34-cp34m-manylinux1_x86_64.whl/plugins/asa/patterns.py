from unicon.patterns import UniconCorePatterns

class ASAPatterns(UniconCorePatterns):
    def __init__(self):
        super().__init__()
        
        self.disable_prompt = r'^.+?>\s*$'
        self.enable_prompt = r'^.+?#\s*$'
        self.line_password = r"^.+?@.+?'s +password: *$"
        self.enable_password = r'^.*Password:\s?$'
        self.config_prompt = r'^(.*)\(.*(con|cfg|ipsec-profile).*\)#\s?$'
        self.bad_passwords = r'^Permission denied, please try again.$'
        self.disconnect_message = r'^Connection to .+? closed by remote host$'
