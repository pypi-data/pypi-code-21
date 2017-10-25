import pprint
import re

import sys
import urllib
from urlparse import urlparse

import requests


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    if sys.version_info < (3, 0):
        value = str(value).decode()
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode()
    value = re.sub('[^\w\s-]', '', value).strip().lower()

    return re.sub('[-\s]+', '-', value)


def sort_video_links(video_links):
    return sorted(video_links, key=lambda k: re.search(r'\d+', k['res']).group())

"""
def drive_link_generator(link, session=None):
    if session is None:
        session = requests.Session()
    url = urlparse(link)
    docid = url.path.split('/')[3]
    req = session.get('https://drive.google.com/get_video_info?docid=' + docid + '&authuser=0')
    drive_info_text = req.text
    drive_info_dict = {}
    for part in drive_info_text.split('&'):
        drive_info_dict[part.split('=')[0]] = part.split('=')[1]
    print(drive_info_dict)
    stream_map = drive_info_dict['url_encoded_fmt_stream_map']
    stream_map = urllib.unquote(stream_map).decode('utf8')
    print(stream_map)
    stream_parts = stream_map.split(',')
    stream_map = []
    for stream_part in stream_parts:
        link_parts = stream_part.split('&')
        link = {}
        for link_part in link_parts:
            link[link_part.split('=')[0]] = link_part.split('=')[1]
        pprint.pprint(link)
        stream_map.append(link)
    print(session.cookies)
"""