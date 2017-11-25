__author__ = 'pvde'

"""
Module that takes a CPP and filters it for a particular or an anonymous viewer,
taking into account the "allowed" and "denied" authorization attributes.

If the viewer is not authorized for the CPP at CPP level, no view is available.
Otherwise a view is available that is a copy of the CPP, with structures
for which the viewer is not authorized omitted.

Structure levels at which authorization is controlled are the ServiceSpecification,
ServiceBinding and ActionBinding structure levels.
"""

import logging, lxml.etree

from unify import lookup_party_identifiers
from copy import deepcopy

NSMAP = {'cppa': 'http://docs.oasis-open.org/ebcore/ns/cppa/v3.0',
         'ds': 'http://www.w3.org/2000/09/xmldsig#',
         'xml': 'http://www.w3.org/XML/1998/namespace',
         'xkms': 'http://www.w3.org/2002/03/xkms#',
         'dsig11' : 'http://www.w3.org/2009/xmldsig11#'
}

class ViewException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

def view_cpp(viewer_parties, acpp):
    try:
        _acl_check(viewer_parties, acpp, acpp)
    except ViewException as e:
        # the viewer is not authorized at cpp level, no
        # view is possible
        raise e
    else:
        # OK at top level, copy the general parts and
        # check at lower levels
        cpp_view = lxml.etree.Element(_cppa('CPP'), nsmap=NSMAP)
        _view_children(viewer_parties, acpp, cpp_view, acpp)
        return cpp_view

def _view_children(viewer_parties, parent, parent_view, acpp):
    next_level_count = 0
    if parent.tag in _next_level:
        next_level_child_tag, cardinality = _next_level[parent.tag]
    else:
        next_level_child_tag, cardinality = None, None

    for child in parent:
        if child.tag not in [_cppa('PartyIdList')]:
            try:
                filtered_child = _view_child(viewer_parties, child, acpp)
            except ViewException as e:
                pass
            else:
                parent_view.append(filtered_child)
                if child.tag == next_level_child_tag:
                    next_level_count += 1
    if cardinality != None:
        if next_level_count < cardinality:
            raise ViewException('More than {} child elements of type {} needed'.format(next_level_count,
                                                                                       next_level_child_tag))
        else:
            logging.info('Found {} child elements of type {}, {} required'.format(next_level_count,
                                                                                  next_level_child_tag,
                                                                                  cardinality))
    next_level_count = 0

def _view_child(viewer_parties, node, acpp):
    _acl_check(viewer_parties, node, acpp)
    filtered_node = lxml.etree.Element(node.tag)
    _view_children(viewer_parties, node, filtered_node, acpp)
    filtered_node.text = node.text
    for att in node.attrib:
        if att not in ['allowed', 'denied']:
            filtered_node.set(att, node.get(att))
    return filtered_node


def _acl_check(viewer_parties, node, acpp):
    a_allowed_party_list_id = node.get('allowed')
    a_denied_party_list_id = node.get('denied')

    if a_allowed_party_list_id != None:
        a_allowed_parties = lookup_party_identifiers(acpp,
                                                     a_allowed_party_list_id, [])
        _acl_allow_match(a_allowed_parties, viewer_parties)

    if a_denied_party_list_id != None:
        a_denied_parties = lookup_party_identifiers(acpp,
                                                     a_denied_party_list_id, [])
        _acl_deny_match(a_denied_parties, viewer_parties)

def _acl_allow_match(allowed_party_ids, party_ids):
    if party_ids == []:
        raise ViewException('Anonymous not in allowed list')
    for (pid, ptype) in party_ids:
        if (pid, ptype) not in allowed_party_ids:
            logging.info('{}, {} not in allowed list {}'.format(pid,
                                                                ptype,
                                                                allowed_party_ids))
            raise ViewException(
                '{}, {} not in allowed list {}'.format(pid,
                                                    ptype,
                                                    allowed_party_ids))
        else:
            logging.debug('{}, {} found in allowed party list'.format(pid,
                                                                      ptype))

def _acl_deny_match(denied_party_ids, party_ids):
    if party_ids == []:
        pass
    else:
        for (pid, ptype) in party_ids:
            if (pid, ptype) in denied_party_ids:
                raise ViewException(
                    '{}, {} in denied list'.format(pid,
                                                   ptype)
                )
            else:
                logging.debug('{}, {} not in denied party list'.format(pid,
                                                                       ptype))
def _cppa(el):
    return '{{{}}}{}'.format(NSMAP['cppa'],el)

_next_level = { _cppa('CPP') : (_cppa('ServiceSpecification'), 0),
               _cppa('ServiceSpecification') : (_cppa('ServiceBinding'), 1),
               _cppa('ServiceBinding') : (_cppa('ActionBinding'), 1) }

