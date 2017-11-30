from rest_framework import status
from base_exception import GenericException

class LoginError(GenericException):
    HTTP_STATUS = status.HTTP_403_FORBIDDEN # NOT FOUND
        
class RegisterError(GenericException):
    HTTP_STATUS = status.HTTP_412_PRECONDITION_FAILED

class DuplicateError(GenericException):
    HTTP_STATUS = status.HTTP_412_PRECONDITION_FAILED
