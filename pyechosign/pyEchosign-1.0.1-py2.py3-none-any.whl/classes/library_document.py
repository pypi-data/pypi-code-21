from typing import TYPE_CHECKING

import arrow
import requests
from io import BytesIO

from pyEchosign.utils.request_parameters import get_headers
from pyEchosign.utils.handle_response import check_error

if TYPE_CHECKING:
    from .account import EchosignAccount


class LibraryDocument(object):
    """
    Represents a Library Document in Echosign. When pulling all Library Documents, only the echosign_id, template_type,
    modified_date, name, and scope are available. Accessing all other attributes results in an HTTP request to pull the
    full document information.

    Attributes:
        account (EchosignAccount): An instance of :class:`EchosignAccount <pyEchosign.classes.account.EchosignAccount>`.
         All Agreement actions will be conducted under this account.
        echosign_id (str): The ID for this document in Echosign
        document (bool): If this LibraryDocument is a document in Echosign
        form_field_layer (bool): If this LibraryDocument is a form field layer
        modified_date (datetime): The day on which the LibraryDocument was last modified
        name (str): The name of the LibraryDocument in Echosign
        scope (str): The visibility of this LibraryDocument, either 'PERSONAL', 'SHARED', or 'GLOBAL"
    """

    def __init__(self, account, echosign_id, template_type, name, modified_date, scope):
        # type: (EchosignAccount, str, list, str, str, str) -> None
        self.account = account
        self.echosign_id = echosign_id
        if 'DOCUMENT' in template_type:
            self.document = True
        if 'FORM_FIELD_LAYER' in template_type:
            self.form_field_layer = True
        self.name = name
        date = arrow.get(modified_date)
        self.modified_date = date.datetime
        self.scope = scope
        self.fully_retrieved = False
        self.document = False
        self.form_field_layer = False

        # The following are only available after retrieving the LibraryDocument specifically
        self._events = None
        self._latest_version_id = None
        self._locale = None
        self._participants = None
        self._status = None
        self._message = None
        self._security_options = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    PERSONAL = 'PERSONAL'
    SHARED = 'SHARED'
    GLOBAL = 'GLOBAL'
    scope = None

    @classmethod
    def json_to_agreement(cls, account, json_data):
        echosign_id = json_data.get('libraryDocumentId')
        template_type = json_data.get('libraryTemplateTypes')
        modified_date = json_data.get('modifiedDate')
        name = json_data.get('name')
        scope = json_data.get('scope')
        return LibraryDocument(account, echosign_id, template_type, name, modified_date, scope)

    @classmethod
    def json_to_agreements(cls, account, json_data):
        response_data = json_data.get('libraryDocumentList')
        return [cls.json_to_agreement(account, doc_data) for doc_data in response_data]

    @property
    def locale(self):
        if not self.fully_retrieved:
            self.retrieve_complete_document()
        return self._locale

    @property
    def audit_trail_file(self):
        # type: () -> BytesIO
        """ The PDF file of the audit for this Library Document."""
        endpoint = '{}libraryDocuments/{}/auditTrail'.format(self.account.api_access_point, self.echosign_id)

        response = requests.get(endpoint, headers=get_headers(self.account.access_token))
        check_error(response)

        return BytesIO(response.content)

    def retrieve_complete_document(self):
        """ Retrieves the remaining data for the LibraryDocument, such as locale, status, and security options. """
        url = self.account.api_access_point + 'libraryDocuments/{}'.format(self.echosign_id)
        headers = get_headers(self.account.access_token)
        r = requests.get(url, headers=headers)

        check_error(r)

        response_data = r.json()
        self._locale = response_data.get('locale')
        self._status = response_data.get('status')
        self._security_options = response_data.get('securityOptions')
        self.fully_retrieved = True

    def delete(self):
        """ Deletes the LibraryDocument from Echosign. It will not be visible on the Manage page. """
        url = self.account.api_access_point + 'libraryDocuments/{}'.format(self.echosign_id)
        headers = get_headers(self.account.access_token)
        r = requests.delete(url, headers=headers)
        check_error(r)
