__author__ = 'pvde'

"""
Module to implement support for ChannelProfile in CPPA3

A ChannelProfileHandler class

"""

from lxml import etree
from copy import deepcopy
import logging, os
from schema import cppa3_content_model as cppa3_content_model

logging.basicConfig(level=logging.DEBUG)

_NSMAP = { 'cppa': 'http://docs.oasis-open.org/ebcore/ns/cppa/v3.0',
           'pycppa3' : 'https://pypi.python.org/pypi/cppa3'}


class ChannelProfileHandler():

    def __init__(self, config=None):
        self._channel_profiles = {}
        self._channel_profiles_send = {}
        self._channel_profiles_receive = {}
        self._channels = {}
        self._channel_dependencies = {}
        self._channel_dependencies_send = {}
        self._channel_dependencies_receive = {}
        self._transports = {}
        if config != None:
            self.load_profile_config(config)

    def load_profile_config(self, parsed_config_document):
        self.load_channel_config(parsed_config_document)
        self.load_transport_config(parsed_config_document)

    def load_channel_config(self, parsed_config_document):
        channels = parsed_config_document.xpath('//pycppa3:ChannelProfiles/*',
                                                namespaces=_NSMAP)
        for channel in channels:
            if _pycppa3('direction') in channel.attrib:
                direction = channel.get(_pycppa3('direction'))
                del channel.attrib[_pycppa3('direction')]
            else:
                direction = None

            channel_profile = channel.xpath('child::cppa:ChannelProfile/text()',
                                            namespaces = _NSMAP)[0]
            logging.info('Loading channel profile {}'.format(channel_profile))
            if not direction:
                self._channel_profiles[channel_profile] = channel
                channel_dependencies = self._channel_dependencies
                # Also add as to send and receive, if no value was provided
                # Will be overwritten if an explicit directional definition is provided
                if channel_profile not in self._channel_profiles_send:
                    self._channel_profiles_send[channel_profile] = channel
                if channel_profile not in self._channel_profiles_receive:
                    self._channel_profiles_receive[channel_profile] = channel

            elif direction == 'send':
                self._channel_profiles_send[channel_profile] = channel
                channel_dependencies = self._channel_dependencies_send
            elif direction == 'receive':
                self._channel_profiles_receive[channel_profile] = channel
                channel_dependencies = self._channel_dependencies_receive

            if 'id' in channel.attrib:
                self._channels[channel.get('id')] = channel

            if channel_profile not in channel_dependencies:
                channel_dependencies[channel_profile] = []

            for dependent_channel_xpath in [
                'child::cppa:ReceiptHandling/cppa:ReceiptChannelId/text()',
                'child::cppa:ErrorHandling/cppa:SenderErrorsReportChannelId/text()',
                'child::cppa:ErrorHandling/cppa:ReceiverErrorsReportChannelId/text()',
                'child::cppa:PullHandling/cppa:PullChannelId/text()',
                'child::cppa:AlternateChannel/text()',
            ]:
                dependent_channel_list = channel.xpath(
                    dependent_channel_xpath,
                    namespaces = _NSMAP)
                for dependent_channel in dependent_channel_list:
                    if dependent_channel not in channel_dependencies[channel_profile]:
                        channel_dependencies[channel_profile].append(dependent_channel)

    def load_transport_config(self, parsed_config_document):
        transports = parsed_config_document.xpath('//pycppa3:TransportProfiles/*',
                                                  namespaces=_NSMAP)
        for transport in transports:
            transporttype = transport.tag
            self._transports[transporttype] = transport



    def apply_profile_configs(self, indoc):
        outdoc = etree.Element(indoc.tag, nsmap = {
            'cppa':'http://docs.oasis-open.org/ebcore/ns/cppa/v3.0' })
        included_dependent_channels = []
        logging.debug('Processing {}'.format(indoc.tag))
        for child in deepcopy(indoc):
            childtype = child.tag
            if childtype in [ cppa('ebMS3Channel'),
                              cppa('ebMS2Channel'),
                              cppa('AS1Channel'),
                              cppa('AS2Channel'),
                              cppa('AS3Channel'),
                              cppa('WSChannel'),
                              cppa('AMQPChannel')
            ]:
                applicable_channel_profiles = self._channel_profiles
                applicable_channel_dependencies = self._channel_dependencies
                if 'id' in child.attrib:
                    element_id = child.get('id')
                    if indoc.xpath(
                        'descendant::cppa:ActionBinding[@sendOrReceive="send"]/cppa:ChannelId="{}"'.format(element_id),
                        namespaces = _NSMAP
                    ):
                        applicable_channel_profiles = self._channel_profiles_send
                        applicable_channel_dependencies = self._channel_dependencies_send
                        logging.info('Channel {} is a SEND channel'.format(element_id))
                    elif indoc.xpath(
                        'descendant::cppa:ActionBinding[@sendOrReceive="receive"]/cppa:ChannelId="{}"'.format(element_id),
                        namespaces = _NSMAP
                    ):
                        applicable_channel_profiles = self._channel_profiles_receive
                        applicable_channel_dependencies = self._channel_dependencies_receive
                        logging.info('Channel {} is a RECEIVE channel'.format(element_id))
                    else:
                        applicable_channel_profiles = self._channel_profiles
                        applicable_channel_dependencies = self._channel_dependencies
                        logging.info('Channel {} is neither a SEND nor a RECEIVE channel'.format(element_id))
                if len(child.xpath('cppa:ChannelProfile',
                                   namespaces = _NSMAP)) > 0:
                    channel_profile = child.xpath('child::cppa:ChannelProfile/text()',
                                                    namespaces = _NSMAP)[0]
                    if channel_profile in applicable_channel_profiles:
                        default = applicable_channel_profiles[channel_profile]
                        if child.tag != default.tag:
                            raise Exception('{} != {}'.format(child.tag, default.tag))
                        logging.info('Document used a channel profile {}'.format(channel_profile))
                        child = apply_default_to_complex_subelement(child,
                                                                    default)
                    else:
                        logging.info('No applicable channel profile for {}'.format(channel_profile))
                    if channel_profile in applicable_channel_dependencies:
                        for dependent_channel in applicable_channel_dependencies[channel_profile]:
                            if dependent_channel not in included_dependent_channels:
                                logging.info('Adding dependent channel {}'.format(dependent_channel))
                                outdoc.append(deepcopy(self._channels[dependent_channel]))
                                included_dependent_channels.append(dependent_channel)
                    else:
                        logging.info('No channel dependencies for {}'.format(channel_profile))
            elif childtype in [
                cppa('HTTPTransport')
            ]:
                logging.info('@@ Processing HTTPTransport for {}'.format(str(child)))
                if childtype in self._transports:
                    default = self._transports[childtype]
                    child = apply_default_to_complex_subelement(child,
                                                                default)
                logging.info('@@ Processed HTTPTransport for {}'.format(str(child)))
            outdoc.append(child)
        import lxml.etree
        logging.debug('RESULT: {}'.format(lxml.etree.tostring(outdoc,
                                                                  pretty_print=True)))
        return outdoc

def cppa(el):
    return '{{{}}}{}'.format(_NSMAP['cppa'], el)

def pycppa3(el):
    return '{{{}}}{}'.format(_NSMAP['pycppa3'], el)

def apply_default_to_complex_subelement(element, default):
    default = deepcopy(default)
    tag = element.tag
    logging.info('Apply defaults for {}'.format(tag))
    result = etree.Element(tag)
    apply_attribute_defaults(result, element)
    apply_attribute_defaults(result, default)
    if tag not in cppa3_content_model:
        logging.info('{} not in content model, taken from input'.format(tag))
        return element
    else:
        model = cppa3_content_model[tag]
        element_children = list(element)
        default_children = list(default)
        if len(element_children) == 0:
            logging.info('{} children from default'.format(tag))
            for child in default_children:
                if child.get(pycppa3('ifused')) == 'true':
                    logging.info('Skipped {} due to pycppa3="https://pypi.python.org/pypi/cppa3"'.format(child.tag))
                else:
                    result.append(child)
        elif len(default_children) == 0:
            logging.info('{} children from element'.format(tag))
            for child in element_children:
                result.append(child)
        else:
            # both are non-empty
            element_counter = default_counter = 0
            element_content_model_position = default_content_model_position = 0
            already_processed = []
            previous_element = None
            while element_counter < len(element_children) or default_counter < len(default_children):
                if element_counter < len(element_children) and default_counter < len(default_children):
                    element_node = element_children[element_counter]
                    default_node = default_children[default_counter]
                    #apply_attribute_defaults(element_node, default_node)
                    element_content_model_position = cppa3_content_model[tag].index(element_node.tag)
                    default_content_model_position = cppa3_content_model[tag].index(default_node.tag)
                    logging.debug('{} {} {} {} {} {}'.format(element_node.tag,
                                                                element_counter,
                                                                element_content_model_position,
                                                                default_node.tag,
                                                                default_counter,
                                                                default_content_model_position))
                    if element_content_model_position == default_content_model_position:
                        logging.info('X Recursive call for {} [{},{}]'.format(element_node.tag,
                                                                            element_content_model_position,
                                                                            default_content_model_position))
                        result.append( apply_default_to_complex_subelement(element_node,
                                                                           default_node))
                        element_counter += 1
                        default_counter += 1
                        already_processed.append(element_node.tag)


                    elif element_content_model_position < default_content_model_position:
                        logging.debug('Y {} [{},{}]'.format(element_node.tag,
                                                       element_content_model_position,
                                                       default_content_model_position))
                        logging.info('Content for {} taken from element [{},{}]'.format(element_node.tag,
                                                                                        element_content_model_position,
                                                                                        default_content_model_position))
                        result.append(element_node)
                        element_counter += 1
                        already_processed.append(element_node.tag)

                    elif element_content_model_position > default_content_model_position:
                        logging.debug('Z {} [{},{}]'.format(element_node.tag,
                                                       element_content_model_position,
                                                       default_content_model_position))
                        if element_node.tag in already_processed:
                            logging.info('Element {} was already processed'.format(element_node.tag))
                        elif default_node.get(pycppa3('ifused')) == 'true':
                            logging.info('Skipped {} due to pycppa3="https://pypi.python.org/pypi/cppa3"'.format(default_node.tag))
                        else:
                            logging.info('Element {} to be added from default [{}]'.format(default_node.tag,
                                                                                           default_content_model_position))
                            result.append(default_node)
                        default_counter += 1

                    if previous_element != element_node.tag:
                        already_processed.append(previous_element)
                        previous_element = element_node.tag

                if element_counter == len(element_children):
                    previous_element = element_node.tag
                    already_processed.append(previous_element)


                    for child in default_children[default_counter:]:
                        logging.info('A Remaining {} children from default'.format(tag))
                        if child.get(pycppa3('ifused')) == 'true':
                            logging.info('Skipped {} due to pycppa3="https://pypi.python.org/pypi/cppa3"'.format(child.tag))
                        elif child.tag in already_processed:
                            logging.info('Skipped already processed {}'.format(child.tag))
                        else:
                            result.append(child)
                            logging.info('Supported {} due to pycppa3="https://pypi.python.org/pypi/cppa3"'.format(child.tag))
                    default_counter = len(default_children)+1


                elif default_counter == len(default_children):
                    logging.info('B Remaining {} children from element'.format(tag))
                    for child in element_children[element_counter:]:
                        #if child.tag in already_processed:
                        #    logging.info('Skipped already processed {}'.format(child.tag))
                        #else:
                        result.append(child)
                    element_counter = len(element_children)+1

                previous_element = element_node.tag

        logging.debug('Returning result from processing {}'.format(tag))
        return result


def apply_attribute_defaults(provided_element, default_element):
    for att in default_element.attrib:
        if att in ['{https://pypi.python.org/pypi/cppa3}ifused']:
            pass
        elif att not in provided_element.attrib:
            provided_element.set(att, default_element.get(att))
            logging.debug('On {} setting att {} to {} {}'.format(provided_element.tag,
                                                              att,
                                                              default_element.get(att),
                                                              provided_element.tag))

def _pycppa3(el):
    return '{{{}}}{}'.format(_NSMAP['pycppa3'],el)

