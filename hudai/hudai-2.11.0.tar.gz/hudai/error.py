class HudAiError(Exception):
    def __init__(self, message=None, type='validation_error'):
        super(HudAiError, self).__init__(message)

        self._message = message
        self.type = type
