__author__ = 'pvde'

import lxml.etree
import logging

from copy import deepcopy

_NSMAP = {'cppa': 'http://docs.oasis-open.org/ebcore/ns/cppa/v3.0',
         'ds': 'http://www.w3.org/2000/09/xmldsig#',
         'xml': 'http://www.w3.org/XML/1998/namespace',
         'cppa2': 'http://www.oasis-open.org/committees/ebxml-cppa/schema/cpp-cpa-2_0.xsd',
         'xlink': 'http://www.w3.org/1999/xlink'
}

_CPPMODE = '_CPPMODE'
_CPAMODE = '_CPAMODE'

_USERMESSAGE = '_USERMESSAGE'
_SIGNALMESSAGE = '_SIGNALMESSAGE'

_SYNC = '_SYNC'
_ASYNC = '_ASYNC'

def cpp23(inputdoc):
    mode = None
    try:
        # in case we got an element tree
        cpp2doc = inputdoc.getroot()
    except:
        # in case we got an element
        cpp2doc = inputdoc
    if cpp2doc.tag == cppa2('CollaborationProtocolProfile'):
        mode = _CPPMODE
        outputdoc = lxml.etree.Element(cppa3('CPP'),
                                       nsmap= {'cppa': 'http://docs.oasis-open.org/ebcore/ns/cppa/v3.0',
                                               'ds': 'http://www.w3.org/2000/09/xmldsig#',
                                               'xml': 'http://www.w3.org/XML/1998/namespace' })
        return _cppa23(cpp2doc, outputdoc, mode=_CPPMODE)
    else:
        raise Exception(
            'Input document is not a CPP, root is {}, expecting {}'.format(cppa2doc.tag,
                                                                           cppa2('CollaborationProtocolProfile'))
        )

def cpa23(inputdoc):
    mode = None
    try:
        # in case we got an element tree
        cppa2doc = inputdoc.getroot()
    except:
        # in case we got an element
        cppa2doc = inputdoc
    if cppa2doc.tag == cppa2('CollaborationProtocolAgreement'):
        mode = _CPAMODE
        outputdoc = lxml.etree.Element(cppa3('CPA'),
                                       nsmap= {'cppa': 'http://docs.oasis-open.org/ebcore/ns/cppa/v3.0',
                                               'ds': 'http://www.w3.org/2000/09/xmldsig#',
                                               'xml': 'http://www.w3.org/XML/1998/namespace' })
        return _cppa23(cppa2doc, outputdoc, mode=_CPAMODE)
    else:
        raise Exception(
            'Input document is not a CPA, root is {}, expecting {}'.format(cppa2doc.tag,
                                                                           cppa2('CollaborationProtocolAgreement'))
        )

def _cppa23(inputdoc, outputdoc, mode=_CPPMODE):
    party_info = inputdoc.xpath('cppa2:PartyInfo',
                                namespaces=_NSMAP)[0]
    if mode == _CPPMODE:
        otherparty_info = None
        process_profileinfo(inputdoc, outputdoc)
    elif mode == _CPAMODE:
        otherparty_info = inputdoc.xpath('cppa2:PartyInfo',
                                         namespaces=_NSMAP)[1]
        process_agreementinfo(inputdoc, outputdoc)
    process_parties(party_info, otherparty_info, outputdoc)
    matched_channels = {}
    matched_transports = {}
    matched_payload_profiles = {}
    match_collaborationroles(party_info, otherparty_info, outputdoc,
                             matched_channels, matched_transports,
                             matched_payload_profiles, mode)
    for ch in matched_channels:
        outputdoc.append(matched_channels[ch])
    for tr in matched_transports:
        outputdoc.append(matched_transports[tr])
    process_payload_profiles(inputdoc, outputdoc, matched_payload_profiles)
    process_packaging(inputdoc, outputdoc, matched_payload_profiles)

    return outputdoc

def process_profileinfo(inputdoc, outputdoc):
    profile_info_element = lxml.etree.SubElement(outputdoc,
                                                   cppa3('ProfileInfo'))
    profile_identifier_element = lxml.etree.SubElement(profile_info_element,
                                                       cppa3('ProfileIdentifier'))
    profile_identifier_element.text = inputdoc.get(cppa2('cppid'))


def process_agreementinfo(inputdoc, outputdoc):
    agreement_info_element = lxml.etree.SubElement(outputdoc,
                                                   cppa3('AgreementInfo'))
    agreement_identifier_element = lxml.etree.SubElement(agreement_info_element,
                                                         cppa3('AgreementIdentifier'))
    agreement_identifier_element.text = inputdoc.get(cppa2('cpaid'))
    for comment_element in inputdoc.xpath('cppa2:Comment', namespaces=_NSMAP):
        description = lxml.etree.SubElement(agreement_info_element,
                                            cppa3('Description'))
        description.text = comment_element.text
        description_lang = comment_element.get(xml('lang'))
        if description_lang != None:
            description.set(xml('lang'), description_lang)




def process_parties(partyinfo, counterparty_info, parent):
    for (p, el) in [
        (partyinfo, cppa3('PartyInfo')),
        (counterparty_info, cppa3('CounterPartyInfo'))
        ]:
        if p != None:
            el = lxml.etree.SubElement(parent, el)
            process_party_elements(p, el)

def process_party_elements(inel, outel):
    v2_partyname = inel.get(cppa2('partyName'))
    v3_partyname = lxml.etree.SubElement(outel, cppa3('PartyName'))
    v3_partyname.text = v2_partyname

    v2_partyref = inel.xpath(
        'cppa2:PartyRef/@xlink:href',
        namespaces=_NSMAP
    )[0]
    v3_partyname.set('href', v2_partyref)
    v2_partyid = inel.xpath(
        'cppa2:PartyId',
        namespaces=_NSMAP
    )[0]
    v3_partyid = lxml.etree.SubElement(outel, cppa3('PartyId'))
    v3_partyid.text = v2_partyid.text
    if v2_partyid.get(cppa2('type')) != None:
        v3_partyid.set('type', v2_partyid.get(cppa2('type')))

    for v2_cert in inel.xpath(
        'cppa2:Certificate',
        namespaces=_NSMAP
    ):
        v3_cert = lxml.etree.SubElement(outel,
                                        cppa3('Certificate'),
                                        id=v2_cert.get(cppa2('certId')))
        for v2_child in v2_cert:
            v3_cert.append(deepcopy(v2_child))

    for v2_security_details in inel.xpath(
        'cppa2:SecurityDetails',
        namespaces=_NSMAP
    ):
        security_details_id = v2_security_details.get(cppa2('securityId'))
        for v2_ta in v2_security_details.xpath(
            'cppa2:TrustAnchors',
            namespaces=_NSMAP
        ):
            v3_ta = lxml.etree.SubElement(outel,
                                          cppa3('TrustAnchorSet'),
                                          id=security_details_id)
            for v2_acert_ref in v2_ta.xpath(
                'cppa2:AnchorCertificateRef',
                namespaces=_NSMAP
            ):
                lxml.etree.SubElement(v3_ta,
                                      cppa3('AnchorCertificateRef'),
                                      certId=v2_acert_ref.get(cppa2('certId')))

def match_collaborationroles(party_info, counterparty_info, parent,
                             matched_channels, matched_transports,
                             matched_payload_profiles, mode):
    collaborationroles = party_info.xpath(
        'cppa2:CollaborationRole',
        namespaces = _NSMAP
    )
    for collaborationrole in collaborationroles:
        party_role = collaborationrole.xpath(
            'cppa2:Role/@cppa2:name',
            namespaces=_NSMAP
        )[0]
        process_specification = collaborationrole.xpath(
            'cppa2:ProcessSpecification',
            namespaces=_NSMAP
        )[0]
        process_name = process_specification.get(cppa2('name'))
        process_version = process_specification.get(cppa2('version'))
        process_uuid = process_specification.get(cppa2('uuid'))

        logging.info('Matching collaborations for {} {} {} {} {}'.format(party_role,
                                                                         process_name,
                                                                         process_version,
                                                                         process_uuid,
                                                                         mode))

        if mode == _CPAMODE:
            other_collaborationroles = counterparty_info.xpath(
                'cppa2:CollaborationRole[cppa2:ProcessSpecification[@cppa2:uuid="{}"]]'.format(process_uuid),
                namespaces = _NSMAP
            )
            # In v2 PartyInfo we can only find the role of the other party
            # via the ActionBinding,  so we just try all of them.
            for othercollaborationrole in other_collaborationroles:
                counterparty_role = othercollaborationrole.xpath(
                    'cppa2:Role/@cppa2:name',
                    namespaces=_NSMAP
                )[0]

                logging.info('Counterparty role is {}'.format(counterparty_role))

                service_specification_element = lxml.etree.Element(cppa3('ServiceSpecification'),
                                                                   name=process_name,
                                                                   version=process_version)
                if process_uuid != None:
                    service_specification_element.set('uuid',process_uuid)
                party_role_element = lxml.etree.SubElement(service_specification_element,
                                                           cppa3('PartyRole'),
                                                           name=party_role)
                #party_role_element.text = party_role
                counterparty_role_element = lxml.etree.SubElement(service_specification_element,
                                                                cppa3('CounterPartyRole'),
                                                                name=counterparty_role)
                #counterparty_role_element.text= counterparty_role
                # A role pair is only added if there is at least one ServiceBinding
                # for the pair
                at_least_one_matching_servicebinding = False
                if match_servicebindings(collaborationrole, othercollaborationrole,
                    party_info, counterparty_info, service_specification_element,
                    matched_channels, matched_transports,
                    matched_payload_profiles, mode):
                    parent.append(service_specification_element)
                else:
                    logging.info('No matching service bindings for {} {} {} '.format(party_role,
                                                                                     counterparty_role,
                                                                                     mode))
        elif mode == _CPPMODE:
            service_specification_element = lxml.etree.Element(cppa3('ServiceSpecification'),
                                                               name=process_name,
                                                               version=process_version)
            if process_uuid != None:
                service_specification_element.set('uuid',process_uuid)
            party_role_element = lxml.etree.SubElement(service_specification_element,
                                                       cppa3('PartyRole'),
                                                       name=party_role)
            #party_role_element.text = party_role
            counterparty_role = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/defaultRole'
            counterparty_role_element = lxml.etree.SubElement(service_specification_element,
                                                            cppa3('CounterPartyRole'),
                                                            name=counterparty_role)

            at_least_one_matching_servicebinding = True
            if match_servicebindings(collaborationrole, None,
                party_info, counterparty_info, service_specification_element,
                matched_channels, matched_transports,
                matched_payload_profiles, mode):
                parent.append(service_specification_element)
            else:
                logging.info('No matching service bindings for {} {} {} '.format(party_role,
                                                                                 counterparty_role,
                                                                                 mode))


def match_servicebindings(collaborationrole, othercollaborationrole, party_info, counterparty_info,
                          parent, matched_channels, matched_transports,
                          matched_payload_profiles, mode):
    service_bindings = collaborationrole.xpath(
        'cppa2:ServiceBinding',
        namespaces=_NSMAP
    )
    at_least_one_matching_servicebinding = False
    for service_binding in service_bindings:
        service = service_binding.xpath(
            'cppa2:Service/text()',
            namespaces=_NSMAP
        )[0]
        logging.info('Processing service binding {}'.format(service))
        service_binding_element = lxml.etree.SubElement(parent,
                                                        cppa3('ServiceBinding'))
        service_element = lxml.etree.SubElement(service_binding_element,
                                                cppa3('Service'))
        service_element.text = service
        if mode == _CPAMODE:
            try:
                other_servicebinding = othercollaborationrole.xpath(
                    'cppa2:ServiceBinding[cppa2:Service/text()="{}"]'.format(service),
                    namespaces=_NSMAP
                )[0]
            except:
                logging.error("Cannot find other servicebinding for {}".format(service))
                raise Exception("Cannot find other servicebinding for {}".format(service))
        elif mode == _CPPMODE:
            other_servicebinding = None
            at_least_one_matching_servicebinding = True
        if match_actionbindings(party_info, service_binding, service,
            counterparty_info, other_servicebinding, service_binding_element,
            matched_channels, matched_transports, matched_payload_profiles, mode):
            at_least_one_matching_servicebinding = True
        else:
            logging.info('No matching service binding for {}'.format(service))
    return at_least_one_matching_servicebinding

def match_actionbindings(party_info, service_binding, service,
                         counterparty_info, other_servicebinding, parent,
                         matched_channels, matched_transports,
                         matched_payload_profiles, mode):
    at_least_one_matching_actionbinding = False
    logging.info('Matching action bindings for {}'.format(service))
    for (v2inbinding, send_or_receive, v2otherbindingxp) in [
        ('cppa2:CanSend','send','cppa2:CanReceive/cppa2:ThisPartyActionBinding[@cppa2:id="{}"]'),
        ('cppa2:CanReceive','receive','cppa2:CanSend/cppa2:ThisPartyActionBinding[@cppa2:id="{}"]')
    ]:
        for action_binding in service_binding.xpath(
            v2inbinding,
            namespaces=_NSMAP
        ):
            thispartyactionbinding = action_binding.xpath(
                'cppa2:ThisPartyActionBinding',
                namespaces = _NSMAP
            )[0]
            thisabid = thispartyactionbinding.xpath('@cppa2:id', namespaces=_NSMAP)[0]
            action = thispartyactionbinding.xpath('@cppa2:action', namespaces=_NSMAP)[0]
            channel_id = thispartyactionbinding.xpath('cppa2:ChannelId/text()', namespaces=_NSMAP)[0]
            actionbinding_element = lxml.etree.Element(cppa3('ActionBinding'),
                                                       sendOrReceive=send_or_receive,
                                                       action=action,
                                                       id=thisabid)
            package_id = thispartyactionbinding.get(cppa2('packageId'))
            logging.info('Matching action bindings for {} {}'.format(service, action))

            if package_id != None:
                payload_profile_ref = lxml.etree.SubElement(action_binding,
                                                            cppa3('PayloadProfileId'))

                payload_profile_ref.text = package_id
                matched_payload_profiles[package_id] = package_id

            ebbp_quality_attributes(thispartyactionbinding,
                                    actionbinding_element)
            action_context(thispartyactionbinding,
                           actionbinding_element)
            if mode == _CPAMODE:
                otherabid = action_binding.xpath(
                    'cppa2:OtherPartyActionBinding/text()',
                    namespaces = _NSMAP
                )[0]
                try:
                    xpq = v2otherbindingxp.format(otherabid)
                    otherpartyactionbinding = other_servicebinding.xpath(
                        xpq,
                        namespaces=_NSMAP
                    )[0]
                    otherchannel_id = otherpartyactionbinding.xpath(
                        'cppa2:ChannelId/text()',
                        namespaces=_NSMAP
                    )[0]
                    channelid_element = lxml.etree.SubElement(actionbinding_element,
                                                              cppa3('ChannelId'))
                    channelid_element.text = xrefid(channel_id, otherchannel_id,
                                                    package_id, send_or_receive)
                except:
                    logging.info('{} {} no match in other party info'.format(thisabid, action))
                else:
                    at_least_one_matching_actionbinding = True
                    parent.append(actionbinding_element)
                    logging.info('{} {} {} {} {} {}'.format(thisabid, send_or_receive, action,
                                                            channel_id, otherabid, otherchannel_id))
            elif mode == _CPPMODE:
                parent.append(actionbinding_element)
                otherchannel_id = None
                at_least_one_matching_actionbinding = True
                channelid_element = lxml.etree.SubElement(actionbinding_element,
                                                          cppa3('ChannelId'))
                channelid_element.text = xrefid(channel_id, 'none',
                                                package_id, send_or_receive)
            match_channels(party_info, counterparty_info,
                           send_or_receive, channel_id, otherchannel_id, package_id,
                           matched_channels, matched_transports, mode, _USERMESSAGE)
    logging.info('at_least_one_matching_actionbinding {}'.format(at_least_one_matching_actionbinding))
    return at_least_one_matching_actionbinding

def ebbp_quality_attributes(thispartyactionbinding,
                            action_binding):
    business_transaction_characteristics = thispartyactionbinding.xpath(
        'cppa2:BusinessTransactionCharacteristics',
        namespaces=_NSMAP
    )[0]
    # to do:  isTamperProof ?
    # to do: isAuthenticated ?
    # to do:  isConfidential
    for att in ['isNonRepudiationRequired',
                'isNonRepudiationReceiptRequired',
                #'isConfidential',
                'isAuthorizationRequired',
                #'isTamperProof',
                #'isAuthenticated',
                'isIntelligibleCheckRequired',
                'timeToAcknowledgeReceipt',
                'timeToAcknowledgeAcceptance',
                'timeToPerform',
                'retryCount']:
        value = business_transaction_characteristics.get(cppa2(att))
        #logging.info('{} {} {}'.format(att, value, lxml.etree.tostring(business_transaction_characteristics)))
        if value != None:
            action_binding.set(att, value)

def action_context(thispartyactionbinding,
                   action_binding):
    action_context_list = thispartyactionbinding.xpath(
        'cppa2:ActionContext',
        namespaces=_NSMAP
    )
    if len(action_context_list) > 0:
        for (att) in [#'binaryCollaboration',
                      'businessTransactionActivity',
                      'requestOrResponseAction']:
            value = action_context_list[0].get(cppa2(att))
            if value != None:
                action_binding.set(att, value)


def match_channels(party_info, counterparty_info, send_or_receive,
                   channel_id, otherchannel_id, package_id, matched_channels, matched_transports,
                   mode=_CPPMODE, message_type=_USERMESSAGE, syncmode=_ASYNC):
    this_v2_channel = party_info.xpath(
        'cppa2:DeliveryChannel[@cppa2:channelId="{}"]'.format(channel_id),
        namespaces=_NSMAP
    )[0]
    this_v2_messagingcharacteristics = this_v2_channel.xpath(
        'cppa2:MessagingCharacteristics',
        namespaces=_NSMAP
    )[0]
    this_v2_docexchange_id = this_v2_channel.xpath(
        '@cppa2:docExchangeId',
        namespaces=_NSMAP
    )[0]
    ebms_binding = get_ebxml_binding(party_info, this_v2_docexchange_id, send_or_receive)
    this_v2_transport_id = this_v2_channel.xpath(
        '@cppa2:transportId',
        namespaces=_NSMAP
    )[0]
    if otherchannel_id != None:
        other_v2_channel_id = counterparty_info.xpath(
            'cppa2:DeliveryChannel[@cppa2:channelId="{}"]'.format(otherchannel_id),
            namespaces=_NSMAP
        )[0]
        other_v2_messagingcharacteristics = other_v2_channel_id.xpath(
            'cppa2:MessagingCharacteristics',
            namespaces=_NSMAP
        )[0]
        other_v2_docexchange_id = other_v2_channel_id.xpath(
            '@cppa2:docExchangeId',
            namespaces=_NSMAP
        )[0]
        other_ebms_binding = get_ebxml_binding(counterparty_info, other_v2_docexchange_id,
                                               reverse(send_or_receive))
        other_v2_transport_id = other_v2_channel_id.xpath(
            '@cppa2:transportId',
            namespaces=_NSMAP
        )[0]
    else:
        other_v2_channel_id = other_v2_docexchange_id = other_v2_transport_id =\
            other_v2_messagingcharacteristics = other_ebms_binding = None
    matched_channel_id = xrefid(channel_id, otherchannel_id, package_id, send_or_receive, message_type)
    matched_transport_id = xrefid(this_v2_transport_id, other_v2_transport_id, package_id, send_or_receive)
    if syncmode == _ASYNC:
        ebms2_channel_element = lxml.etree.Element(cppa3('ebMS2Channel'),
                                                   id=matched_channel_id,
                                                   transport=matched_transport_id,
                                                   package=envelope_key(package_id))
    else:
        ebms2_channel_element = lxml.etree.Element(cppa3('ebMS2Channel'),
                                                   id=matched_channel_id,
                                                   asResponse='true',
                                                   package=envelope_key(package_id))
    if message_type == _USERMESSAGE:
        signal_channel_id = signal_channel(party_info, counterparty_info,
                                           channel_id, otherchannel_id,
                                           this_v2_messagingcharacteristics,
                                           send_or_receive,
                                           matched_channels, matched_transports,
                                           mode)
        process_error_handling(ebms2_channel_element, signal_channel_id)
        process_receipt_handling(ebms2_channel_element, signal_channel_id,
                                this_v2_messagingcharacteristics)
        process_reliable_messaging(ebms2_channel_element,
                                  this_v2_messagingcharacteristics,
                                  ebms_binding)
    process_security_binding(ebms2_channel_element,
                             ebms_binding,
                             other_ebms_binding,
                             send_or_receive,
                             mode)
    matched_channels[matched_channel_id] = ebms2_channel_element
    match_transports(party_info, counterparty_info, send_or_receive,
                       this_v2_transport_id, other_v2_transport_id, matched_transports)

def signal_channel(party_info, counterparty_info,
                   um_channel_id, um_otherchannel_id,
                   messagingcharacteristics, send_or_receive,
                   matched_channels, matched_transports, mode):
    sync_reply_mode = messagingcharacteristics.get(cppa2('syncReplyMode'), 'none')
    if sync_reply_mode in ['none', 'responseOnly']:
        sync = _ASYNC
        channel_id = party_info.get(cppa2('defaultMshChannelId'))
        if counterparty_info != None:
            otherchannel_id = counterparty_info.get(cppa2('defaultMshChannelId'))
        else:
            otherchannel_id = None
    else:
        sync = _SYNC
        channel_id = um_channel_id
        otherchannel_id = um_otherchannel_id
    match_channels(party_info, counterparty_info,
                   reverse(send_or_receive), channel_id, otherchannel_id, 'signal',
                   matched_channels, matched_transports, mode, message_type=_SIGNALMESSAGE, syncmode=sync)
    channel_id = xrefid(channel_id, otherchannel_id, 'signal', reverse(send_or_receive), _SIGNALMESSAGE)
    return channel_id

def process_error_handling(ebms2_channel_element, signal_channel_id):
    error_handling_element = lxml.etree.SubElement(ebms2_channel_element,
                                                   cppa3('ErrorHandling'))
    receiver_errors_channel_element = lxml.etree.SubElement(error_handling_element,
                                                            cppa3('ReceiverErrorsReportChannelId'))
    receiver_errors_channel_element.text = signal_channel_id

def process_receipt_handling(ebms2_channel_element, signal_channel_id, messagingcharacteristics):
    ackrequested = messagingcharacteristics.get(cppa2('ackRequested'), 'perMessage')
    if ackrequested != 'never':
        receipt_handling_element = lxml.etree.SubElement(ebms2_channel_element,
                                                         cppa3('ReceiptHandling'))
        receipt_channel_element = lxml.etree.SubElement(receipt_handling_element,
                                                        cppa3('ReceiptChannelId'))
        receipt_channel_element.text = signal_channel_id

def process_reliable_messaging(ebms2_channel_element, messagingcharacteristics, ebmsbinding):
    duplicate_elimination = messagingcharacteristics.get(cppa2('ackRequested'), 'perMessage')

    ebms_rm_list = ebmsbinding.xpath(
        'cppa2:ReliableMessaging',
        namespaces=_NSMAP
    )

    if duplicate_elimination != 'never' or len(ebms_rm_list) > 0:
        rm_element = lxml.etree.SubElement(ebms2_channel_element,
                                           cppa3('ebMS2ReliableMessaging'))
        actor = messagingcharacteristics.get(cppa2('actor'))
        if actor != None:
            rm_element.set('actor', actor)
        if duplicate_elimination != 'never':
            dh_element = lxml.etree.SubElement(rm_element,
                                               cppa3('DuplicateHandling'))
            de_element = lxml.etree.SubElement(dh_element,
                                               cppa3('DuplicateElimination'))
            de_element.text = 'true'
        if len(ebms_rm_list) > 0:
            ebms_rm = ebms_rm_list[0]
            #logging.info(lxml.etree.tostring(ebms_rm))
            rh_element = lxml.etree.SubElement(rm_element,
                                               cppa3('RetryHandling'))
            try:
                retries = ebms_rm.xpath('cppa2:Retries/text()', namespaces=_NSMAP)[0]
                retries_element = lxml.etree.SubElement(rh_element,
                                                        cppa3('Retries'))
                retries_element.text = retries
            except:
                pass
            try:
                retry_int = ebms_rm.xpath('cppa2:RetryInterval/text()', namespaces=_NSMAP)[0]
                retry_int_element = lxml.etree.SubElement(rh_element,
                                                        cppa3('RetryInterval'))
                retry_int_element.text = retry_int
            except:
                pass
            message_ordering = ebms_rm.xpath('cppa2:MessageOrderSemantics/text()', namespaces=_NSMAP)[0]
            if message_ordering == 'Guaranteed':
                rm_element.set('ordered', 'true')
            else:
                rm_element.set('ordered', 'false')


def process_security_binding(ebms2_channel_element,
                             ebms_binding,
                             other_ebms_binding,
                             send_or_receive, mode):

    #logging.info('>>>> {} {} {} {}'.format(ebms2_channel_element,
    #                                  ebms_binding,
    #                                  other_ebms_binding,
    #                                  send_or_receive))

    if send_or_receive == 'send':
        sender_ebms2_nro_list = ebms_binding.xpath(
            'cppa2:SenderNonRepudiation',
            namespaces=_NSMAP
        )
        sender_ebms2_de_list = ebms_binding.xpath(
            'cppa2:SenderDigitalEnvelope',
            namespaces=_NSMAP
        )
        if other_ebms_binding != None:
            receiver_ebms2_nro_list = other_ebms_binding.xpath(
                'cppa2:ReceiverNonRepudiation',
                namespaces=_NSMAP
            )
            receiver_ebms2_de_list = other_ebms_binding.xpath(
                'cppa2:ReceiverDigitalEnvelope',
                namespaces=_NSMAP
            )
        else:
            receiver_ebms2_nro_list = []
            receiver_ebms2_de_list = []
    else:
        receiver_ebms2_nro_list = ebms_binding.xpath(
            'cppa2:ReceiverNonRepudiation',
            namespaces=_NSMAP
        )
        receiver_ebms2_de_list = ebms_binding.xpath(
            'cppa2:ReceiverDigitalEnvelope',
            namespaces=_NSMAP
        )
        if other_ebms_binding != None:
            sender_ebms2_nro_list = other_ebms_binding.xpath(
                'cppa2:SenderNonRepudiation',
                namespaces=_NSMAP
            )
            sender_ebms2_de_list = other_ebms_binding.xpath(
                'cppa2:SenderDigitalEnvelope',
                namespaces=_NSMAP
            )
        else:
            sender_ebms2_nro_list = []
            sender_ebms2_de_list = []

    #logging.info('>>>> {} {} {} {}'.format(sender_ebms2_de_list,
    #                                       sender_ebms2_nro_list,
    #                                       receiver_ebms2_de_list,
    #                                       receiver_ebms2_nro_list))

    if len(sender_ebms2_nro_list) > 0 or \
        len(receiver_ebms2_nro_list) > 0 or \
        len(sender_ebms2_de_list) > 0 or \
        len(receiver_ebms2_de_list) > 0:
        ebms2_security_element = lxml.etree.SubElement(ebms2_channel_element,
                                                       cppa3('ebMS2SecurityBinding'))
        if len(sender_ebms2_nro_list) > 0 and \
            len(receiver_ebms2_nro_list) > 0:
            process_signature(ebms2_security_element,
                              sender_ebms2_nro_list[0],
                              receiver_ebms2_nro_list[0],
                              mode)
        if len(receiver_ebms2_de_list) > 0:
            process_encryption(ebms2_security_element,
                               receiver_ebms2_de_list[0],
                               mode)


def process_signature(ebms2_security_element, sender_ebms2_nro, receiver_ebms2_nro, mode):
    signature_element = lxml.etree.SubElement(ebms2_security_element,
                                              cppa3('Signature'))
    signature_format_element = lxml.etree.SubElement(signature_element,
                                                     cppa3('SignatureFormat'))
    signature_format_element.text = sender_ebms2_nro.xpath(
        'cppa2:NonRepudiationProtocol',
        namespaces=_NSMAP
    )[0].text
    for v2_signature_algorithm in sender_ebms2_nro.xpath(
        'cppa2:SignatureAlgorithm',
        namespaces=_NSMAP
    ):
        signature_algorithm_element = lxml.etree.SubElement(signature_element,
                                                            cppa3('SignatureAlgorithm'))
        if v2_signature_algorithm.get(cppa2('w3c')) != None:
            signature_algorithm_element.text = v2_signature_algorithm.get(cppa2('w3c'))
        else:
            signature_algorithm_element.text = v2_signature_algorithm.text
    digest_algorithm_element = lxml.etree.SubElement(signature_element,
                                                     cppa3('DigestAlgorithm'))
    digest_algorithm_element.text = sender_ebms2_nro.xpath(
        'cppa2:HashFunction',
        namespaces=_NSMAP
    )[0].text
    signing_certificate_ref_element = lxml.etree.SubElement(
        signature_element,
        cppa3('SigningCertificateRef'))
    v2_certificate_ref = sender_ebms2_nro.xpath(
        'cppa2:SigningCertificateRef',
        namespaces=_NSMAP
    )[0]
    signing_certificate_ref_element.text = v2_certificate_ref.text
    signing_certificate_ref_element.set('certId', v2_certificate_ref.get(cppa2('certId')))

def process_encryption(ebms2_security_element, receiver_ebms2_de, mode):
    encryption_element = lxml.etree.SubElement(ebms2_security_element,
                                               cppa3('Encryption'))

    #logging.info('############# {}'.format(lxml.etree.tostring(receiver_ebms2_de, pretty_print=True)))
    encryption_format_element = lxml.etree.SubElement(encryption_element,
                                                     cppa3('EncryptionFormat'))
    de_protocol = receiver_ebms2_de.xpath(
        'cppa2:DigitalEnvelopeProtocol',
        namespaces=_NSMAP)[0]
    encryption_format_element.text = de_protocol.text
    try:
        encryption_format_element.set('version',
                                      de_protocol.get(cppa2('version'))
        )
    except:
        pass
    for v2_encryption_algorithm in receiver_ebms2_de.xpath(
        'cppa2:EncryptionAlgorithm',
        namespaces=_NSMAP
    ):
        #data_encryption_element = lxml.etree.SubElement(encryption_element,
        #                                                cppa3('DataEncryption'))
        encryption_algorithm_element = lxml.etree.SubElement(encryption_element,
                                                            cppa3('EncryptionAlgorithm'))
        encryption_algorithm_element.text = v2_encryption_algorithm.text
    v2_certificate_ref = receiver_ebms2_de.xpath(
        'cppa2:EncryptionCertificateRef',
        namespaces=_NSMAP
    )[0]
    encryption_certificate_ref_element = lxml.etree.SubElement(
        encryption_element,
        cppa3('EncryptionCertificateRef'))
    encryption_certificate_ref_element.text = v2_certificate_ref.text
    encryption_certificate_ref_element.set('certId', v2_certificate_ref.get(cppa2('certId')))


def process_payload_profiles(inputdoc, outputdoc, matched_payload_profiles):
    for key in matched_payload_profiles:
        payloadprofile_element = lxml.etree.SubElement(outputdoc,
                                                       cppa3('PayloadProfile'),
                                                       id=key)
        v2_packaging = inputdoc.xpath('descendant::cppa2:Packaging[@cppa2:id="{}"]'.format(key),
                                      namespaces=_NSMAP)[0]
        v2_composite_list = v2_packaging[-1]
        v2_ebms_envelope = v2_composite_list[-1]
        assert v2_ebms_envelope.get(cppa2('mimetype')) == 'multipart/related'
        assert v2_ebms_envelope.tag == cppa2('Composite')
        # check that first constituent is ebMS2 SOAP header
        for v2_constituent in v2_ebms_envelope[1:]:
            payloadpart_element = lxml.etree.SubElement(payloadprofile_element,
                                                        cppa3('PayloadPart'))
            v2_partid = v2_constituent.get(cppa2('idref'))
            partname_element = lxml.etree.SubElement(payloadpart_element,
                                                     cppa3('PartName'))
            partname_element.text = v2_partid
            process_payload_part(inputdoc, payloadpart_element, v2_partid)

def process_payload_part(inputdoc, payloadpart_element, v2_partid):
    v2_referenced_part = inputdoc.xpath('descendant::*[@cppa2:id="{}"]'.format(v2_partid),
                                        namespaces=_NSMAP)[0]
    if v2_referenced_part.tag == cppa2('SimplePart'):
        mimetype_element = lxml.etree.SubElement(payloadpart_element,
                                                 cppa3('MIMEContentType'))
        mimetype_element.text = v2_referenced_part.get(cppa2('mimetype'))
        v2_namespacesupported = v2_referenced_part.xpath(
            'cppa2:NamespaceSupported',
            namespaces=_NSMAP
        )[-1]
        schema_element = lxml.etree.SubElement(payloadpart_element,
                                               cppa3('Schema'))
        for att in ['version', 'location', 'namespace']:
            if v2_namespacesupported.get(cppa2(att)) != None:
                schema_element.set(att,
                                   v2_namespacesupported.get(cppa2(att)))
    elif v2_referenced_part.tag == cppa2('Encapsulation'):
        constituent_idref = v2_referenced_part.xpath(
            'cppa2:Constituent/@cppa2:idref',
            namespaces=_NSMAP
        )[0]
        process_payload_part(inputdoc, payloadpart_element, constituent_idref)



def process_packaging(inputdoc, outputdoc, matched_payload_profiles):
    for key in matched_payload_profiles:
        v3_package_element = lxml.etree.SubElement(outputdoc,
                                                   cppa3('SOAPWithAttachmentsEnvelope'),
                                                   id=envelope_key(key))
        v2_packaging = inputdoc.xpath('descendant::cppa2:Packaging[@cppa2:id="{}"]'.format(key),
                                      namespaces=_NSMAP)[0]
        v2_composite_list = v2_packaging[-1]
        v2_ebms_envelope = v2_composite_list[-1]
        assert v2_ebms_envelope.get(cppa2('mimetype')) == 'multipart/related'
        assert v2_ebms_envelope.tag == cppa2('Composite')
        # check that first constituent is ebMS2 SOAP header
        for v2_constituent in v2_ebms_envelope[1:]:
            lxml.etree.SubElement(v3_package_element,
                                  cppa3('SimpleMIMEPart'),
                                  PartName=v2_constituent.get(cppa2('idref')))



def envelope_key(key):
    return key+'_envelope'

def get_ebxml_binding(party_info, docexchangeid, send_or_receive):
    if party_info is None:
        return None
    if send_or_receive == 'send':
        return party_info.xpath(
            'cppa2:DocExchange[@cppa2:docExchangeId="{}"]/cppa2:ebXMLSenderBinding'.format(docexchangeid),
            namespaces=_NSMAP
        )[0]
    else:
        return party_info.xpath(
            'cppa2:DocExchange[@cppa2:docExchangeId="{}"]/cppa2:ebXMLReceiverBinding'.format(docexchangeid),
            namespaces=_NSMAP
        )[0]



def xrefid(v1, v2, v3, v4, v5=_USERMESSAGE):
    if v5 == _SIGNALMESSAGE:
        return '{}_{}_{}_{}{}'.format(v1, v2, v3, v4, v5)
    else:
        return '{}_{}_{}_{}'.format(v1, v2, v3, v4)

def reverse(direction):
    if direction == 'send':
        return 'receive'
    elif direction == 'receive':
        return 'send'

def match_transports(party_info, counterparty_info, send_or_receive,
                     transport_id, othertransport_id, matched_transports):
    sender_transport = receiver_transport = transport_protocol_name = None
    if send_or_receive == 'send':
        sender_transport = party_info.xpath(
            'cppa2:Transport[@cppa2:transportId="{}"]/cppa2:TransportSender'.format(transport_id),
            namespaces=_NSMAP
        )[0]
        base_transport = sender_transport
        if counterparty_info != None:
            receiver_transport = counterparty_info.xpath(
                'cppa2:Transport[@cppa2:transportId="{}"]/cppa2:TransportReceiver'.format(othertransport_id),
                namespaces=_NSMAP
            )[0]
    elif send_or_receive == 'receive':
        receiver_transport = party_info.xpath(
            'cppa2:Transport[@cppa2:transportId="{}"]/cppa2:TransportReceiver'.format(transport_id),
            namespaces=_NSMAP
        )[0]
        base_transport = receiver_transport
        if counterparty_info != None:
            sender_transport = counterparty_info.xpath(
                'cppa2:Transport[@cppa2:transportId="{}"]/cppa2:TransportSender'.format(othertransport_id),
                namespaces=_NSMAP
            )[0]
    transport_protocol = base_transport.xpath(
        'cppa2:TransportProtocol',
        namespaces=_NSMAP
    )[0]
    transport_protocol_name = transport_protocol.text
    transport_protocol_version_list = transport_protocol.xpath(
        '@cppa2:version',
        namespaces=_NSMAP
    )
    if transport_protocol_name == 'HTTP':
        unified_transport = lxml.etree.Element(cppa3('HTTPTransport'),
                                               id=xrefid(transport_id,
                                                         othertransport_id,
                                                         '',
                                                         send_or_receive))
    elif transport_protocol_name == 'SMTP':
        unified_transport = lxml.etree.Element(cppa3('SMTPTransport'), id=xrefid(transport_id,
                                                         othertransport_id,
                                                         '',
                                                         send_or_receive))
    if receiver_transport != None:
        endpoint_element = lxml.etree.SubElement(unified_transport,
                                                 cppa3('Endpoint'))
        endpoint_element.text = receiver_transport.xpath(
            'cppa2:Endpoint/@cppa2:uri', namespaces=_NSMAP
        )[0]

    matched_transports[xrefid(transport_id,
                              othertransport_id, '',
                              send_or_receive)] = unified_transport

def cppa3(el):
    return '{{{}}}{}'.format(_NSMAP['cppa'],el)

def cppa2(el):
    return '{{{}}}{}'.format(_NSMAP['cppa2'],el)

def xml(el):
    return '{{{}}}{}'.format(_NSMAP['xml'],el)
