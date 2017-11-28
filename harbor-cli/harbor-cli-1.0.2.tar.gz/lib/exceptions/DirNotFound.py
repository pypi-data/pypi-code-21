class DirNotFoundException(Exception):
    ''' Custom exception class whenever a file is not found. '''
    def __init__(self, path, message=None):
        if not message:
            message = "Directory {0} does not exist.".format(path)

        super().__init__(message)

        self.path = path
        self.message = message
