import typing
from pyEchosign.exceptions.internal import MissingAgreement

if typing.TYPE_CHECKING:
    from pyEchosign import Agreement

__all__ = ['User']


class User(object):
    """ Maps to the DisplayUserInfo provided by Echosign for agreements fetched in bulk.
    Provides additional attributes to facilitate sending documents to recipients, such as Security Options.

    Attributes:
        agreement (Agreement): The :class:`Agreement <pyEchosign.classes.agreement.Agreement>` to be associated with
            this User
        authentication_method (str): A "The authentication method for the recipients to have access to view and
            sign the document" (Echosign API Docs). Available options are 'NONE' (string),
            'INHERITED_FROM_DOCUMENT' or 'PASSWORD' or 'WEB_IDENTITY' or 'KBA' or 'PHONE'.
        password (str): Optional - "The password required for the recipient to view and sign the document"
        signing_url (str): If this recipient is associated with an
            :class:`Agreement <pyEchosign.classes.agreement.Agreement>` this is the URL that the user can visit to
            complete/sign the agreement.

     """
    def __init__(self, email, **kwargs):
        # type: (str) -> None
        self.authentication_method = kwargs.get('authentication_method', 'NONE')
        self.password = kwargs.get('password', None)
        self.agreement = kwargs.get('agreement', None)  # type: Agreement
        self._signing_url = kwargs.get('signing_url', None)

        self.email = email
        self.company = kwargs.pop('company', None)
        self.full_name = kwargs.pop('full_name', None)

    def __str__(self):
        if self.full_name:
            return self.full_name
        else:
            return self.email

    @classmethod
    def json_to_user(cls, user_data, agreement=None):
        email = user_data.get('email')
        name = user_data.get('fullName', None)
        company = user_data.get('company', None)
        user = User(email, full_name=name, company=company, agreement=agreement)
        return user

    @classmethod
    def json_to_users(cls, user_data, agreement=None):
        return [cls.json_to_user(data, agreement) for data in user_data]

    @property
    def signing_url(self):
        if self._signing_url is None:
            if self.agreement is None:
                raise MissingAgreement('An agreement must be tied to this User in order to retrieve the signing URL')
            self.agreement.get_signing_urls()

        return self._signing_url


class RecipientInfo(object):
    email = None
    fax = None
    role = None
    private_message = None
    signing_order = None

    # Acceptable Options for role
    SIGNER = 'SIGNER'
    APPROVER = 'APPROVER'
    ACCEPTOR = 'ACCEPTOR'
    FORM_FILLER = 'FORM_FILLER'
    CERTIFIED_RECIPIENT = 'CERTIFIED_RECIPIENT'
    DELEGATE_TO_SIGNER = 'DELEGATE_TO_SIGNER'
    DELEGATE_TO_APPROVER = 'DELEGATE_TO_APPROVER'
    DELEGATE_TO_ACCEPTOR = 'DELEGATE_TO_ACCEPTOR'
    DELEGATE_TO_FORM_FILLER = 'DELEGATE_TO_FORM_FILLER'
    DELEGATE_TO_CERTIFIED_RECIPIENT = 'DELEGATE_TO_CERTIFIED_RECIPIENT'