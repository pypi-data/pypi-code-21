
"""
THIS MODULE IS DEPRECATED and no longer maintained.
Instead, development now focuses on the new cppa23, which converts in the opposite direction.
"""

from lxml import etree
import logging

NSMAP = {'cppa': 'http://docs.oasis-open.org/ebcore/ns/cppa/v3.0',
         'ds': 'http://www.w3.org/2000/09/xmldsig#',
         'xml': 'http://www.w3.org/XML/1998/namespace',
         'cpa2': 'http://www.oasis-open.org/committees/ebxml-cppa/schema/cpp-cpa-2_0.xsd'
}

def downtranslate(v3in):
    """
    @param v3in:  an lxml representation of a version 3 CPA
    @return: an lxml representation of a version 2 CPA derived from v3in
    """
    v2out = etree.Element(cpa2ns('CollaborationProtocolAgreement'),
                         nsmap = NSMAP)
    _process_agreement_info(v3in, v2out)
    partyinfo = _init_partyinfo(v3in, v2out, 'PartyInfo')
    counterpartyinfo = _init_partyinfo(v3in, v2out, 'CounterPartyInfo')
    _process_service_bindings(v3in, partyinfo, counterpartyinfo)
    return v2out

def _process_agreement_info(v3in, v2out):
    v2out.set(cpa2ns('cpaid'),'id')
    status = etree.SubElement(v2out, 'Status')
    status.set(cpa2ns('value'),'agreed')
    start = etree.SubElement(v2out, cpa2ns('Start'))
    start.text = v3in.findtext('{}/{}'.format(cpa3ns('AgreementInfo'),
                                              cpa3ns('ActivationDate')))
    end = etree.SubElement(v2out, cpa2ns('End'))
    end.text = v3in.findtext('{}/{}'.format(cpa3ns('AgreementInfo'),
                                            cpa3ns('ExpirationDate')))

def _init_partyinfo(v3in, v2out, infoelement):
    v3partyinfo = v3in.find(cpa3ns(infoelement))
    v2partyinfo = etree.SubElement(v2out, cpa2ns('PartyInfo'))
    v2partyinfo.set(cpa2ns('partyName'), v3partyinfo.findtext(cpa3ns('PartyName')))
    for v3partyid in v3partyinfo.iterfind(cpa3ns('PartyId')):
        v2partyid = etree.SubElement(v2partyinfo,cpa2ns('PartyId'))
        v2partyid.text = v3partyid.text
        if v3partyid.get('type') is not None:
            v2partyid.set('type',v3partyid.get('type'))
    return v2partyinfo

def _process_service_bindings(v3in, v2partyinfo, v2counterpartyinfo):
    for servicespec in v3in.iterfind(cpa3ns('ServiceSpecification')):
        p1_cr, p2_cr = _init_collaborationrole(servicespec, v2partyinfo, v2counterpartyinfo)
        for sb in servicespec.iterfind(cpa3ns('ServiceBinding')):
            _process_servicebinding(sb, p1_cr, p2_cr)

def _init_collaborationrole(servicespec, v2partyinfo, v2counterpartyinfo):
    p1_cr = etree.SubElement(v2partyinfo, cpa2ns('CollaborationRole'))
    p1_role = etree.SubElement(p1_cr, cpa2ns('Role'))
    p1_role.set(cpa2ns('name'),servicespec.find('{}'.format(cpa3ns('PartyRole'))).get('name'))
    p2_cr = etree.SubElement(v2counterpartyinfo, cpa2ns('CollaborationRole'))
    p2_role = etree.SubElement(p2_cr, cpa2ns('Role'))
    p2_role.set(cpa2ns('name'),servicespec.find('{}'.format(cpa3ns('CounterPartyRole'))).get('name'))
    return p1_cr, p2_cr

def _process_servicebinding(v3servicebinding, p1_cr, p2_cr):
    v2sb_p1 = etree.SubElement(p1_cr, cpa2ns('ServiceBinding'))
    v2sb_p2 = etree.SubElement(p2_cr, cpa2ns('ServiceBinding'))
    for el in v2sb_p1, v2sb_p2:
        v3sel = v3servicebinding.find(cpa3ns('Service'))
        servel = etree.SubElement(el, cpa2ns('Service'))
        servel.text = v3sel.text
        if v3sel.get('type') is not None:
            servel.set( cpa2ns('type'), v3sel.get('type'))
    for ab in v3servicebinding.find(cpa3ns('ActionBinding')):
        _process_actionbinding(ab, v2sb_p1, 'send', 'CanSend', 'S_')
    for ab in v3servicebinding.find(cpa3ns('ActionBinding')):
        _process_actionbinding(ab, v2sb_p1, 'receive', 'CanReceive', 'R_')
    for ab in v3servicebinding.find(cpa3ns('ActionBinding')):
        _process_actionbinding(ab, v2sb_p2, 'receive', 'CanSend', 'R_')
    for ab in v3servicebinding.find(cpa3ns('ActionBinding')):
        _process_actionbinding(ab, v2sb_p2, 'send', 'CanReceive', 'R_')


def _process_actionbinding(ab, sb, direction, v2_elementtag, prefix):
    if ab.get('sendOrReceive') is direction:
        v2_element = etree.SubElement(sb, cpa2ns(v2_element),
                                      id = '{}_{}'.prefix(prefix, ab.get('id')))
    logging.debug('{} {}'.format(ab.get('id'),ab.get('sendOrReceive')))

def cpa3ns(el):
    return '{{{}}}{}'.format(NSMAP['cppa'],el)

def cpa2ns(el):
    return '{{{}}}{}'.format(NSMAP['cpa2'],el)

def ns(ns,el):
    return '{{{}}}{}'.format(ns,el)

