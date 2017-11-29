# -*- coding: utf-8 -*-

import re
from collections import OrderedDict

import requests
from lxml import html

all = ['all_manga', 'chapter_number_pages', 'image_url', 'verify_release']


MANGASTREAM_URL = "http://www.mangastream.com"
MANGASTREAM_LIST_URL = "http://mangastream.com/manga"

MANGA_EXCEPTIONS = {
    "Haikyuu": "Haikyuu!!"
}


def generate_html(url):
    """Return the html page content

    Parameters
    ----------
    url : str
        http url.

    Returns
    -------
    bytes
        page's content or raise Exception
    """
    response = requests.get(url, timeout=5)
    if response.status_code != 200:
        response.raise_for_status()
    else:
        return response.content


def last_page(string):
    """Parse the page number of a chapter

    Parameters
    ----------
    string : str
        string to parse
    Returns
    -------
    str
        the last page number
    """

    last_str = re.compile("^Last Page \((.+)\)")
    obj = last_str.match(string)

    return obj.group(1)


def last_chapter(string):
    """Return the last chapter number

    Parameters
    ----------
    string : str
        string to parse
    Returns
    -------
    str
        the last chapter released
    """

    last_str = re.compile("^(.+) - (.+)")
    obj = last_str.match(string)

    return obj.group(1)


def chapter_number_pages(url):
    """Return the number of pages

    Parameters
    ----------
    url : str
        the chapter url

    Returns
    -------
    str
        the page number of a chapter
    """

    content = generate_html(url)
    root = html.fromstring(content)

    div = root.cssselect('div.subnav-wrapper')
    # cssselect return a list. In that case, a list of one element
    div = div[0]

    ul = div.cssselect('ul.dropdown-menu')
    ul = ul[1]
    li = ul.cssselect('li')
    a = li[-1].cssselect('a')[0].text_content()
    nb_page = last_page(a)

    return int(nb_page)


def image_url(url):
    """Return the url of the chapter

    Parameters
    ----------
    url : str
        the chapter url

    Returns
    -------
    str
        the url of the chapter
    """
    content = generate_html(url)
    root = html.fromstring(content)

    img = root.cssselect('img[id=manga-page]')

    return img[0].attrib['src'][2:]


def new_release():
    """
    Yield all new chapters
    Generate tuple of new chapters released.

    Yields
    ------
    tuple
        the next name, chapter, title, url
    """
    content = generate_html(MANGASTREAM_URL)
    root = html.fromstring(content)

    xpath_str = '//div[@class="side-nav hidden-xs"]/ul[@class="new-list"]/li'
    for elem in root.xpath(xpath_str):
        for a in elem.xpath('./a'):
            name = a.xpath('text()')[0].strip()
            chapter = a.find('strong').text.strip()
            title = a.find('em').text.strip()
            url = a.attrib['href'].strip()

            yield (name, chapter, title, url)


def all_manga():
    """Return all the manga hosted in Mangastream.com

    Returns
    -------
    OrderedDict
        each manga with the last chapter and url
    """

    content = generate_html(MANGASTREAM_LIST_URL)
    root = html.fromstring(content)
    series = OrderedDict()

    xpath_str = '//table[@class="table table-striped"]'
    for table in root.xpath(xpath_str):
        for tr in table.xpath('//tr')[1:]:

            # For each manga, get the two <a> tag
            td = tr.xpath("./td")

            # Get the manga info
            tag = td[0].xpath("./strong/a")[0]
            manga = tag.text_content()

            # Get the last chapter info
            tag = td[1].xpath("./a")[0]
            chapter = last_chapter(tag.text_content())
            chapter_url = tag.attrib['href']
            series[manga] = OrderedDict({
                "chapter": chapter,
                "url": chapter_url
            })

    return series


def verify_release(manga):
    """If there are new chapters Then yield it

    Paramaters
    ----------
    manga : dict
        mangas to check chapter release

    Returns
    -------
    list
        new chapter released
    """
    out = list()
    for k, v in manga.items():
        for release in new_release():
            if release[0] == k and int(release[1]) > int(v['chapter']):
                out.append(release)

    # When multiple chapters of a manga are out
    # We need to sort them in order to write the last chapter in the database
    sorted_out = sorted(out, key=lambda out: out[1])

    return sorted_out
