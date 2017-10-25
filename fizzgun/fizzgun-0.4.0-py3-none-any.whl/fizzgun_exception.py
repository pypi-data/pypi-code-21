
class FizzgunException(Exception):
    def __init__(self, message, reason=None):
        super(FizzgunException, self).__init__()
        self._message = message
        self._reason = reason

    @property
    def message(self):
        return self._message

    @property
    def reason(self):
        return self._reason
