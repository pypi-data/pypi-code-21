import argparse
from urllib import parse as urlparse
import re
import sys

import zs.bibtex
from lxml import html
import requests
import bibtexparser

# local
from goldfinder import misc

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
    # item['directions']['english']  = get_english(directions)

def request_page_raw(uid, extra_params):
    params = {
        'rfr_id': 'info:sid/primo.exlibrisgroup.com-BRAND_ALMA',
        'rft_dat': f'ie=01BRAND_INST:{uid}',
        'svc_dat': 'getit',
    }

    params.update(extra_params)

    url = 'https://na01.alma.exlibrisgroup.com/view/uresolver/01BRAND_INST/openurl'

    r = requests.get(url, params=params)
    status = misc.check_internet(r)
    if status is None:
        misc.err(status)
    return r

def _el_to_txt(e):
    """
    takes a list or variable of type lxml.html.HtmlElement
    """
    if isinstance(e, list) and len(e) > 0:
        return _el_to_txt(e[0])
    elif isinstance(e, html.HtmlElement):
        txt = e.text_content()
        return None if txt is None else txt.strip()
    else:
        raise ValueError('input MUST be an lxml.html.HtmlElement')

def _fix_call_number(call_number):
    return call_number.strip('() \t\r\n')

def itemize_element_deep(el):
    """
    el is a td.EXLSummary

    Sometimes books are available both in the library and online, in which
    case OneSearch doesn't display the call number??? so we have to grab a
    uid

    books like: QA76.9.H85 R37 2000
    """
    # something like 'snippet_BRAND_ALMA21229408670001921'
    uid = el.cssselect('p.EXLResultSnippet')[0].attrib['id']
    # trim the 'snippet_BRAND_ALMA' (18 chars)
    uid = uid[18:]

    tree = tree_request(request_page_raw, uid)
    holding_info = tree.cssselect('ul.holdingInfo')[0]

    pre = lambda x: _el_to_txt(holding_info.cssselect(f'span.item{x}'))

    item = {
        'library':    pre('LibraryName'),
        'collection': pre('LocationName'),
        'call':       pre('AccessionNumber'),
    }

    return item

def itemize_element_light(el):
    """
    el is a td.EXLResultStatusAvailable
    """

    pre = lambda x: _el_to_txt(
        el.cssselect('span.EXLAvailability' + x))

    item = {
        'library':     pre('LibraryName'),
        'collection':  pre('CollectionName'),
        'call':        pre('CallNumber'),
    }

    return item

def itemize_element(el):
    """
    el is a td.EXLSummary
    """
    availability = el.cssselect('em.EXLResultStatusAvailable')
    availability = availability[0] if len(availability) > 0 else None
    summary = el.cssselect('div.EXLSummaryFields')
    summary = summary[0] if len(summary) > 0 else None

    pre = lambda x: _el_to_txt(summary.cssselect(x.format('EXLResult')))

    item = {
        'title':   pre('h2.{}Title > a'),
        'author':  pre('h3.{}Author'),
        'details': pre('span.{}Details'),
        'year':    pre('h3.{}FourthLine'),
    }

    if 'The library also has physical copies.' in availability.text_content():
        # no call number here!!! we gotta go deeper
        item.update(itemize_element_deep(el))
    else:
        item.update(itemize_element_light(availability))

    # if len(item['call']) == 0:
        # return item

    item['call'] = _fix_call_number(item['call'])

    add_directions(item)

    return item

def search_raw(search_term, extra_params={}):
    params = {
        'mode': 'Basic',
        'vid': 'BRAND',
        'vl(freeText0)': search_term,
        'fn': 'search',
        'tab': 'alma',
        'fctN': 'facet_tlevel',
        'fctV': 'available',
    }

    params.update(extra_params)

    url = 'http://search.library.brandeis.edu/primo_library/libweb/action/search.do'

    r = requests.get(url, params=params)
    status = misc.check_internet(r)
    if status is None:
        misc.err(status)
    return r

def tree_request(func, search_term, extra_params={}):
    return html.fromstring(func(search_term, extra_params).content)

def search(search_term, max_count=10, extra_params={}):
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
            contain the aisle or say "about halfway down" or anything.
            currently disabled.
    """
    tree = tree_request(search_raw, search_term, extra_params)
    results = tree.cssselect('td.EXLSummary')

    ret = []
    for result in results:
        item = itemize_element(result)
        ret.append(item)

        if len(ret) >= max_count:
            break

    return ret

def pretty(item):
    ret = []
    ret.append('{title} ({author}, {year})'.format(**item))
    if 'directions' in item:
        ret.append('{building} {floor}, {aisle}: {call}'.format(
            call=item['call'],
            **item['directions']))
    return '\n'.join(ret)

def get_directions(
        search_term,
        amount=1,
        numbered=False,
        width=78,
        raw=False,
        number_postfix='. ',
        indent=8,
        separators=False,
        verbose=False,
        continue_numbering=False,
        suppress=False,
        extra_search_params={},
        start_number=1,
        **kwargs # completely ignored
        ):

    ret = []
    results = []
    total_results = 0

    for search_t in search_term:
        if verbose:
            print(f'searching for `{search_t}`')
        search_results = search(search_t, amount, extra_search_params)
        total_results += len(search_results)
        results.append(search_results)

    if total_results == 0:
        return ''
    elif total_results == 1 and not numbered:
        raw = True
    elif not raw or numbered or (total_results > 1 and not raw):
        numbered = True
        number_col_w = misc.digits(total_results) + len(number_postfix)

    i = start_number

    if suppress:
        ret = []
        for result_group in results:
            ret.extend(result_group)
        return ret

    for search_t, search_results in zip(search_term, results):
        if separators:
            ret.append('\n' + ' ' * indent + search_t.upper())
            ret.append(       ' ' * indent + '-' * len(search_t))
        if not continue_numbering:
            i = start_number
        for result in search_results:
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
            i += 1

    return '\n'.join(ret)

def search_from_bib(bib):
    """
    bib: a bibliography object
    """
    # some shit from the onesearch api
    magic = '1219566' # ???

    bib2onesearch = {
        'freeText': {
            'title': 'title',
            'author': 'creator',
            'keywords': 'sub',
            'issn': 'issn',
            'isbn': 'isbn',
            'publisher': 'lsr02',
        },
        'elsewhere': {
            'year': 'vl(drStartYear7)',
            'endyear' : f'vl({magic}22UI7)',
            'language': f'vl({magic}10UI6)',
        }
    }

    n = 0
    def fill_free(subj, txt):
        nonlocal n
        nonlocal params
        if n > 3:
            return

        n_magic = {
            0: f'vl({magic}13UI0)',
            1: f'vl({magic}15UI1)',
            2: f'vl({magic}16UI2)',
            3: f'vl({magic}17UI3)',
        }

        params[f'vl(freeText{n})'] = txt
        params[n_magic[n]] = subj
        n += 1

    def set_other(key, val):
        nonlocal params
        if key == 'year':
            params[bib2onesearch['elsewhere']['year']] = val
            params[bib2onesearch['elsewhere']['endyear']] = str(int(val) + 1)
            # set month / day to jan 1
            params[f'vl({magic}18UI7)'] = '01'
            params[f'vl({magic}19UI7)'] = '01'
            params[f'vl({magic}20UI7)'] = '01'
            params[f'vl({magic}21UI7)'] = '01'

        elif key == 'language':
            params[bib2onesearch['elsewhere']['language']] = val

    params = {
        'mode': 'Advanced',
        'vl(freeText0)': '',
        'vl(freeText1)': '',
        'vl(freeText2)': '',
        'vl(freeText3)': '',
    }

    # keys ranked by specificity
    rank = [
        'isbn',
        'issn',
        'title',
        'author',
    ]

    # fill priority items first
    for item in rank:
        if item in bib:
            fill_free(bib2onesearch['freeText'][item], bib[item])
            del bib[item]

    # fill in gaps next
    for bibkey, OneSearch in bib2onesearch['freeText'].items():
        if n == 4:
            break
        elif bibkey in bib:
            fill_free(OneSearch, bib[bibkey])

    for bibkey in bib2onesearch['elsewhere'].keys():
        if bibkey in bib:
            set_other(bibkey, bib[bibkey])

    for i in range(4):
        params[f'vl(1UIStartWith{i})'] = 'contains'
        params[f'vl(boolOperator{i})'] = 'AND'

    return params

def stdin_lines():
    ret = []
    for line in sys.stdin.readlines():
        ret.append(line.strip())
    return ret

def regular_search(args):
    """
    args: an argparse object
    """
    args_dict = args.__dict__
    if not args.search_term:
        # read from stdin
        args_dict['search_term'] = stdin_lines()

    return get_directions(**args_dict)

def bib_search(args):
    """
    args: an argparse object
    """
    ret = []
    if not args.bibtex:
        args['bibtex'] = stdin_lines()
    args_dict = args.__dict__.copy()
    del args_dict['search_term']

    n = 1
    for bibtex_file in args.bibtex:
        with open(bibtex_file, encoding='utf-8') as bibfile:
            if not args.continue_numbering:
                n = 1
            citations = bibtexparser.load(bibfile)
            for citation in citations.entries:
                params = search_from_bib(citation)
                item = get_directions([''],
                    extra_search_params=params,
                    start_number=n,
                    **args_dict)
                if len(item.strip()):
                    ret.append(item)
                    n += 1
    return '\n'.join(ret)

def main():
    parser = argparse.ArgumentParser(
        description='Find materials in the Brandeis Goldfarb / Farber libraries.',
    )

    parser.add_argument('-a', '--amount', type=int, metavar='N', default=1,
        help='parse N results (max 10)')
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
    parser.add_argument('-c', '--continue-numbering', action='store_true',
        help='don\'t reset list numbering between search terms')
    parser.add_argument('--verbose', action='store_true',
        help='verbose / debug output; print dicts as well as formatted output')
    parser.add_argument('--suppress', action='store_true',
        help='don\'t output formatted data; useful with --verbose')

    parser.add_argument('-b', '--bibtex', nargs='*',
        help='bibtex file to process; if no arguments are present, reads '
        'from STDIN as bibtex. prioritized over search_term, i.e. search_term '
        'will be ignored if -b is present')
    parser.add_argument('search_term', nargs='*',
        help='search term passed directly to OneSearch, '
        'search.library.brandeis.edu. can be a call number, title, or author')

    args = parser.parse_args()
    func = regular_search
    if args.bibtex:
        func = bib_search

    print(func(args))

if __name__ == '__main__':
    main()
