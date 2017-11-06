

class ClientError(Exception):
    def __init__(self, message, code=0, *args):
        super().__init__(message, *args)
        self.code = code


class ResourceNotFoundException(ClientError):
    def __init__(self, message, *args):
        super().__init__(message, code=404, *args)
