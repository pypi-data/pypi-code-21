class UserNotFoundException(Exception):
    ''' Custom exception class whenever a user is not found. '''
    def __init__(self, message=None):
        if not message:
            message = "User not found."

        super().__init__(message)

        self.message = message
