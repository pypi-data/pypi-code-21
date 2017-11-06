import requests
import argparse
from urllib import parse as urlparse
from lxml import html
import re

# local
import goldfinder.misc

def search_raw(search_term):
    params = {
        'mode': 'Basic',
        'vid': 'BRAND',
        'vl(freeText0)': search_term,
        'fn': 'search',
        'tab': 'alma',
        'fctN': 'facet_tlevel',
        'fctV': 'available',
    }

    url = 'http://search.library.brandeis.edu/primo_library/libweb/action/search.do'

    r = requests.get(url, params=params)
    status = misc.check_internet(r)
    if status is None:
        misc.err(status)
    return r


def add_aisle(item):
    return misc.get_in(item, 'directions', 'maps', 0, 'ranges', 0, 'label') or ''

def add_floor(item):
    url = misc.get_in(item, 'directions', 'maps', 0, 'mapurl')
    if url is None:
        return ''
    url = urlparse.urlparse(url)
    params = urlparse.parse_qs(url.query)
    floor = misc.get_in(params, 'floor', 0)
    if floor is None:
        return ''
    else:
        if floor == '5':
            return 'M'
        else:
            return int(floor)

def add_building(item):
    # something like: Please proceed to the mezzanine level of the Goldfarb
    directions = misc.get_in(item, 'directions', 'maps', 0, 'directions')
    matches = re.search(r'(Goldfarb|Farber) building', directions)
    default = 'Goldfarb / Farber'
    if matches is None:
        return default
    groups = matches.groups()
    if len(groups) == 0:
        return default
    else:
        return groups[0]

def add_directions(item):
    if 'directions' in item:
        return

    params = {
        'holding[]': '{library}$${collection}$${call}'.format(**item),
        'alt': 'true',
    }

    url = 'https://brandeis.stackmap.com/json/'

    r = requests.get(url, params=params)
    status = misc.check_internet(r)
    if status is None:
        misc.err(status)
        return

    try:
        directions = r.json()
    except json.decoder.JSONDecodeError as e:
        # ¯\_(ツ)_/¯
        return

    item.update({'directions': misc.get_in(directions, 'results', 0)})

    item['directions']['aisle']    = add_aisle(item)
    item['directions']['floor']    = add_floor(item)
    item['directions']['building'] = add_building(item)

def search(search_term, max_count=10):
    tree = html.fromstring(search_raw(search_term).content)
    results = tree.cssselect('td.EXLSummary')

    def el_to_txt(e):
        if len(e) > 0:
            txt = e[0].text_content()
            return '' if txt is None else txt.strip()
        else:
            return ''

    def fix_call(call_number):
        return call_number.strip('() \t\r\n')

    ret = []
    for result in results:
        availability = result.cssselect('em.EXLResultStatusAvailable')[0]
        summary = result.cssselect('div.EXLSummaryFields')[0]

        exl_prefix = 'span.EXLAvailability'

        item = {
            'library':     availability.cssselect(exl_prefix + 'LibraryName'),
            'collection':  availability.cssselect(exl_prefix + 'CollectionName'),
            'call':        availability.cssselect(exl_prefix + 'CallNumber'),
            'title':       summary.cssselect('h2.EXLResultTitle > a'),
            'author':      summary.cssselect('h3.EXLResultAuthor'),
            'details':     summary.cssselect('span.EXLResultDetails'),
            'year':        summary.cssselect('h3.EXLResultFourthLine'),
        }

        if len(item['call']) == 0:
            continue

        item.update({k: el_to_txt(v) for k, v in item.items()})
        item['call'] = fix_call(item['call'])

        add_directions(item)

        ret.append(item)

        if len(ret) >= max_count:
            break

    return ret

def top(search_term):
    return search(search_term)[0]

def pretty(item):
    ret = []
    ret.append('{title} ({year}, {author})'.format(**item))
    ret.append('{building} {floor}, {aisle}: {callno}'.format(
        **item['directions']))
    return '\n'.join(ret)

def get_directions(
        search_term,
        show_all=False,
        numbered=False,
        width=78,
        raw=False,
        number_postfix='. ',
        indent=8,
        separators=False
        ):
    search_terms = search_term
    ret = []
    results = []

    for search_term in search_terms:
        results.extend(search(search_term, 10 if show_all else 1))

    if len(results) == 0:
        misc.err_exit('no results!')
    elif len(results) == 1 and not numbered:
        raw = True
    elif not raw or numbered:
        numbered = True
        number_col_w = misc.digits(len(results)) + len(number_postfix)

    for result, i in zip(results, range(1, len(results) + 1)):
        if separators and len(search_terms) > 1:
            ret.append('\n' + ' ' * indent + search_term.upper())
            ret.append(       ' ' * indent + '-' * len(search_term))
        if numbered:
            ret.append(misc.format_left(
                pretty(result),
                firstline=(str(i) + number_postfix).rjust(number_col_w),
                reformat=False,
                width=width))
        else:
            ret.append(pretty(result))

    return '\n'.join(ret)

def main():
    parser = argparse.ArgumentParser(
        description='Find materials in the Brandeis Goldfarb / Farber libraries.',
    )

    parser.add_argument('search_term', nargs='+', metavar='TERM',
        help='search term passed directly to OneSearch, '
        'search.library.brandeis.edu. can be a call number, title, or author')
    parser.add_argument('-a', '--all', action='store_true', dest='show_all',
        help='parse all results')
    parser.add_argument('-n', '--numbered', action='store_true',
        help='format output as a numbered list')
    parser.add_argument('-w', '--width', type=int, default=78,
        help='output width')
    parser.add_argument('-r', '--raw', action='store_true',
        help='raw output; don\'t wrap text')
    parser.add_argument('--number-postfix', default='. ',
        help='string to output after the number in numbered output')
    parser.add_argument('-s', '--separators', action='store_true',
        help='output headers between search terms')
    args = parser.parse_args()

    print(get_directions(**args.__dict__))

if __name__ == '__main__':
    main()
