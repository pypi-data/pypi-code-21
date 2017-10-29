from pyEchosign.exceptions.echosign import BaseEchosignException


class ApiError(BaseEchosignException):
    base_echosign_error = 'Received an error HTTP response code from the Echosign API'


class MissingAgreement(BaseEchosignException):
    base_echosign_error = 'An agreement is required'
