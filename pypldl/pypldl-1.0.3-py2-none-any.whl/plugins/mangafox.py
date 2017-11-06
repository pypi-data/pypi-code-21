import re
import logging
from collections import OrderedDict
from .manga import _MangaTask

HANDLER_NAME = 'mangafox'
logger = logging.getLogger(HANDLER_NAME)


def normalize_title(title):
    """Normalize a manga title"""
    return title.lower().replace(' ', '_').replace('-', '_')


class MangafoxTask(_MangaTask):
    """
    Download manga chapters on mangafox
    """

    handler_name = HANDLER_NAME
    base_url = "http://mangafox.me"
    uri_re = re.compile(r"^http://mangafox.me/manga/(?P<title>[^/]+)/(?:(?P<chapter>[a-zA-Z0-9./]+)/(?:\d+\.html)?)?$")

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
        return '{0}/manga/{1}/'.format(cls.base_url, title)

    @classmethod
    def get_manga_info(cls, dm, title):
        soup = dm.request_soup(cls.build_manga_url(normalize_title(title)))
        if soup.find(id='searchform'):
            return False

        # get pretty title
        pretty_title = soup.find(id='series_info').find('img')['alt']
        # get path title
        s = soup.find('link', rel='canonical')['href']
        path_title = cls.uri_re.match(s).group('title')

        chapters = OrderedDict()
        # remove the manga title from the chapter name
        for e in soup.find_all('a', class_='tips')[::-1]:
            chapter_name = e.text.replace(pretty_title, '').strip()
            chapters[chapter_name] = cls.uri_re.match(e['href']).group('chapter')

        return {'title': pretty_title, 'path': path_title, 'chapters': chapters}

    def get_chapter_pages_paths(self, chapter):
        soup = self.request_soup(chapter+'/')
        pages = []
        for e in soup.find('select', class_='m').find_all('option'):
            if e.text == 'Comments':
                continue
            pages.append('{0}/{1}.html'.format(chapter, e['value']))
        return pages

    def get_image_url(self, page):
        soup = self.request_soup(page)
        e = soup.find('img', id='image')
        if e is None:
            return None
        else:
            return e['src']

