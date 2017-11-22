'''
Custom Exception when a `package.json` field is not found.
'''
from lib.exceptions.FileNotFound import FileNotFoundException

MESSAGE = 'A valid package.json was not found.'

class PackageJsonNotFoundException(FileNotFoundException):
    ''' Custom exception class whenever a file is not found. '''
    def __init__(self, message=None):
        if not message:
            message = MESSAGE

        super().__init__(message)

        self.message = message
