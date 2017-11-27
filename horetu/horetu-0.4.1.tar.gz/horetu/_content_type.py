import re
from mimetypes import types_map
types_set = set(types_map.values())
from funmap import funmap

def _is_content_type(x):
    return x.count('/') == 1
    return x in types_set or \
        x.count('/') == 1 and x.split('/', 1)[1].lower().startswith('x-')

@funmap('original', 'parsed')
def ContentType(content_type):
    original = content_type
    if isinstance(content_type, str):
        if content_type in types_map:
            parsed = types_map[content_type]
        else:
            y = re.split(r'[ ;]', content_type)[0]
            if _is_content_type(y):
                parsed = y
            else:
                raise ValueError('Bad content type: %s' % content_type)
    else:
        raise TypeError('Content-type must be str, not %s' % type(content_type).__name__)
    return {'original': original, 'parsed': parsed}
