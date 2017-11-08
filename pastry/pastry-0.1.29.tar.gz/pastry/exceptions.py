'''exceptions for pastry events'''


class HttpError(Exception):
    '''
    Exception calling http request -adds teh ststus code)
    '''
    def __init__(self, message, statuscode, *args, **kwargs):
        '''
        Create the Exception
        '''
        self.statuscode = statuscode
        super(HttpError, self).__init__(message, *args, **kwargs)

    def __str__(self):
        '''
        Show the exception and statuscode
        '''
        return '(%s) %s' % (self.statuscode, self.message)
