

import requests
from lxml import html


MANGASTREAM_URL = "http://www.mangastream.com"
MANGASTREAM_LIST_URL = "http://mangastream.com/manga"


def generate_html(url):
    response = requests.get(url)
    if response.ok:
        return response.content


def get_new_release():

    content = generate_html(MANGASTREAM_URL)
    root = html.fromstring(content)

    for elem in root.xpath('//div[@class="side-nav hidden-xs"]/ul[@class="new-list"]/li'):
        for a in elem.xpath('./a'):
            name = a.xpath('text()')[0].strip()
            chapter = a.find('strong').text.strip()
            title = a.find('em').text.strip()
            url = a.attrib['href'].strip()

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

    for data in get_new_release():
        print("url=({})".format(data[3]))
