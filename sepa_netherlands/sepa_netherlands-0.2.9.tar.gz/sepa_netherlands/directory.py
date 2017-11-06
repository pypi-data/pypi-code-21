import requests
from lxml import etree
from .util import xml_to_dict

def request_directory(client):
    # Create XML message
    root = etree.Element('DirectoryReq', nsmap={
        None: 'http://www.betaalvereniging.nl/iDx/messages/Merchant-Acquirer/1.0.0'
    })
    root.attrib['productID'] = 'NL:BVN:eMandatesCore:1.0'
    root.attrib['version'] = '1.0.0'
    root.append(client._timestamp())
    root.append(client._merchant(False))

    # Sign XML message and convert it to string
    data = client.sign_to_string(root)

    # Post signed XML message to directory endpoint
    r = requests.post(client.directory_url, data=data)

    if r.status_code >= 200 and r.status_code <= 399:
        # Parse XML response
        xml_result = etree.fromstring(r.text.encode('utf8'))

        # Verify response
        if not client.verify(xml_result):
            return {'is_error': True, 'error_code': 'SO100', 'error_message': 'Invalid response', 'error_detail': 'Signature verification failed'}

        # Convert XML object to dictionary
        result = xml_to_dict(xml_result)

        print(r.text.encode('utf8'))

        # Check for error
        if hasattr(result, 'error'):
            r = result['error']
            r['is_error'] = True
            return r

        # Parse response
        response = {
            'is_error': False,
            'timestamp': result['create_date_timestamp'],
            'acquirer_id': result['acquirer']['acquirer_id'],
            'countries': result['directory']['country']
        }

        print(response['countries'])

        if not isinstance(response['countries'], list):
            response['countries'] = [response['countries']]

        for country in response['countries']:
            country['name'] = country['country_names']
            del country['country_names']

            if not isinstance(country['issuer'], list):
                country['issuers'] = [country['issuer']]
            else:
                country['issuers'] = country['issuer']

            del country['issuer']

        return response
    else:
        # An HTTP error occurred
        return {'is_error': True, 'error_code': 'SO100', 'error_message': 'An unknown error occurred', 'error_detail': 'HTTP request returned error code'}
