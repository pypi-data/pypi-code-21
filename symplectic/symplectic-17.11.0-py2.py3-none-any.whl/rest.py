"""
Parse ReST files
"""

import io

from xml.etree import ElementTree as ET

from docutils import core as ducore

from symplectic import posts


def _parse_docinfo(docinfo):
    parsed = ET.fromstring(docinfo)
    ret = {}
    for elem in parsed.find('tbody').findall('tr'):
        field = elem.find('th').text.strip(':').lower()
        value = elem.find('td').text
        ret[field] = value
    return ret


def _parse_rest_files(fnames):
    overrides = {'input_encoding': 'utf-8',
                 'initial_header_level': 2}
    for fname in fnames:
        with io.open(fname, "r", encoding='utf-8') as filep:
            input_string = filep.read()
        parts = ducore.publish_parts(
            source=input_string, source_path=fname,
            writer_name='html', settings_overrides=overrides)
        docinfo = _parse_docinfo(parts['docinfo'])
        yield parts, docinfo


def pages_from_rest_files(fnames):
    """
    Read pages from ReST files
    """
    ret = []
    for parts, docinfo in _parse_rest_files(fnames):
        page = posts.Page(title=parts['title'],
                          contents=parts['body'],
                          slug=docinfo['slug'],
                          author=docinfo['author'])
        ret.append(page)
    return ret


def posts_from_rest_files(fnames):
    """
    Read posts from ReST files
    """
    ret = []
    for parts, docinfo in _parse_rest_files(fnames):
        page = posts.Post(title=parts['title'],
                          contents=parts['body'],
                          slug=docinfo['slug'],
                          author=docinfo['author'],
                          date=docinfo['date'])
        ret.append(page)
    return ret
