#!/usr/bin/env python3

import argparse
from bs4 import BeautifulSoup
import queue
import requests
from urllib.parse import urlparse, urlunparse

DESCRIPTION = """
Cerca recursively searches a website for links to other websites.
The website must be static because a headless browser is not used.
"""

TAG_HANDLERS = {
    'a': lambda el: el.get('href'),
    'form': lambda el: el.get('action'),
    'link': lambda el: el.get('href'),
    'script': lambda el: el.get('src'),
}

def get_links(body):
    """
    Retrieve all external links from an HTML text

    :param body: html string
    """
    soup = BeautifulSoup(body, 'html.parser')
    return [ 
        h(link)
        for tag, h in TAG_HANDLERS.items() for link in soup.find_all(tag)
    ]

def search(domain):
    """
    Search a given domain for blacklisted urls

    :param domain: url to recursively search
    """
    scheme = domain.scheme
    netloc = domain.netloc
    urls = queue.Queue()
    urls.put(domain)
    visited_urls = set()

    while not urls.empty():
        try:
            url = urls.get()
            str_url = url.geturl()
            resp = requests.get(str_url)
            yield resp.status_code, str_url
            visited_urls.add(url)
            links = get_links(resp.text)
            for l in links:
                o = urlparse(l)
                if l in visited_urls:
                    continue
                if o.netloc == '':
                    o = urlparse(urlunparse((scheme, netloc) + o[2:]))
                if o.netloc == netloc:
                    urls.put(o)
        except Exception as err:
            print("Search error :", err)
