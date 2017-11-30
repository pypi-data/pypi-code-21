'''Module containing custom errors'''
import requests

from . import util

class GencoveClientError(Exception): 
    '''All errors thrown in this API inherit from this class'''
    pass

class URLDataIncompleteError(GencoveClientError):
    '''Thrown when there is not enough data to generate a URL'''
    pass

class NotLoggedInError(GencoveClientError):
    '''Thrown when user attempts an action requiring login, but is not logged 
    in'''
    pass

class NoApiKeyError(GencoveClientError):
    '''Thrown when user attempts an action requiring auth, but does not have
    an API key'''
    pass

class NoAuthError(GencoveClientError):
    '''Thrown when user attempts an action requiring auth, but does not have
    any credentials available'''
    pass

class NoJSONInResponseError(ValueError, GencoveClientError):
    '''Thrown when HTTP response should contain JSON, but it does not

    Although technically a ValueError, using it in this case is slightly 
        ambiguous. NoJSONInResponseError provides more context (the response).

    Args:
        message (str): message of original exception
        response (requests.Response): HTTP response that could not be parsed
    '''
    def __init__(self, message, response):
        super(NoJSONInResponseError, self).__init__('Error: \'{}\' with HTTP status code: \'{}\' and text \'{}\''.format(message, response.status_code, response.text))

        self.message_original = message
        self.response = response

class NoDataError(GencoveClientError):
    '''Thrown when an api endpoint has flexible number of parameters, but none 
    are provided'''
    pass

class HTTPError(requests.HTTPError, GencoveClientError):
    '''Thrown on HTTP Error, provides more info in message string so there
    is no need to dig into requests.HTTPError.response.text'''
    def __init__(self, *args, **kwargs):
        more = None
        if 'response' in kwargs:
            more = util.extract_backend_message(kwargs['response'])
            
        new_args = args
        if len(args) > 0 and more:
            new_args_list = list(args)
            new_args_list[0] = new_args_list[0]+" with message: "+more
            new_args = tuple(new_args_list)

        super(HTTPError, self).__init__(*new_args, **kwargs)

class MemberAndExternalIdsProvided(GencoveClientError):
    '''Thrown when user attempts to get raw data by providing both member ids
    and external ids'''
    pass