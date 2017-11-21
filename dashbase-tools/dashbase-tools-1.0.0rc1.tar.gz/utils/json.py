from __future__ import print_function

import simplejson


def decode_json(raw_data):
    try:
        return simplejson.loads(raw_data)
    except (simplejson.JSONDecodeError, TypeError):
        print('\nError exists when decoding json!')
        print('The response is:')
        print(raw_data)
        if 'The plain HTTP request was sent to HTTPS port' in raw_data:
            print('Please check if you should use HTTPS!')
        raise SystemExit
