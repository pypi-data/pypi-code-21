from random import choice
from string import ascii_uppercase

from parameter_encoder import encode_data, decode_data


def get_random_string():
    return ''.join(choice(ascii_uppercase) for i in range(12))


def test():
    for i in range(1,6):
        key = '12345678'
        values = {
            'email_id': get_random_string(),
            'url_id': get_random_string(),
            'contact_id': get_random_string(),
            'link_type': get_random_string(),
            'redirect_url': get_random_string(),
        }
        
        encoded_data = encode_data(values, key)
        decoded_data = decode_data(encoded_data, key)
        
        assert(values == decoded_data), 'The encoding and decoding does not work'
        
        print('Test {} passed succesfully'.format(i))


test()