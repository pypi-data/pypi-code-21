'''
Custom Exception when a `AndroidManifest.xml` file is not found.
'''
from lib.exceptions.FileNotFound import FileNotFoundException

MESSAGE = 'A valid AndroidManifest.xml was not found'

class ManifestNotFoundException(FileNotFoundException):
    ''' Custom exception class whenever manifest is not found. '''
    def __init__(self, message=None):
        if not message:
            message = MESSAGE

        super().__init__(message)

        self.message = message
