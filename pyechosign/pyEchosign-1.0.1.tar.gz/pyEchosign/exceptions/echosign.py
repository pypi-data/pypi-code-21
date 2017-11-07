class BaseEchosignException(Exception):
    base_echosign_error = None

    def __init__(self, message=None, *args, **kwargs):
        if message is None:
            self.message = self.base_echosign_error
        elif message is not None and self.base_echosign_error is None:
            self.message = message
        else:
            self.message = '{} - {}'.format(message, self.base_echosign_error)

        super(BaseEchosignException, self).__init__(message, *args, **kwargs)


class InvalidMultipart(BaseEchosignException, ValueError):
    base_echosign_error = 'An invalid multipart was specified.'


class AccessTokenError(BaseEchosignException, ValueError):
    base_echosign_error = 'Access token not provided or invalid'


class FileTooLargeError(BaseEchosignException):
    pass


class PermissionDenied(BaseEchosignException):
    base_echosign_error = 'The API caller do not have the permission to execute this operation.'


class UnsupportedMediaError(BaseEchosignException):
    base_echosign_error = 'Content type was not provided or is not supported.'


class ProcessingError(BaseEchosignException):
    base_echosign_error = ('The transient document was deleted from the system because Adobe Sign could not '
                           'process the document. This can happen if uploaded document contains scripts, macros or '
                           'Visual Basic code. You may wish to inspect your document for these elements, remove them, '
                           'and try uploading the document again.')


class ResourceVirusDetected(ProcessingError):
    base_echosign_error = 'The transient document was deleted because a virus was detected in the file.'
