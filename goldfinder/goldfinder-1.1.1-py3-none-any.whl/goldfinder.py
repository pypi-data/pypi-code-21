import requests
import argparse
from urllib import parse as urlparse
from lxml import html
import re

# local
from goldfinder import misc

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

def get_english(directions):
    return misc.get_in(directions, 'maps', 0, 'directions')

def get_aisle(directions):
    return misc.get_in(directions, 'maps', 0, 'ranges', 0, 'label') or ''

def get_floor(directions):
    url = misc.get_in(directions, 'maps', 0, 'mapurl')
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

def get_building(directions):
    """
    gets the building from an item's directions
    """
    # something like: Please proceed to the mezzanine level of the Goldfarb
    default = 'Goldfarb / Farber'
    directions = misc.get_in(directions, 'maps', 0, 'directions')
    if directions is None:
        return default
    matches = re.search(r'(Goldfarb|Farber) building', directions)
    if matches is None:
        return default
    groups = matches.groups()
    if len(groups) == 0:
        return default
    else:
        return groups[0]

def get_raw_directions(item):
    if 'directions' in item:
        return item['directions']

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

    return misc.get_in(directions, 'results', 0)

def add_directions(item):
    directions = get_raw_directions(item)
    item['directions'] = {}
    item['directions']['building'] = get_building(directions)
    item['directions']['floor']    = get_floor(directions)
    item['directions']['aisle']    = get_aisle(directions)
    item['directions']['english']  = get_english(directions)

def search(search_term, max_count=10):
    """
    returns a list of item dicts with the following keys:
    library: usually Main Library
    collection: usually Stacks, sometimes Media or Microfiche
    call: call number, something like B3305.M74 C56 2004
    title: item title
    author: last, first, birth-death, something like 'Collier, Andrew 1944-' but
        can get really verbose
    details: unused (i think?)
    year: something like c2004
    directions: dict containing:
        building: Goldfarb or Farber (unless errors, in which case
            Goldfarb/Farber)
        floor: 1-4 (4 is farber only) or M (goldfarb only)
        aisle: something like 3a
        english: plain-english directions, something like "Please proceed to the
            third floor of Brandeis University Library." but strangely doesn't
            contain the aisle or say "about halfway down" or anything
    """
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
    ret.append('{building} {floor}, {aisle}: {call}'.format(
        call=item['call'],
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
        separators=False,
        verbose=False,
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
        if verbose:
            ret.append(str(result))
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

    parser.add_argument('search_term', nargs='+',
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
    parser.add_argument('--number-postfix', default='. ', metavar='STRING',
        help='string to output after the number in numbered output')
    parser.add_argument('-s', '--separators', action='store_true',
        help='output headers between search terms')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='verbose / debug output; print dicts as well as formatted output')
    args = parser.parse_args()

    print(get_directions(**args.__dict__))

if __name__ == '__main__':
    main()
