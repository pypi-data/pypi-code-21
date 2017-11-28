class FileNotFoundException(Exception):
    ''' Custom exception class whenever a file is not found. '''
    def __init__(self, path, message=None):
        if not message:
            message = "File {0} does not exist.".format(path)

        super().__init__("File {0} does not exist.".format(path))

        self.path = path
        self.message = message
