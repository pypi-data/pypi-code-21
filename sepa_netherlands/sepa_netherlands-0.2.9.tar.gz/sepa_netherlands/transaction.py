import requests
from lxml import etree
from sepa import builder, signer
from .util import xml_to_dict

def request_transaction(client, issuer_id, language, entrance_code, expiration_period, mandate_document):
    # Create XML message
    root = etree.Element('AcquirerTrxReq', nsmap={
        None: 'http://www.betaalvereniging.nl/iDx/messages/Merchant-Acquirer/1.0.0'
    })
    root.attrib['productID'] = 'NL:BVN:eMandatesCore:1.0'
    root.attrib['version'] = '1.0.0'
    root.append(client._timestamp())
    root.append(client._merchant(True))

    issuer = etree.Element('Issuer')
    issuer.append(client._element('issuerID', issuer_id))
    root.append(issuer)

    transaction = etree.Element('Transaction')
    transaction.append(client._element('language', language))
    transaction.append(client._element('entranceCode', entrance_code))
    transaction.append(client._element('expirationPeriod', expiration_period))

    container = etree.Element('container')
    transaction.append(container)
    container.append(mandate_document)
    root.append(transaction)

    # Sign XML message and convert it to string
    data = client.sign_to_string(root)

    print(data)

    # Post signed XML message to directory endpoint
    r = requests.post(client.transaction_url, data=data)

    if r.status_code >= 200 and r.status_code <= 399:
        # Parse XML response
        xml_result = etree.fromstring(r.text.encode('utf8'))
        print(etree.tostring(xml_result))

        # Verify response
        if not client.verify(xml_result):
            return {'is_error': True, 'error_code': 'SO100', 'error_message': 'Invalid response', 'error_detail': 'Signature verification failed'}

        # Convert XML object to dictionary
        result = xml_to_dict(xml_result)

        response = {}

        # TODO: parse result

        return response
    else:
        # An HTTP error occurred
        return {'is_error': True, 'error_code': 'SO100', 'error_message': 'An unknown error occurred', 'error_detail': 'HTTP request returned error code'}
