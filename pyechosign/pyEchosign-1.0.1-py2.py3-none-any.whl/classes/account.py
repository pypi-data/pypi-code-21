import logging
from typing import List

import requests

from pyEchosign.classes.agreement import Agreement
from pyEchosign.classes.library_document import LibraryDocument
from pyEchosign.utils import endpoints
from pyEchosign.utils.handle_response import check_error
from pyEchosign.utils.request_parameters import get_headers

log = logging.getLogger('pyOutlook - {}'.format(__name__))
__all__ = ['EchosignAccount']


class EchosignAccount(object):
    """ Saves OAuth Information for connecting to Echosign
    
    Attributes:
        access_token: The OAuth Access token to use for authenticating to Echosign
        user_id: The ID of the user to specify as the API caller, if not provided the caller is inferred from the token
        user_email: The email of the user to specify as the API caller, if not provided the caller is inferred from the token
        api_access_point: The API endpoint used as a base for all API calls
    """
    def __init__(self, access_token, **kwargs):
        # type: (str) -> None
        self.access_token = access_token
        self.user_id = kwargs.pop('user_id', None)
        self.user_email = kwargs.pop('user_email', None)

        log.debug('EchosignAccount instantiated. Requesting base_uris from API...')
        headers = {'Access-Token': access_token}
        response = requests.get(endpoints.BASE_URIS, headers=headers)
        response_body = response.json()
        log.debug('Received status code {} from Echosign API'.format(response.status_code))
        self.api_access_point = response_body.get('api_access_point') + endpoints.API_URL_EXTENSION

    access_token = None

    def headers(self, content_type='application/json'):
        """ Return headers using account information

        Args:
            content_type: The Content-Type to use in the request headers. Defaults to application/json

        Returns: A dict of headers

        """
        return get_headers(self.access_token, self.user_email, content_type)

    def get_agreements(self, query=None):
        # type: (str) -> List[Agreement]
        """ Gets all agreements for the EchosignAccount

        Keyword Args:
            query: (str) A search query to filter results by
        
        Returns: A list of :class:`Agreement <pyEchosign.classes.agreement.Agreement>` objects
        """
        url = self.api_access_point + 'agreements'
        params = dict()

        if query is not None:
            params.update({'query': query})

        r = requests.get(url, headers=get_headers(self.access_token), params=params)
        check_error(r)
        response_body = r.json()
        return Agreement.json_to_agreements(self, response_body)

    def get_library_documents(self):
        """ Gets all Library Documents for the EchosignAccount

        Returns: A list of :class:`Agreement <pyEchosign.classes.library_document.LibraryDocument>` objects
        """
        url = self.api_access_point + 'libraryDocuments'
        headers = get_headers(self.access_token)
        r = requests.get(url, headers=headers)
        response_data = r.json()

        check_error(r)

        return LibraryDocument.json_to_agreements(self, response_data)

