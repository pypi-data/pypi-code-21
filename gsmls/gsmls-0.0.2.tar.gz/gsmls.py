#!/usr/bin/env python3

"""
http://warren-damiano.idx.rewidx.com/?refine=true&search_by=&sortorder=ASC-ListingPrice&view=grid&map%5Blongitude%5D=-74.36040000000003&map%5Blatitude%5D=40.3724&map%5Bzoom%5D=12&search_zip=07013&search_type=Residential&idx=gsmls&minimum_price=&maximum_price=&search_county=&minimum_bedrooms=&maximum_bedrooms=

http://www.rewidx.com/

http://www.rewidx.com/mls-boards/

http://gsmls.demo.idx.rewidx.com/

https://emailrpt.gsmls.com/public/show_public_report_rpt.do?method=getData&sysid=4745969&ptype=RES&report=onelinerw,clientfull&pubid=249302&Id=128622381_15825&fromPublic=PUBLIC&reportchangeto=true
"""

import re
import requests
import lxml.html
from typing import List

__version__ = '0.0.2'

class GSMLSException(Exception):
    pass

# https://forms.gsmls.com/TownCodes.pdf

counties = {
    "Atlantic": 10,
    "Bergen": 11,
    "Burlington": 12,
    "Camden": 13,
    "CapeMay": 14,
    "Cumberland": 15,
    "Essex": 16,
    "Gloucester": 17,
    "Hudson": 18,
    "Hunterdon": 19,
    "Mercer": 20,
    "Middlesex": 21,
    "Monmouth": 22,
    "Morris": 23,
    "Ocean": 24,
    "Passaic": 25,
    "Salem": 26,
    "Somerset": 27,
    "Sussex": 28,
    "Union": 29,
    "Warren": 30,
}

def get_towns(county):
    response = requests.post("https://www2.gsmls.com/publicsite/propsearch.do?method=getpropertysearch", data={
        "idxId": "",
        "token": "",
        "transactionsought": "purchase",
        "propertytype": "RES",
        "town": "ALL",
        "Continue": "Continue",
        "countycode": counties[county],
        "countyname": county})
    doc = lxml.html.fromstring(response.content)
    sttowns = doc.cssselect('form[name="propsearch"] input[name="sttowns"]')[0].get('value')
    return sttowns.split(',')

def get_listings_inner(county, towns, min_list_price='', max_list_price='', min_bedrooms='', min_bathrooms=''):
    response = requests.post("https://www2.gsmls.com/publicsite/propsearch.do?method=getpropertydetails", data={
        'idxId': '',
        'token': '',
        'minlistprice': min_list_price,
        'maxlistprice': max_list_price,
        'minbedrooms': min_bedrooms,
        'minbaths': min_bathrooms,
        'minacres': '',
        'maxacres': '',
        'lotdesc': '',
        'Search': 'Search',
        'countycode': counties[county],
        'countyname': county,
        'propertytype': 'RES',
        'propertytypedesc': 'Residential',
        'transactionsought': 'purchase',
        'sttowns': ','.join(towns),
    })
    if "which is over the limit of 250" in response.text:
        raise GSMLSException(f"more than 250 listings returned in {county}")
    doc = lxml.html.fromstring(response.content)
    stmlsnums = doc.cssselect('form[name="propsearch"] input[name="stmlsnums"]')[0].get('value')
    return stmlsnums.split(',')

def get_listing_detail(sysid: str): # mlsnums
    response = requests.post(f"https://www2.gsmls.com/publicsite/propsearch.do?method=moredetails&sysid={sysid}", data={
        'idxId': '',
        'token': '',
        'propertytype': 'RES',
        'propertytypedesc': 'Residential',
        'transactionsought': 'purchase',
        'listpricesel': '',
        'sortorder': '',
        'noresultsflag': '',
        'openmap': 'true',
        'mailto': '',
        'subject': '',
        'mailbody': '',
        'pubid': '',
        'mlsnum': '',
        'stmlsnums': sysid, #','.join(mlsnums),
        })
    return response

def get_listings_summary(mlsnums: List[str]):
    response = requests.post(f"https://www2.gsmls.com/publicsite/propsearch.do?method=printablereport", data={
        'idxId': '',
        'token': '',
        'propertytype': 'RES',
        'propertytypedesc': 'Residential',
        'transactionsought': 'purchase',
        'listpricesel': '',
        'sortorder': '',
        'noresultsflag': '',
        'openmap': 'true',
        'mailto': '',
        'subject': '',
        'mailbody': '',
        'pubid': '',
        'mlsnum': '',
        'stmlsnums': ','.join(mlsnums),
        'selmlsnums': mlsnums,
        })

    def get(listing, selector, name, fn):
        try:
            return [fn(x) for x in listing.cssselect(selector) if x.text == name][0]
        except IndexError:
            return None

    def parse_int(x):
        if x is not None:
            try:
                return int(x.replace(',', ''))
            except ValueError:
                pass
        return x

    def parse_money(x):
        if x is not None:
            return parse_int(x.replace('$', '').strip())
        return x

    def parse_float(x):
        if x is not None:
            try:
                return float(x)
            except ValueError:
                pass
        return x

    def parse_str(x):
        if x is not None:
            return re.sub(r'\s+', ' ', x.strip())
        return x

    doc = lxml.html.fromstring(response.content)
    listings = []
    for i, row in enumerate(doc.cssselect('table')):
        listing = {
            "id": get(row, 'b u', "MLS#", lambda x: x.getparent().getnext()).text,
            "price": parse_money(get(row, 'b u', "MLS#", lambda x: x.getparent().getparent().getprevious()).text),
            "address": parse_str(get(row, 'b', 'Address:', lambda x: x.tail)),
            "county": get(row, 'b u', 'County:', lambda x: x.getparent().getnext()).text,
            "city/town": get(row, 'b u', 'Cities/Towns:', lambda x: x.getparent().getnext()).text,
            "style": get(row, 'b u', 'Style:', lambda x: x.getparent().getnext()).text,
            "rooms": parse_int(get(row, 'b u', 'Rooms:', lambda x: x.getparent().getnext()).text),
            "bedrooms": parse_int(get(row, 'b u', 'Bedrooms:', lambda x: x.getparent().getnext()).text),
            "full_baths": parse_int(get(row, 'b u', 'Full Baths:', lambda x: x.getparent().getnext()).text),
            "half_baths": parse_int(get(row, 'b u', 'Half Baths:', lambda x: x.getparent().getnext()).text),
            "total_baths": parse_float(get(row, 'b u', 'Total Baths:', lambda x: x.getparent().getnext()).text),
            "sq_ft": parse_int(get(row, 'b u', 'Sq Ft:', lambda x: x.getparent().getnext()).text),
            "tax": parse_int(get(row, 'b u', 'Tax Amount:', lambda x: x.getparent().getnext()).text),
            "heat_source": parse_str(get(row, 'b u', 'Heat Source:', lambda x: x.getparent().getnext()).text),
            "heat_system": parse_str(get(row, 'b u', 'Heat System:', lambda x: x.getparent().getnext()).text),
            "cool_system": parse_str(get(row, 'b u', 'Cool System:', lambda x: x.getparent().getnext()).text),
            "water": parse_str(get(row, 'b u', 'Water:', lambda x: x.getparent().getnext()).text),
            "sewer": parse_str(get(row, 'b u', 'Sewer:', lambda x: x.getparent().getnext()).text),
            "utilities": parse_str(get(row, 'b u', 'Utilities:', lambda x: x.getparent().getnext()).text),
        }
        listings.append(listing)
    return listings

def get_listings(county, **kwargs):
    mytowns = get_towns(county)
    mlsnums = get_listings_inner(county, mytowns, **kwargs)
    listings = get_listings_summary(mlsnums)
    return listings

from gsmls import get_listing_detail

def get_listing_detail_preview(mlsid):

    def remove_node(x):
        y = x.getparent()
        y.remove(x)

    doc = lxml.html.fromstring(get_listing_detail(mlsid).content)
    content = doc.cssselect('#content .bufer')[0]
    remove_node(content.cssselect('input[title="Select this property"]')[0].getnext())
    remove_node(content.cssselect('input[title="Select this property"]')[0])
    remove_node(content.cssselect('#footer')[0])
    remove_node(content.cssselect('img[alt="More Media"]')[0])
    remove_node(content.cssselect('a[title="Open media link"]')[0])
    media_url = f"<a href='https://www2.gsmls.com/publicsite/propsearch.do?method=getmedia&mlsnum={mlsid}&lstngsysid=0&imagecount=50&openhousesysid='>More Media</a>"
    html = media_url + "\n" + lxml.html.tostring(content).decode('utf-8')
    return html
