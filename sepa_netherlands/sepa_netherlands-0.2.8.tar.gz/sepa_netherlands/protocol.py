from datetime import datetime
from lxml import etree
from sepa import signer

from .directory import request_directory
from .transaction import request_transaction

class Client:
    def __init__(self, id, return_url, directory_url, status_url, transaction_url, key, cert, passphrase, fingerprint, verification_cert, sub_id='0'):
        self.id = id
        self.return_url = return_url
        self.directory_url = directory_url
        self.status_url = status_url
        self.transaction_url = transaction_url
        self.key = key
        self.cert = cert
        self.passphrase = passphrase.encode('utf-8')
        self.fingerprint = fingerprint.replace(':', '').upper()
        self.verification_cert = verification_cert
        self.sub_id = sub_id

    def request_directory(self):
        return request_directory(self)

    def request_transaction(self, **kwargs):
        return request_transaction(self, **kwargs)

    def sign(self, root):
        return signer.sign(root, key=self.key, cert=self.cert, passphrase=self.passphrase, key_name=self.fingerprint)

    def sign_to_string(self, root):
        return self._string(self.sign(root))

    def verify(self, root):
        return self.verification_cert is None or signer.verify(root, x509_cert=self.verification_cert)

    def _string(self, tree):
        return etree.tostring(tree, xml_declaration=True, encoding='UTF-8')

    def _element(self, tag, text, **kwargs):
        element = etree.Element(tag, **kwargs)
        element.text = text
        return element

    def _timestamp(self):
        timestamp = datetime.now().isoformat()
        return self._element('createDateTimestamp', timestamp[:timestamp.rfind('.')] + 'Z')

    def _merchant(self, include_return=True):
        element = etree.Element('Merchant')
        element.append(self._element('merchantID', self.id))
        element.append(self._element('subID', self.sub_id))
        if include_return:
            element.append(self._element('merchantReturnURL', self.return_url))

        # return self._sort(element, ['merchantID', 'subID', 'merchantReturnURL'])
        return element

    def _sort(self, element, sorting):
        element[:] = sorted(element, key=lambda element: sorting.index(element.tag))
        return element
