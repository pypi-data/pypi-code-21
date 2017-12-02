#!/usr/bin/env python

"""
Code for generating the bibtex key from Google Scholar for the list of papers, whose names are stored
    in the excel sheet.

Referred: https://github.com/venthur/gscholar
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Library to query Google Scholar.

Call the method query with a string which contains the full search
string. Query will return a list of citations.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

try:
    # python 2
    from urllib2 import Request, urlopen, quote
except ImportError:
    # python 3
    from urllib.request import Request, urlopen, quote

try:
    # python 2
    from htmlentitydefs import name2codepoint
except ImportError:
    # python 3
    from html.entities import name2codepoint


import logging
import contextlib
import time
import random
import re
# import os


GOOGLE_SCHOLAR_URL = "https://scholar.google.com"
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'}

FORMAT_BIBTEX = 4
FORMAT_ENDNOTE = 3
FORMAT_REFMAN = 2
FORMAT_WENXIANWANG = 5


logger = logging.getLogger(__name__)


def query(searchstr, outformat=FORMAT_BIBTEX, allresults=False):
    """Query google scholar.

    This method queries google scholar and returns a list of citations.

    Parameters
    ----------
    searchstr : str
        the query
    outformat : int, optional
        the output format of the citations. Default is bibtex.
    allresults : bool, optional
        return all results or only the first (i.e. best one)

    Returns
    -------
    result : list of strings
        the list with citations

    """
    logger.debug("Query: {sstring}".format(sstring=searchstr))
    searchstr = '/scholar?q='+quote(searchstr)
    url = GOOGLE_SCHOLAR_URL + searchstr
    header = HEADERS
    header['Cookie'] = "GSP=CF=%d" % outformat
    request = Request(url, headers=header)
    # time.sleep(5+(random.random()-0.5)*5)
    with contextlib.closing(urlopen(request)) as response:
        # response = urlopen(request)
        html = response.read()
        html = html.decode('utf8')

        # grab the links
        tmp = get_links(html, outformat)


        # follow the bibtex links to get the bibtex entries
        result = list()
        if not allresults:
            tmp = tmp[:1]
        for link in tmp:
            url = GOOGLE_SCHOLAR_URL+link
            request = Request(url, headers=header)
            with contextlib.closing(urlopen(request)) as response:
                # response = urlopen(request)
                bib = response.read()
                bib = bib.decode('utf8')
            result.append(bib)
    return result

def get_links(html, outformat):
    """Return a list of reference links from the html.

    Parameters
    ----------
    html : str
    outformat : int
        the output format of the citations

    Returns
    -------
    List[str]
        the links to the references

    """
    if outformat == FORMAT_BIBTEX:
        refre = re.compile(r'<a href="https://scholar.googleusercontent.com(/scholar\.bib\?[^"]*)')
    elif outformat == FORMAT_ENDNOTE:
        refre = re.compile(r'<a href="https://scholar.googleusercontent.com(/scholar\.enw\?[^"]*)"')
    elif outformat == FORMAT_REFMAN:
        refre = re.compile(r'<a href="https://scholar.googleusercontent.com(/scholar\.ris\?[^"]*)"')
    elif outformat == FORMAT_WENXIANWANG:
        refre = re.compile(r'<a href="https://scholar.googleusercontent.com(/scholar\.ral\?[^"]*)"')
    reflist = refre.findall(html)
    # escape html entities
    reflist = [re.sub('&(%s);' % '|'.join(name2codepoint), lambda m:
                      chr(name2codepoint[m.group(1)]), s) for s in reflist]
    return reflist

