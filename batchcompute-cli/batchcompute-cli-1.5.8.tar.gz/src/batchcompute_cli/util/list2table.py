
# -*- coding:utf-8 -*-

import json
from terminal import blue
import re
from ..util import smart_unicode

from ..const import STRING
#from os import environ

# if environ.get('LANG') and 'UTF-8' in environ.get('LANG')\
#         or environ.get('LANGUAGE') and 'UTF-8' in environ.get('LANGUAGE'):
chars_border = {
  'top': '─'
, 'top-mid': '┬'
, 'top-left': '┌'
, 'top-right': '┐'
, 'bottom': '─'
, 'bottom-mid': '┴'
, 'bottom-left': '└'
, 'bottom-right': '┘'
, 'left': '│'
, 'left-mid': '├'
, 'mid': '─'
, 'mid-mid': '┼'
, 'right': '│'
, 'right-mid': '┤'
, 'middle': '│'
}


chars_borderless = {
  'top': ' '
, 'top-mid': ' '
, 'top-left': ' '
, 'top-right': ' '
, 'bottom': '─'
, 'bottom-mid': '-'
, 'bottom-left': '-'
, 'bottom-right': '-'
, 'left': ' '
, 'left-mid': '-'
, 'mid': '─'
, 'mid-mid': '-'
, 'right': ' '
, 'right-mid': ' '
, 'middle': ' '
}

for k in chars_border:
    chars_border[k] = smart_unicode.format_utf8(chars_border[k])
for k in chars_borderless:
    chars_borderless[k] = smart_unicode.format_utf8(chars_borderless[k])


def print_table(cells=[], cols=None, show_no=True, show_header=True, show_border=True):
    chars = chars_border
    if not show_border:
        chars = chars_borderless

    cells_len = len(cells)
    if len(cells)>0 and not cols:
        cols = [k for k in cells[0].keys()]

    if show_no:
        cols.insert(0, 'No.')

    # calc
    col_max_len_map = {}


    for k in cols:
        if isinstance(k,tuple):
            col_max_len_map[k[0]] =  __len(__to_str(k[1])) if show_header else 0
        else:
            col_max_len_map[k] =  __len(__to_str(k)) if show_header else 0


    index = 0
    for item in cells:
        index += 1
        for k in cols:
            if k=='No.':
                s = __to_str(index)
                col_max_len_map[k] = max( __len(s),  col_max_len_map[k] )
            else:
                if isinstance(k,tuple):
                    s = __to_str(item.get(k[0]))
                    s = k[2](s) if __len(k)>=3 else s
                    col_max_len_map[k[0]] = max( __len(s),  col_max_len_map[k[0]] )
                else:
                    s = __to_str(item.get(k))
                    col_max_len_map[k] = max( __len(s),  col_max_len_map[k] )


    hasData = cells_len>0
    colspace = []


    # print cols
    t=[]
    for k in cols:
        if isinstance(k,tuple):
            s = __to_str(k[1])
            t.append(" %s%s " % (blue(s), ' '*(col_max_len_map[k[0]]-__len(s)) ))
            colspace.append('%s' % '-'*(col_max_len_map[k[0]]+2)  )
        else:
            s = __to_str(k)
            t.append(" %s%s " % (blue(s), ' '*(col_max_len_map[k]-__len(s)) ))

            colspace.append( '-'*(col_max_len_map[k]+2)  )

    if show_border:
       print('%s%s%s' % (chars['top-left'], chars['top-mid'].join(colspace), chars['top-right']) )

    if show_header:
        print('%s%s%s' % (chars['left'], chars['middle'].join(t), chars['right']))

        if hasData:
            print('%s%s%s' % (chars['left-mid'], chars['mid-mid'].join(colspace), chars['right-mid']) )
        else:
            print('%s%s%s' % (chars['bottom-left'], chars['bottom-mid'].join(colspace), chars['bottom-right']) )



    # print data
    index = 0
    for item in cells:
        index += 1
        t = []
        for k in cols:
            if k=='No.':
                s = __to_str(index)
                t.append(' %s.%s' % (s, ' '*(col_max_len_map[k]-__len(s)) ) )
            else:
                if isinstance(k, tuple):
                    s = __to_str(item.get(k[0]))
                    s = k[2](s) if __len(k)>=3 else s
                    t.append(' %s%s' % (s, ' '*(col_max_len_map[k[0]]-__len(s)+1) ) )
                else:
                    s = __to_str(item.get(k))
                    t.append(' %s%s' % (s, ' '*(col_max_len_map[k]-__len(s)+1)) )

        print('%s%s%s' % (chars['left'],  chars['middle'].join(t), chars['right']) )

        if not show_header and cells_len > index:
            print('%s%s%s' % (chars['left-mid'], chars['mid-mid'].join(colspace), chars['right-mid']) )


    if hasData and show_border:
        print('%s%s%s' % (chars['bottom-left'], chars['bottom-mid'].join(colspace), chars['bottom-right']) )

def __len(s):

    # '\x1b[38;5;4mName\x1b[0;39;49m: echo'
    if not s:
        return 0

    if isinstance(s, STRING) and re.search(r'\x1b\[[\d;]+m', s):
        s = re.sub(r'\x1b\[[\d;]+m','', s)

    return len(s)

def __to_str(s):
    if isinstance(s, STRING):
        return s
    else:
        return json.dumps(s)

