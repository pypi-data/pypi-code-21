from rest_framework import status



from base_exception import GenericException

class ResourceNotFound(GenericException):
    HTTP_STATUS = status.HTTP_404_NOT_FOUND # NOT FOUND

class NotImplementedException(GenericException):
    '''Cause NotImplemented is already been used!'''
    HTTP_STATUS = status.HTTP_501_NOT_IMPLEMENTED

class PermissionError(GenericException):
    HTTP_STATUS = status.HTTP_403_FORBIDDEN # NOT FOUND

class PermissionAdminError(GenericException):
    HTTP_STATUS = status.HTTP_403_FORBIDDEN # NOT FOUND

class InputValueError(GenericException):
    HTTP_STATUS = status.HTTP_412_PRECONDITION_FAILED
    

class RestSerializerError(InputValueError):
    HTTP_STATUS = status.HTTP_412_PRECONDITION_FAILED
    

class ModelValidationError(InputValueError):
    HTTP_STATUS = status.HTTP_412_PRECONDITION_FAILED

