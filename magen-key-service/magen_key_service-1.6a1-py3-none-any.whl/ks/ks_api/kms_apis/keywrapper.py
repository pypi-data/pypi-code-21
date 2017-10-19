import jwt

__author__ = "paulq@cisco.com"
__maintainer__ = "Alena Lifar"
__email__ = "alifar@cisco.com"
__copyright__ = "Copyright(c) 2017, Cisco Systems, Inc."
__version__ = "0.4.1"
__status__ = "alpha"


def jot_key(key_info: dict):
    """
    A Hook to decode bytes into str to let jwt encode key_info properly

    :param key_info: collection of keys
    :type key_info: dict

    :return: encoded key info
    :rtype: bytes
    """
    try:
        for item in key_info['keys']:
            cur = item['key']
            for each in cur.keys():
                cur[each] = cur[each].decode("utf-8") if isinstance(cur[each], bytes) else cur[each]
    except (KeyError, TypeError):
        pass
    encoded = jwt.encode(key_info, 'secret', algorithm='HS256')
    return encoded
