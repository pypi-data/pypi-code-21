#!/usr/bin/env python

import random
import difflib

import requests

from .parser import process_showlist_page

EZTV_SHOWS_URL = "https://eztv.ag/showlist"


def whatdoyoumean(shows, name):
    matches = difflib.get_close_matches(name, shows, 3)
    error_msg = '\n\nDid you mean one of these?\n    %s' % '\n    '.join(matches)
    print(error_msg)


def get_user_agent():
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    ]

    uint = random.randint(0, 2)
    ua = USER_AGENTS[uint]

    return ua


def do_request(url):
    ua = get_user_agent()

    headers = requests.utils.default_headers()

    headers.update({'User-Agent': ua})

    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r
    else:
        r.raise_for_status()


def update_shows():

    r = do_request(EZTV_SHOWS_URL)

    for show, link in process_showlist_page(r.content):
        yield (show, link)


def write_shows(filename="/Users/jpradier/shows.txt"):

    with open(filename, 'a') as fp:
        for t in update_shows():
            line = ['[', '"', t[0], '"', ',', ' "', t[1], '"', ']', ',']
            fp.write("\t")
            fp.write("".join(line))
            fp.write("\n")


