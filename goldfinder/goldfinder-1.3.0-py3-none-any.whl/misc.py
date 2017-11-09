import textwrap
import math
import requests
import sys

def digits(n):
    return math.floor(math.log10(n)) + 1

def format_left(txt, leader='', width=78, firstline=None, align_leader='right',
        reformat=True):
    firstline = firstline or leader
    margin = len(firstline)
    leader = leader.rjust(margin) if align_leader == 'right' else leader
    width = width - margin

    lines = []
    if reformat:
        lines = textwrap.wrap(txt, width=width)
    else:
        for l in txt.splitlines():
            lines.extend(textwrap.wrap(l, width=width))

    out = [f'{firstline}{lines.pop(0)}']
    for line in lines:
        out.append(f'{leader}{line}')
    return '\n'.join(out)

# https://stackoverflow.com/a/14981125/5719760
def err(*args, **kwargs):
    print('ERROR: ', *args, file=sys.stderr, **kwargs)

def err_exit(*args, **kwargs):
    err(*args, **kwargs)
    sys.exit(-1)

def warn(*args, **kwargs):
    print('WARNING: ', *args, file=sys.stderr, **kwargs)

def check_list_bound(listy, bound):
    length = len(listy)
    return length > bound >= -length

def get_in(dictionary, *keys):
    """
    an abstraction of repeated item-access for nested dictionaries / lists to
    protect against IndexError and KeyError

    ex: dictionary[a][b][3][c] may be converted to
    get_in(dictionary, a, b, 3, c)
    """
    if len(keys) == 0:
        return dictionary
    try:
        return get_in(dictionary[keys[0]], *keys[1:])
    except (IndexError, KeyError) as e:
        return None

def check_internet(request):
    if request.status_code == 200:
        return request
    else:
        return ('Internet problem! '
            '{url} responded with status {code}: {reason}!'.format(
                url=request.url,
                code=request.status_code,
                reason=request.reason))
