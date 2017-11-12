#!/usr/bin/python
# -*- coding: utf-8 -*-

import jsonpickle
import math
import os
import re
import socket
import struct

from urlparse import urlsplit, SplitResult


def normalize_path(path):
    """
    :param path:
    :return:
    """
    ret_path = re.sub('#', '%23', path)
    ret_path = re.sub(' ', '%20', ret_path)

    return ret_path


ip2int = lambda ip_str: struct.unpack('!I', socket.inet_aton(ip_str))[0]
int2ip = lambda n: socket.inet_ntoa(struct.pack('!I', n))


def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata

        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def normalize_str(tmp_str):
    tmp_str = str(tmp_str)
    tmp_str = tmp_str.replace(' ', '')
    tmp_str = tmp_str.replace(',', '.')
    tmp_str = tmp_str.replace('N/A', '')
    tmp_str = tmp_str.replace('Future', '')
    tmp_str = tmp_str.replace('', '')

    return tmp_str


def get_new_ip(ip_address, w_mask):
    """Ip calculator to generate masked Ip address from received params

    :param ip_address: ip address to mask
    :param w_mask: wild card mask
    :return:
    """

    ip_octets = ip_address.split('.')
    mask_octets = w_mask.split('.')
    new_ip = []
    for i in range(len(ip_octets)):
        new_ip.append(str(int(ip_octets[i]) + int(mask_octets[i])))

    return '.'.join(new_ip)


def validate_ip(string):
    """Validate if provided string matches IPv4 with 4 decimal parts
    """

    octets = string.strip('\"\r').split('.')
    if len(octets) != 4:
        return False

    for x in octets:
        if not x.isdigit():
            return False

    for octet in octets:
        i = int(octet)
        if i < 0 or i > 255:
            return False
    return True


def validate_vlan_number(number):
    try:
        if int(number) > 4000 or int(number) < 1:
            return False
    except ValueError:
        return False
    return True


def validate_vlan_range(vlan_range):
    result = None
    for vlan in vlan_range.split(','):
        if '-' in vlan:
            for vlan_range_border in vlan.split('-'):
                result = validate_vlan_number(vlan_range_border)
        else:
            result = validate_vlan_number(vlan)
        if not result:
            return False
    return True


def validate_spanning_tree_type(data):
    spanning_tree_types = ['bridge', 'domain', 'lc-issu', 'loopguard', 'mode', 'mst',
                           'pathcost', 'port', 'pseudo-information', 'vlan']
    if data in spanning_tree_types:
        return True
    return False


def verify_ip_in_range(ip_address, start_addr, end_addr):
    """Validate if provided IP address matches provided network range

    :return: True/False
    """

    start_list = map(int, start_addr.split('.'))
    end_list = map(int, end_addr.split('.'))
    ip_list = map(int, ip_address.split('.'))

    for i in range(len(ip_list)):
        if (ip_list[i] < start_list[i]) or (ip_list[i] > end_list[i]):
            return False

    return True


def validate_mac(str_mac):
    """Validate if provided string matches MAC address pattern
    """
    return re.match('^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$', str_mac.upper())


def get_broad_cast_address(ip, mask):
    """Calculate broadcast IP address for provided IP and subnet
    """
    # fixme need lib
    # network = ipcalc.Network(ip, mask)
    # return str(network.broadcast())


def get_ip_info(ip_str):
    """Get IANA allocation information for the current IP address.
    """
    # fixme need lib
    # ip = ipcalc.IP(ip_str)
    # return ip.info()


def get_subnet_cidr(ip, mask):
    """Get subnet in CIDR format, ex: 255.255.255.0 - 24
    """
    # fixme need lib
    # return ipcalc.Network('{}/{}'.format(ip, mask)).subnet()


def get_network_address(ip, mask):
    """Network slice calculations.

    :param ip: network address
    :param mask: net mask

    :return networkAddress: string

    """
    # fixme need lib
    # return str(ipcalc.Network(ip, mask).network())


# fixme add comments
def get_matrix_from_string(data_str):
    lines = data_str.split('\n')

    lines = filter(
        lambda value:
        value != '',
        lines)

    if len(lines) <= 1:
        return {}

    del lines[-1]
    del lines[0]

    pattern_def_line = re.compile('-{2,}')

    columns_count = 0
    column_lens = []

    for line in lines:
        data = pattern_def_line.findall(line)
        if data:
            lines.remove(line)
            for element in data:
                column_lens.append(len(element))
            break

    data_matrix = {}

    data_index_names = {}

    pattern_not_space = re.compile('\S+')

    for line in lines:
        index = 0
        position = 0
        for column_len in column_lens:
            column_line = line[position: position + column_len]

            column_line_list = pattern_not_space.findall(column_line)
            column_line = ''
            for col_index in range(0, len(column_line_list) - 1):
                column_line += column_line_list[col_index] + ' '
            column_line += column_line_list[len(column_line_list) - 1]

            column_data = []
            if index < len(data_matrix):
                column_data = data_matrix[data_index_names[index]]

                column_data.append(column_line)
            else:
                data_index_names[index] = column_line.lower()
                data_matrix[column_line.lower()] = column_data

            position += column_len + 1
            index += 1

    return data_matrix


def shield_string(data_str):
    iter_object = re.finditer('[\{\}\(\)\[\]\|]', data_str)

    list_iter = list(iter_object)
    iter_size = len(list_iter)
    iter_object = iter(list_iter)

    new_data_str = ''
    current_index = 0

    if iter_size == 0:
        new_data_str = data_str

    for match in iter_object:
        match_range = match.span()

        new_data_str += data_str[current_index:match_range[0]] + '\\'
        new_data_str += data_str[match_range[0]:match_range[0] + 1]

        current_index = match_range[0] + 1

    return new_data_str


def normalize_buffer(input_buffer):
    """
    Method for clear color fro input_buffer and special characters
    """

    color_pattern = re.compile('\[[0-9]+;{0,1}[0-9]+m|\[[0-9]+m|\b|' + chr(27))  # 27 - ESC character

    result_buffer = ''

    match_iter = color_pattern.finditer(input_buffer)

    current_index = 0
    for match_color in match_iter:
        match_range = match_color.span()
        result_buffer += input_buffer[current_index:match_range[0]]
        current_index = match_range[1]

    result_buffer += input_buffer[current_index:]

    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', result_buffer)


def get_dictionary_data(source_dictionary, forbidden_keys):
    destination_dictionary = {}
    for key, value in source_dictionary.iteritems():
        if key in forbidden_keys:
            continue

        destination_dictionary[key] = value

    return destination_dictionary


def get_bit_size(bandwidth):
    bandwidth = bandwidth.lower()
    multiplier = 1
    if re.search('kbit/sec', bandwidth):
        multiplier = 2 ** 10
    elif re.search('mbit/sec', bandwidth):
        multiplier = 2 ** 20
    elif re.search('gbit/sec', bandwidth):
        multiplier = 2 ** 30

    bits = int(re.search('\d+', bandwidth).group()) * multiplier

    return math.log10(bits)


def serialize_to_json(result, unpicklable=False):
    """Serializes output as JSON and writes it to console output wrapped with special prefix and suffix

    :param result: Result to return
    :param unpicklable: If True adds JSON can be deserialized as real object.
                        When False will be deserialized as dictionary
    """

    json = jsonpickle.encode(result, unpicklable=unpicklable)
    result_for_output = str(json)
    return result_for_output


class UrlParser(object):
    SCHEME = 'scheme'
    NETLOC = 'netloc'
    PATH = 'path'
    FILENAME = 'filename'
    QUERY = 'query'
    FRAGMENT = 'fragment'
    USERNAME = 'username'
    PASSWORD = 'password'
    HOSTNAME = 'hostname'
    PORT = 'port'

    @staticmethod
    def parse_url(url):
        parsed = urlsplit(url)
        result = {}
        for attr in dir(UrlParser):
            if attr.isupper() and not attr.startswith('_'):
                attr_value = getattr(UrlParser, attr)
                if hasattr(parsed, attr_value):
                    value = getattr(parsed, attr_value)
                    if attr_value == UrlParser.PATH:
                        path, filename = os.path.split(value)
                        result[UrlParser.PATH] = path
                        result[UrlParser.FILENAME] = filename
                    else:
                        result[attr_value] = value
        return result

    @staticmethod
    def build_url(url):
        url_result = {UrlParser.QUERY: '', UrlParser.FRAGMENT: ''}
        if not url or UrlParser.SCHEME not in url or not url[UrlParser.SCHEME]:
            raise Exception('UrlParser:build_url', 'Url dictionary is empty or missing key values')

        url_result[UrlParser.SCHEME] = url[UrlParser.SCHEME]

        if UrlParser.NETLOC in url and url[UrlParser.NETLOC]:
            if UrlParser.USERNAME in url \
                    and url[UrlParser.USERNAME] \
                    and url[UrlParser.USERNAME] in url[UrlParser.NETLOC]:
                url_result[UrlParser.NETLOC] = url[UrlParser.NETLOC]
        if UrlParser.NETLOC not in url_result:
            url_result[UrlParser.NETLOC] = url[UrlParser.HOSTNAME]
            if UrlParser.PORT in url and url[UrlParser.PORT]:
                url_result[UrlParser.NETLOC] += str(url[UrlParser.PORT])
            if UrlParser.USERNAME in url and url[UrlParser.USERNAME]:
                credentials = '{}@'.format(url[UrlParser.USERNAME])
                if UrlParser.PASSWORD in url and url[UrlParser.PASSWORD]:
                    credentials = '{}:{}@'.format(url[UrlParser.USERNAME], url[UrlParser.PASSWORD])
                url_result[UrlParser.NETLOC] = credentials + url_result[UrlParser.NETLOC]

        url_result[UrlParser.PATH] = url[UrlParser.FILENAME]
        if UrlParser.PATH in url and url[UrlParser.PATH]:
            url_result[UrlParser.PATH] = url[UrlParser.PATH] + '/' + url_result[UrlParser.PATH]
            url_result[UrlParser.PATH] = re.sub('//+', '/', url_result[UrlParser.PATH])

        if UrlParser.QUERY in url and url[UrlParser.QUERY]:
            url_result[UrlParser.QUERY] = url[UrlParser.QUERY]

        result = SplitResult(**url_result)
        return result.geturl()
