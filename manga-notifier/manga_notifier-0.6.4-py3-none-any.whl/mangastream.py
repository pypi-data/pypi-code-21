# -*- coding: utf-8 -*-

import re

import requests
from lxml import html


MANGASTREAM_URL = "http://www.mangastream.com"
MANGASTREAM_LIST_URL = "http://mangastream.com/manga"


def generate_html(url):

    response = requests.get(url)
    if response.ok:
        return response.content
    else:
        return None


def re_last_page(string):

    rstr = re.compile("^Last Page \((.+)\)")
    obj = rstr.match(string)

    return obj.group(1)


def get_chapter_pages(url):

    content = generate_html(url)
    root = html.fromstring(content)
    print(url)
    div = root.cssselect('div.subnav-wrapper')
    div = div[0]

    ul = div.cssselect('ul.dropdown-menu')
    ul = ul[1]
    li = ul.cssselect('li')
    a = li[-1].cssselect('a')[0].text_content()
    nb_page = re_last_page(a)

    return int(nb_page)


def get_image_url(url):

    content = generate_html(url)
    root = html.fromstring(content)

    img = root.cssselect('img[id=manga-page]')

    return img[0].attrib['src'][2:]


def get_new_release():

    content = generate_html(MANGASTREAM_URL)
    root = html.fromstring(content)

    for elem in root.xpath('//div[@class="side-nav hidden-xs"]/ul[@class="new-list"]/li'):
        for a in elem.xpath('./a'):
            name = a.xpath('text()')[0].strip()
            chapter = a.find('strong').text.strip()
            title = a.find('em').text.strip()
            url = a.attrib['href'].strip()
            url = "{0}{1}".format(MANGASTREAM_URL, url)

            yield (name, chapter, title, url)


def get_all_manga():

    content = generate_html(MANGASTREAM_LIST_URL)
    root = html.fromstring(content)
    db = {}

    for table in root.xpath('//table[@class="table table-striped"]'):
        for tr in table.xpath('//tr')[1:]:
            name = tr.xpath("./td/strong/a/text()")
            chapter = tr.xpath("./td/a/text()")
            db[name[0]] = chapter[0]

    return db


def check_release(manga):

    new = list()
    for k, v in manga.items():
        for release in get_new_release():
            if release[0] == k and int(release[1]) > int(v):
                new.append(release)

    return new


if __name__ == "__main__":

#    for data in get_new_release():
#        print("url=({})".format(data[3]))

    url = "http://readms.net/r/haikyuu/275/4644/1"
    get_image_url(url)
