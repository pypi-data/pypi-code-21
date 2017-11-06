import re
import os
import logging
from collections import OrderedDict
from .manga import _MangaTask

HANDLER_NAME = 'kissmanga'
logger = logging.getLogger(HANDLER_NAME)


class KissmangaTask(_MangaTask):
    """
    Download manga chapters on kissmanga
    """

    handler_name = HANDLER_NAME
    base_url = "http://kissmanga.com"
    uri_re = re.compile(r"^http://kissmanga.com/Manga/(?P<title>[^/]+)/?(?:[^?/]+\?id=(?P<chapter>(\d+)))?$")

    @classmethod
    def from_uri(cls, uri):
        m = cls.uri_re.match(uri)
        if m is None:
            return None
        if m.group('chapter'):
            chapters = [m.group('chapter')]
        else:
            chapters = None
        return cls(title=m.group('title'), chapters=chapters)

    @classmethod
    def build_manga_url(cls, title):
        return '{0}/Manga/{1}'.format(cls.base_url, title)

    @classmethod
    def get_manga_info(cls, dm, title):
        soup = dm.request_soup(cls.build_manga_url(title))

        e = soup.find('link', rel='alternate')
        if e is None:
            return False
        pretty_title = e['title'].rsplit(' manga', 1)[0]
        path_title = cls.uri_re.match(e['href'].replace('/RSS', '')).group('title')

        chapters = OrderedDict()
        # remove the manga title from the chapter name
        for e in soup.find('table', class_='listing').find_all('a')[::-1]:
            chapter_name = e.text.split(pretty_title)[1].strip()
            chapters[chapter_name] = cls.uri_re.match(cls.base_url + e['href']).group('chapter')

        return {'title': pretty_title, 'path': path_title, 'chapters': chapters}


    def get_chapter_pages_paths(self, chapter):
        data = self.request('x?id={0}'.format(chapter)).data
        return re.findall(r' lstImages.push\("([^"]+)"\);', data)

    def get_image_url(self, page):
        return page

