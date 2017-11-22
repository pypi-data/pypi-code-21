'''
Custom exception class whenever project is not valid android.
'''

MESSAGE = 'You are not in a valid android project.'

class InvalidAndroidProjectException(Exception):
    ''' Custom exception class whenever project is not valid android.'''
    def __init__(self, message=None):
        if not message:
            message = MESSAGE

        super().__init__(message)

        self.message = message
