import logging
from io import IOBase, FileIO, BytesIO
from typing import TYPE_CHECKING, Union

import arrow
import requests

from pyEchosign.exceptions.internal import ApiError
from pyEchosign.utils.handle_response import check_error, response_success
from pyEchosign.utils.request_parameters import get_headers

log = logging.getLogger('pyEchosign.' + __name__)
if TYPE_CHECKING:
    from .account import EchosignAccount

__all__ = ['TransientDocument']


class TransientDocument(object):
    """
    A document which can be used in Agreements - is deleted by Echosign after 7 days. The TransientDocument is created
    in Echosign on instantiation.

    Args:
        account: The :class:`EchosignAccount <pyEchosign.classes.account.EchosignAccount>`
            to be associated with this document
        file_name (str): The name of the file
        file: The actual file object to upload to Echosign, accepts a stream of bytes.
        mime_type: (optional) The MIME type of the file. Echosign will infer the type from the file extension if not
            provided.
    
    Attributes:
        file_name: The name of the file
        file: The actual file object to upload to Echosign
        mime_type: The MIME type of the file
        document_id: The ID provided by Echosign, used to reference it in creating agreements
        expiration_date: The date Echosign will delete this document
            (not provided by Echosign, calculated for convenience)
    """
    def __init__(self, account, file_name, file, mime_type=None):
        # type: (EchosignAccount, str, Union[IOBase, FileIO, BytesIO], str) -> None
        self.file_name = file_name
        self.file = file
        self.mime_type = mime_type

        self.document_id = None
        self.expiration_date = None

        # With file data provided, make request to Echosign API for transient document
        url = account.api_access_point + 'transientDocuments'

        # Create post_data
        file_tuple = (file_name, file)
        # Only add the mime type if provided
        if mime_type is not None:
            file_tuple = file_tuple + (mime_type, )

        files = dict(File=file_tuple)
        r = requests.post(url, headers=get_headers(account.access_token, content_type=None), files=files)

        if response_success(r):
            log.debug('Request to create document {} successful.'.format(self.file_name))
            response_data = r.json()
            self.document_id = response_data.get('transientDocumentId', None)
            # If there was no document ID, something went wrong
            if self.document_id is None:
                log.error('Did not receive a transientDocumentId from Echosign. Received: {}'.format(r.content))
                raise ApiError('Did not receive a Transient Document ID from Echosign')
            else:
                today = arrow.now()
                # Document will expire in 7 days from creation
                self.expiration_date = today.replace(days=+7).datetime
        else:
            try:
                log.error('Error encountered creating document {}. Received message: {}'.
                          format(self.file_name, r.content))
            finally:
                check_error(r)

    def __str__(self):
        return self.file_name


class AgreementDocument(object):
    """ Represents a document used in an Agreement.

        Attributes:
            echosign_id: The ID of the Document which can be used to retrieve its file stream
            mime_type: The MIME type of the document
            name: The name of the document
            page_count: The number of pages in the document
            supporting_document: Whether or not this document is a "supporting document" as specified by the API
            field_name: If a supporting document, what the name is of the supporting document field

    """
    def __init__(self, echosign_id, mime_type, name, page_count, supporting_document=False, field_name=None):
        # type: (str, str, str, int, bool, str) -> None
        self.echosign_id = echosign_id
        self.mime_type = mime_type
        self.name = name
        self.page_count = page_count

        self.supporting_document = supporting_document
        self.field_name = field_name

    def __str__(self):
        return 'AgreementDocument: {}'.format(self.name)

    def __repr__(self):
        return 'AgreementDocument: {}'.format(self.name)

