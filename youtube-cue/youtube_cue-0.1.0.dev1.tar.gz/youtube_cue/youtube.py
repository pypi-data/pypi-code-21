import json
import logging
import lxml.html
import re
import requests
import time
from lxml.cssselect import CSSSelector

YOUTUBE_COMMENTS_URL = 'https://www.youtube.com/all_comments?v={youtube_id}'
YOUTUBE_COMMENTS_AJAX_URL = 'https://www.youtube.com/comment_ajax'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'


def find_value(html, key, num_chars=2):
    pos_begin = html.find(key) + len(key) + num_chars
    pos_end = html.find('"', pos_begin)
    return html[pos_begin:pos_end]


def extract_comments(html):
    tree = lxml.html.fromstring(html)
    item_sel = CSSSelector('.comment-item')
    text_sel = CSSSelector('.comment-text-content')

    for item in item_sel(tree):
        yield text_sel(item)[0].text_content()


def ajax_request(session, url, params, data, retries=10, sleep=20):
    for _ in range(retries):
        response = session.post(url, params=params, data=data)
        if response.status_code == 200:
            response_dict = json.loads(response.text)
            return response_dict.get('page_token', None), response_dict['html_content']
        else:
            logging.error('Ajax get comments response: %s %s', response.status_code, response.text)
            time.sleep(sleep)


def get_youtube_id(url):
    m = re.search('.*v=(.{11}).*', url)
    if m is None:
        return
    return m.group(1)


def get_comments(url):
    youtube_id = get_youtube_id(url)

    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT

    # Get Youtube page with initial comments
    response = session.get(YOUTUBE_COMMENTS_URL.format(youtube_id=youtube_id))
    html = response.text
    for comment in extract_comments(html):
        yield comment

    page_token = find_value(html, 'data-token')
    session_token = find_value(html, 'XSRF_TOKEN', 4)

    # Get next batch of comments (the same as pressing the 'Show more' button)
    if page_token:
        data = {'video_id': youtube_id,
                'session_token': session_token}
        params = {'action_load_comments': 1,
                  'order_by_time': False,
                  'filter': youtube_id,
                  'order_menu': True}
        response = ajax_request(session, YOUTUBE_COMMENTS_AJAX_URL, params, data)
        if not response:
            return

        page_token, html = response
        for comment in extract_comments(html):
            yield comment
