"""
Module defining SAML2 Service Provider metadata utility functions

Copyright (C) 2017 ERT Inc.
"""
__author__ = "Brandon J. Van Vaerenbergh <brandon.vanvaerenbergh@noaa.gov>"

import json

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from onelogin.saml2.errors import OneLogin_Saml2_Error

class EntityDescriptorSettingsError(OneLogin_Saml2_Error):
    # Raised on EntityDescriptor metadata generation failure
    pass

class EntityDescriptorValidationError(ValueError):
    # Raised on EntityDescriptor metadata XML validation failure
    pass

def get_entity_descriptor(settings_path, cert_path, key_path):
    """
    Return Service Provider metadata & content type,as tuple of Strings

    Keyword Parameters:
    settings_path  -- String, representing the path to your OneLogin
      settings.json file
    cert_path  -- String,representing path to the OpenSSL PEM formatted
      certificate file identifying the server which uses remote SSO
    key_path  -- String, representing path to the OpenSSL private key
      file used to sign cert_path certifiate file

    Exceptions:
    EntityDescriptorSettingsError  -- raised when contents of the
      settings_path file are invalid
    EntityDescriptorValidationError  -- raised if settings generate XML
      with an invalid SAML2 EntityDescriptor element

    >>> from pprint import pprint
    >>> import tempfile
    >>> test_f = tempfile.NamedTemporaryFile
    >>> with test_f() as settings, test_f() as cert, test_f() as key:
    ...     settings.write(b'''{
    ...     "strict": true,
    ...     "debug": true,
    ...     "sp": {
    ...         "entityId": "https://my_server.fake_domain/saml/metadata/",
    ...         "assertionConsumerService": {
    ...             "url": "https://my_server.gov/saml/?acs",
    ...             "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    ...         },
    ...         "singleLogoutService": {
    ...             "url": "https://my_server.gov/saml/?sls",
    ...             "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    ...         },
    ...         "attributeConsumingService": {
    ...                 "serviceName": "Test Name",
    ...                 "serviceDescription": "A Test Service",
    ...                 "requestedAttributes": [
    ...                     {
    ...                         "name": "TestName",
    ...                         "isRequired": false,
    ...                         "nameFormat": "",
    ...                         "friendlyName": "",
    ...                         "attributeValue": []
    ...                     }
    ...                 ]
    ...         },
    ...         "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified",
    ...         "x509cert": "",
    ...         "privateKey": ""
    ...     },
    ...     "idp": {
    ...         "entityId": "noaa-online-idp",
    ...         "singleSignOnService": {
    ...             "url": "https://fake_sso_server.gov/sso/noaa-online-idp",
    ...             "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    ...         },
    ...         "singleLogoutService": {
    ...             "url": "https://fake_sso_server.gov/slo/noaa-online-idp",
    ...             "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    ...         },
    ...         "x509cert": "invalid_cert"
    ...     }
    ... }''') #write out 1554 bytes
    ...     settings.seek(0) #reset file object, to beginning of file
    ...     test_out = get_entity_descriptor(settings.name, cert.name, key.name)
    1554
    0
    >>> len(test_out) #validate tuple length
    2
    >>> test_out[1] #check last element
    'text/xml'
    >>> #now, check first element
    >>> pprint(test_out[0]) # doctest: +ELLIPSIS
    '<?xml version="1.0"?>\\n'
    '<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"\\n'
    '                     validUntil="...Z"\\n'
    '                     cacheDuration="PT604800S"\\n'
    '                     '
    'entityID="https://my_server.fake_domain/saml/metadata/">\\n'
    '    <md:SPSSODescriptor AuthnRequestsSigned="false" '
    'WantAssertionsSigned="false" '
    'protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">\\n'
    '        <md:SingleLogoutService '
    'Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"\\n'
    '                                Location="https://my_server.gov/saml/?sls" '
    '/>\\n'
    '        '
    '<md:NameIDFormat>urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified</md:NameIDFormat>\\n'
    '        <md:AssertionConsumerService '
    'Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"\\n'
    '                                     '
    'Location="https://my_server.gov/saml/?acs"\\n'
    '                                     index="1" />\\n'
    '        <md:AttributeConsumingService index="1">\\n'
    '            <md:ServiceName xml:lang="en">Test Name</md:ServiceName>\\n'
    '            <md:ServiceDescription xml:lang="en">A Test '
    'Service</md:ServiceDescription>\\n'
    '            <md:RequestedAttribute Name="TestName" />\\n'
    '        </md:AttributeConsumingService>\\n'
    '    </md:SPSSODescriptor>\\n'
    '\\n'
    '\\n'
    '</md:EntityDescriptor>'
    """
    fake_request = dict()
    with open(cert_path) as cert_file, open(key_path) as key_file:
        cert = cert_file.read()
        key = key_file.read()
    try:
        auth = OneLogin_Saml2_Auth(fake_request, get_settings_json(settings_path, cert, key))    
        s = auth.get_settings()
        md = s.get_sp_metadata()
        errors = s.validate_metadata(md)
        if errors:
            raise EntityDescriptorValidationError(errors)
        content_type = 'text/xml'
        return (md, content_type)
    except OneLogin_Saml2_Error as e:
        raise EntityDescriptorSettingsError(e) from e

def get_settings_json(settings_path, cert_string, key_string):
    """
    Return String, representing OneLogin SAML settings.json

    Keyword Parameters:
    settings_path  -- String, representing the path to your OneLogin
      settings.json file
    cert_path  -- String,representing path to the OpenSSL PEM formatted
      certificate file identifying the server which uses remote SSO
    key_path  -- String, representing path to the OpenSSL private key
      file used to sign cert_path certifiate file

    >>> from pprint import pprint
    >>> import tempfile
    >>> with tempfile.NamedTemporaryFile() as settings:
    ...     settings.write(b'''{
    ...     "strict": true,
    ...     "debug": true,
    ...     "sp": {
    ...         "entityId": "https://my_server.fake_domain/saml/metadata/",
    ...         "assertionConsumerService": {
    ...             "url": "https://my_server.fake_domain/saml/?acs",
    ...             "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    ...         },
    ...         "singleLogoutService": {
    ...             "url": "https://my_server.fake_domain/saml/?sls",
    ...             "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    ...         },
    ...         "attributeConsumingService": {
    ...                 "serviceName": "Test Name",
    ...                 "serviceDescription": "A Test Service",
    ...                 "requestedAttributes": [
    ...                     {
    ...                         "name": "TestName",
    ...                         "isRequired": false,
    ...                         "nameFormat": "",
    ...                         "friendlyName": "",
    ...                         "attributeValue": []
    ...                     }
    ...                 ]
    ...         },
    ...         "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified",
    ...         "x509cert": "",
    ...         "privateKey": ""
    ...     },
    ...     "idp": {
    ...         "entityId": "noaa-online-idp",
    ...         "singleSignOnService": {
    ...             "url": "https://fake.test_domain/sso/noaa-online-idp",
    ...             "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    ...         },
    ...         "singleLogoutService": {
    ...             "url": "https://fake.test_domain/slo/noaa-online-idp",
    ...             "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    ...         },
    ...         "x509cert": "invalid_cert"
    ...     }
    ... }''') #write out 1564 bytes
    ...     settings.seek(0) #reset file object, to beginning of file
    ...     test_out = get_settings_json(settings.name, 'foo', 'bar')
    1564
    0
    >>> pprint(test_out)
    {'debug': True,
     'idp': {'entityId': 'noaa-online-idp',
             'singleLogoutService': {'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
                                     'url': 'https://fake.test_domain/slo/noaa-online-idp'},
             'singleSignOnService': {'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
                                     'url': 'https://fake.test_domain/sso/noaa-online-idp'},
             'x509cert': 'invalid_cert'},
     'sp': {'NameIDFormat': 'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified',
            'assertionConsumerService': {'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
                                         'url': 'https://my_server.fake_domain/saml/?acs'},
            'attributeConsumingService': {'requestedAttributes': [{'attributeValue': [],
                                                                   'friendlyName': '',
                                                                   'isRequired': False,
                                                                   'name': 'TestName',
                                                                   'nameFormat': ''}],
                                          'serviceDescription': 'A Test Service',
                                          'serviceName': 'Test Name'},
            'entityId': 'https://my_server.fake_domain/saml/metadata/',
            'privateKey': 'bar',
            'singleLogoutService': {'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
                                    'url': 'https://my_server.fake_domain/saml/?sls'},
            'x509cert': 'foo'},
     'strict': True}
    """
    with open(settings_path) as settings_file:
        settings_string = settings_file.read()
    settings = json.loads(settings_string)
    sp = settings['sp']
    sp['x509cert'] = cert_string
    sp['privateKey'] = key_string
    return settings
