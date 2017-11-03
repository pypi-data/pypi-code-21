#!/usr/bin/env python

import re

import requests
from lxml import html


simple_episode = r"""(.*)         # Title
                    [ .]
                    [Ss](\d{1,2}) # Season
                    [Ee](\d{1,2}) # Episode
                    [ .a-zA-Z]*   # Space, period, or words like PROPER/Buried
                    (\d{3,4}p)?   # Quality
                    """


def process_title(fullname):
    tv = re.findall(simple_episode, fullname, re.VERBOSE)
    if(any(tv)):
        show = tv[0][0].replace(".", " ")
        season = tv[0][1]
        episode = tv[0][2]
        quality = (tv[0][3] if len(tv[0][3]) > 0 else "480p")
#        display_show(show, season, episode, quality)

        return (show, season, episode, quality)


def display_show(show, season, episode, quality):
    print("---------- TV ----------")
    print("Show: {}".format(show))
    print("Season: {}".format(season))
    print("Episode: {}".format(episode))
    print("Quality: {}".format(quality))


def process_countdown_page(content):
    root = html.fromstring(content)

    table = root.cssselect('table.forum_header_border')
    table = table[1]

    table = table.cssselect('table')
    table = table[0]

    for tr in table.cssselect('tr[name=hover]'):
        tds = tr.cssselect('td')
        show = tds[1].cssselect('a')[0].text_content()
        release_date = tds[2].text_content()
        countdown = tds[3].cssselect('b')[0].text_content()

        yield show, release_date, countdown


def process_showlist_page(content):
    root = html.fromstring(content)

    table = root.cssselect('table.forum_header_border')
    table = table[1]
    for tr in table.cssselect('tr[name=hover]'):
        a = tr.cssselect('td a')
        title = a[0].text_content()
        link = a[0].attrib['href']

        yield title, link


def process_show_page(content):
    root = html.fromstring(content)

    table = root.cssselect('table.forum_header_noborder')
    table = table[0]
    for tr in table.cssselect('tr.forum_header_border'):
        title, magnet, torrent, mirror = (None, None, None, None)
        a = tr.cssselect('td a.epinfo')
        if(a):
            title = a[0].text_content()
        a = tr.cssselect('td a.magnet')
        if(a):
            magnet = a[0].attrib['href']
        a = tr.cssselect('td a.download_1')
        if(a):
            torrent = a[0].attrib['href']
        a = tr.cssselect('td a.download_3')
        if(a):
            mirror = a[0].attrib['href']

        yield title, magnet, torrent, mirror
