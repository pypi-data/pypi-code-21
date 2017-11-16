"""
This module provides partial functionality to map between CPP3 and SMP XML formats.

Main Features and Limitations:

- A CPP can provide more than one Party Identifier for a Party.  In the mapping, a separate ServiceGroup
and related SignedServiceMetadata set is created for each identifier.

- The only supported channel type is the NamedChannel, because SMP only has a "transport" attribute
value for channel configuration, so we can't provide any other configuration information.

- Only receive action bindings are mapped as SMP only has provides information on receiving capabilities.

- Only Push bindings are supported, as an SMP receiver has to specify is a mandatory EndpointURI element.

- The SMP certificate is filled using the X509 content of the encryption certificate, if the channel
specifies one.  This reflects the real life use of this SMP field in e-SENS.  If none is specified, the
first reference to a signing certificate in the channel or in the CPP is used, although this is
probably an error in the specification.
https://lists.oasis-open.org/archives/bdxr/201705/msg00003.html

- The document scheme is cppa-docid-qns,  which indicates the document identifier value is derived from
the Action header,  not from the payload profile.  This is for now the only supported scheme.

- No checks if the PKI assumed for the SMP domain matches any CPP trust anchors.

- Currently only CPP to SMP is supported.  The reverse would be very similar, but not done

- Also, the restriction to NamedChannel means that the CPP is for the receiving party and there is
no separate C3 receiver.  A future version of this module may support the CPPA3 DelegationChannel.

- Currently, the SignedServiceMetadata does not contain a Signature.  Use the xmlsign library or similar
to add it.

"""

_NSMAP = {'cppa': 'http://docs.oasis-open.org/ebcore/ns/cppa/v3.0',
         'smp': 'http://docs.oasis-open.org/bdxr/ns/SMP/2016/05',
         'ds': 'http://www.w3.org/2000/09/xmldsig#'}

_SMPNSMAP = {'smp': 'http://docs.oasis-open.org/bdxr/ns/SMP/2016/05',
             'ds': 'http://www.w3.org/2000/09/xmldsig#'}

import lxml, urllib, logging, string

def cpp2smp(cpp, url_prefix, doc_id_schema='cppa-docid-qns'):
    """
    @param cpp: an lxml.etree.Element for a CPP
    @param url_prefix:  the URL prefix (including the domain name of the SMP server at which
    the CPP is to be deployed).
    @return: a tuple (ServiceGroup, SignedServiceMetadataSet), where ServiceGroup is an
      SMP ServiceGroup etree and SignedServiceMetadataSet is a dictionary of SignedServiceMetadata
      etrees keyed on metadata references
    """
    cpp_result_set = []
    for partyid_el in cpp.xpath(
        'descendant::cppa:PartyId',
        namespaces=_NSMAP
    ):
        this_partyid_result_set = []
        service_group_el = lxml.etree.Element(smp('ServiceGroup'), nsmap=_SMPNSMAP)
        this_partyid_result_set.append(service_group_el)
        partyid, scheme = determine_participant_identifier(service_group_el, partyid_el)
        smrc_el = lxml.etree.SubElement(service_group_el,
                                        smp('ServiceMetadataReferenceCollection'))
        if doc_id_schema == 'cppa-docid-qns':
            for action in enumerate_actions(cpp):
                add_service_metadata_reference(smrc_el, url_prefix, partyid, scheme, doc_id_schema, action)
                create_signed_service_metadata(cpp, this_partyid_result_set, partyid_el, doc_id_schema, action)
        else:
            raise Exception('Unsupported doc_id_schema: {}'.format(doc_id_schema))
        cpp_result_set.append(this_partyid_result_set)
    return cpp_result_set


def smp2cpp(servicegroup_el, signedservicemetadata_set):
    pass

def determine_participant_identifier(parent_el, partyid_el):
    participant_identifier_el = lxml.etree.SubElement(parent_el,
                                                      smp('ParticipantIdentifier'))
    partyid = partyid_el.text
    participant_identifier_el.text = partyid
    if 'type' in partyid_el.attrib:
        scheme = partyid_el.get('type')
        participant_identifier_el.set('scheme',scheme)
        return partyid, scheme
    else:
        return partyid, None

def enumerate_actions(cpp):
    return set(cpp.xpath('descendant::cppa:ActionBinding[@sendOrReceive="receive"]/@action',
                         namespaces=_NSMAP))

def add_service_metadata_reference(smrc_el, url_prefix, partyid, scheme, doc_id_scheme, document_type):
    smr_el = lxml.etree.SubElement(smrc_el, smp('ServiceMetadataReference'))

    url = '{}{}/services/{}{}{}'.format(url_prefix,
                                        urllib.quote(absolute_party_id(partyid, scheme)),
                                        urllib.quote(doc_id_scheme),
                                        urllib.quote('::'),
                                        urllib.quote(document_type))
    smr_el.set('href', url)

def create_signed_service_metadata(cpp, result_set, partyid_el, doc_id_scheme, document_type, docmap=None):
    signed_service_metadata_el = lxml.etree.Element(smp('SignedServiceMetadata'), nsmap=_SMPNSMAP)
    service_metadata_el = lxml.etree.SubElement(signed_service_metadata_el,
                                                smp('ServiceMetadata'), nsmap=_SMPNSMAP)
    service_info_el = lxml.etree.SubElement(service_metadata_el,
                                            smp('ServiceInformation'))
    determine_participant_identifier(service_info_el, partyid_el)
    document_identifier(service_info_el, doc_id_scheme, document_type)
    process_list_el = lxml.etree.SubElement(service_info_el, smp('ProcessList'))
    if doc_id_scheme == 'cppa-docid-qns':
        for service_binding_el in enumerate_services_for_action(cpp, document_type):
            description = service_binding_el.xpath(
                'child::cppa:Description/text()',
                namespaces=_NSMAP
            )[0]
            process_el = lxml.etree.SubElement(process_list_el, smp('Process'))
            process_identifier(service_binding_el, process_el)
            service_endpoint_list_el = lxml.etree.SubElement(process_el,
                                                             smp('ServiceEndpointList'))
            channels_to_endpoint(cpp, service_binding_el, doc_id_scheme, document_type, service_endpoint_list_el,
                                 description, docmap)
    result_set.append(signed_service_metadata_el)

def enumerate_services_for_action(cpp, action):
    return cpp.xpath(
        'descendant::cppa:ServiceBinding[cppa:ActionBinding[@sendOrReceive="receive" and @action="{}"]]'.format(action),
        namespaces=_NSMAP
    )

def channels_to_endpoint(cpp, service_binding_el, doc_id_scheme, document_type, service_endpoint_list_el, description,
                         docmap):
    if doc_id_scheme == 'cppa-docid-qns':
        logging.debug('Listing channels for document {} scheme {}'.format(document_type, doc_id_scheme))
        xpath_query = 'child::cppa:ActionBinding[@sendOrReceive="receive" and @action="{}"]'
    for action_binding_el in service_binding_el.xpath(
        xpath_query.format(document_type),
        namespaces=_NSMAP
    ):
        for channelid in action_binding_el.xpath(
            'child::cppa:ChannelId/text()',
            namespaces=_NSMAP
        ):
            try:
                # the following will fail if the referenced channel is not a NamedChannel.
                # in that case,  we skip the channel and hope there is another ChannelId that
                # works
                channel_el = cpp.xpath(
                    'descendant::cppa:NamedChannel[@id="{}"]'.format(channelid),
                    namespaces=_NSMAP
                )[0]
                channel_name = channel_el.xpath(
                    'child::cppa:ChannelName/text()',
                    namespaces=_NSMAP
                )[0]
                endpoint_el = lxml.etree.SubElement(service_endpoint_list_el, smp('Endpoint'), transportProfile=channel_name)
                transportid = channel_el.get('transport')
                transport_el = cpp.xpath(
                    'cppa:*[@id="{}"]'.format(transportid),
                    namespaces=_NSMAP
                )[0]
                endpoint_uri = lxml.etree.SubElement(endpoint_el, smp('EndpointURI'))
                endpoint_uri.text = transport_el.xpath(
                    'child::cppa:Endpoint',
                    namespaces=_NSMAP
                )[0].text
                cert_el = lxml.etree.SubElement(endpoint_el, smp('Certificate'))
                try:
                    #Use the smp:Certificate to contain the ENCRYPTION certificate;  reflects e-SENS practice.
                    enc_cert_ref = channel_el.xpath(
                        'child::cppa:EncryptionCertificateRef/@certId',
                        namespaces=_NSMAP
                    )[0]
                    enc_cert_x509 = cpp.xpath(
                        'descendant::cppa:Certificate[@id="{}"]//ds:X509Certificate/text()'.format(enc_cert_ref),
                        namespaces=_NSMAP
                    )[0]
                    cert_el.text = enc_cert_x509
                except:
                    #Else see if there is a signing certificate reference. Doesn't make sense normally for
                    #received actions ...
                    try:
                        cert_ref = channel_el.xpath(
                            'child::cppa:SigningCertificateRef/@certId',
                            namespaces=_NSMAP
                        )[0]
                        cert_x509 = channel_el.xpath(
                            'child::cppa:Certificate[@id="{}"]//ds:X509Certificate/text()'.format(cert_ref),
                            namespaces=_NSMAP
                        )[0]
                        cert_el.text = cert_x509
                    except:
                        #Else pick the first signing certificate referenced. At least satifies the XSD ..
                        cert_ref = cpp.xpath(
                            'descendant::cppa:SigningCertificateRef/@certId',
                            namespaces=_NSMAP
                        )[0]
                        cert_x509 = cpp.xpath(
                            'descendant::cppa:Certificate[@id="{}"]//ds:X509Certificate/text()'.format(cert_ref),
                            namespaces=_NSMAP
                        )[0]
                        cert_el.text = enc_cert_x509

                add_activation_date(cpp, service_binding_el, endpoint_el)
                add_expiration_date(cpp, service_binding_el, endpoint_el)
                desc_el = lxml.etree.SubElement(endpoint_el, smp('ServiceDescription'))
                desc_el.text = description
                tech_contact_uri_el = lxml.etree.SubElement(endpoint_el, smp('TechnicalContactUrl'))
                tech_contact_uri = string.join(cpp.xpath(
                    'descendant::cppa:PartyContact/cppa:Email/text() | descendant::cppa:PartyContact/cppa:URICommunication/text()',
                    namespaces=_NSMAP))
                tech_contact_uri_el.text = tech_contact_uri
            except:
                logging.info('Exception processing channel {}'.format(channelid))

def add_activation_date(cpp, service_binding_el, endpoint_el):
    local_activation_date_l = service_binding_el.xpath(
        'cppa:ActivationDate/text()',
        namespaces=_NSMAP
    )
    if len(local_activation_date_l) > 0:
        activation_date = lxml.etree.SubElement(endpoint_el, smp('ActivationDate'))
        activation_date.text = local_activation_date_l[0]
    else:
        logging.debug('No local ActivationDate')
        cpp_activation_date_l = cpp.xpath(
            'cppa:ProfileInfo/cppa:ActivationDate/text()',
            namespaces=_NSMAP
        )
        if len(cpp_activation_date_l) > 0:
            activation_date = lxml.etree.SubElement(endpoint_el, smp('ActivationDate'))
            activation_date.text = cpp_activation_date_l[0]
        else:
            logging.debug('No CPP ActivationDate')

def add_expiration_date(cpp, service_binding_el, endpoint_el):
    local_expiration_date_l = service_binding_el.xpath(
        'cppa:ExpirationDate/text()',
        namespaces=_NSMAP
    )
    if len(local_expiration_date_l) > 0:
        activation_date = lxml.etree.SubElement(endpoint_el, smp('ExpirationDate'))
        activation_date.text = local_expiration_date_l[0]
    else:
        logging.debug('No local ExpirationDate')
        cpp_expiration_date_l = cpp.xpath(
            'cppa:ProfileInfo/cppa:ExpirationDate/text()',
            namespaces=_NSMAP
        )
        if len(cpp_expiration_date_l) > 0:
            expiration_date = lxml.etree.SubElement(endpoint_el, smp('ExpirationDate'))
            expiration_date.text = cpp_expiration_date_l[0]
        else:
            logging.debug('No CPP ExpirationDate')



def absolute_party_id(partyid, scheme):
    if scheme != None:
        return '{}:{}'.format(scheme, partyid)
    else:
        return partyid

def document_identifier(parent_el, doc_id_scheme, document_type):
    document_identifier_el = lxml.etree.SubElement(parent_el, smp('DocumentIdentifier'),
                                                   scheme=doc_id_scheme)
    document_identifier_el.text = document_type

def process_identifier(service_binding_el, process_el):
    service_el = service_binding_el.xpath('child::cppa:Service',
                                       namespaces=_NSMAP)[0]
    process_identifier_el = lxml.etree.SubElement(process_el, smp('ProcessIdentifier'))

    if 'type' in service_el.attrib:
        process_identifier_el.set('scheme', service_el.get('type'))
    process_identifier_el.text = service_el.text
    logging.debug("Setting process {}".format(service_el.text))

def smp(el):
    return '{{{}}}{}'.format(_NSMAP['smp'],el)
