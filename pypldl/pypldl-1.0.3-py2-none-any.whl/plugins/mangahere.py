import re
import os
import logging
from collections import OrderedDict
from .manga import _MangaTask

HANDLER_NAME = 'mangahere'
logger = logging.getLogger(HANDLER_NAME)


def normalize_title(title):
    """Normalize a manga title"""
    return title.lower().replace(' ', '_').replace('-', '_')


class MangahereTask(_MangaTask):
    """
    Download manga chapters on mangahere
    """

    handler_name = HANDLER_NAME
    base_url = "http://www.mangahere.co"
    uri_re = re.compile(r"^(?:http:)?//www.mangahere.co/manga/(?P<title>[^/]+)/(?:(?P<chapter>[a-z0-9./]+)/)?$")

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
        if soup.find(class_='error_404'):
            return False

        # get pretty title
        s = soup.find('meta', property='og:title')['content']
        pretty_title = s.split(' manga, read ')[0]
        # get path title
        s = soup.find('meta', property='og:url')['content']
        path_title = cls.uri_re.match(s).group('title')

        chapters = OrderedDict()
        # remove the manga title from the chapter name
        use_name = True
        for e in soup.find('div', class_='detail_list').find_all('a', class_='color_0077')[::-1]:
            chapter_name = e.text.replace(pretty_title, '').strip()
            path = cls.uri_re.match(e['href']).group('chapter')
            if use_name:
                if chapter_name in chapters:
                    # duplicate name: use pathes instead of names
                    chapters = { p: p for p in chapters.values() }
                    use_name = False
            chapters[chapter_name if use_name else path] = path

        return {'title': pretty_title, 'path': path_title, 'chapters': chapters}


    def get_chapter_pages_paths(self, chapter):
        soup = self.request_soup(chapter+'/')
        pages = []
        for e in soup.find('select', class_='wid60').find_all('option'):
            page_name = e['value'].rsplit('/', 1)[-1]
            if page_name == 'featured.html':
                continue  # ignore "featured" pages with ads
            pages.append('{0}/{1}'.format(chapter, page_name))
        return pages

    def get_image_url(self, page):
        soup = self.request_soup(page)
        e = soup.find('img', id='image')
        if e is None:
            return None
        else:
            return e['src']

