#-*-coding:utf-8-*-
__author__ = 'cchen'

import json
import re
from urlparse import parse_qsl

from base62 import mid2str
from parsers_utils import keep_int, get_url


def parse_weibostore(data):
    """
    Args:
        data (dict): json

    Returns:
        has_next: boolean
        goods: list of [good_id, taobao_id, name, price]
    """
    n_goods = len(data['data']['goodsList'])
    if not n_goods:
        return []
    goods = []
    for good in data['data']['goodsList']:
        good_id = good['iid']
        price = good['price']
        taobao_item_id = good['out_iid']
        name = good['name'].encode('utf-8')
        goods.append([good_id, taobao_item_id, name, price])
    return goods


def parse_weibo(weibo, target_uid=None):
    # media_id
    # timestamp, sent_from
    # forwards, comments, likes
    # media_type[live, video, image], media_url(s)
    # location
    # content(text, urls)
    uid = weibo.find('a', usercard=re.compile('id=')).attrs['usercard']
    uid = dict(parse_qsl(uid))['id']

    if target_uid and uid != target_uid:
        return False

    mid = weibo.attrs['mid']
    mid62 = mid2str(mid)
    created_time = weibo.find('a', attrs={'node-type': 'feed_list_item_date'})
    sent_from = created_time.find_next_sibling('a')
    tms = created_time.attrs['date']
    frm = sent_from.get_text(strip=True).encode('utf-8') if sent_from else ''

    forwards = keep_int(weibo.find('span', attrs={'node-type': re.compile('forward')}).get_text(strip=True))
    comments = keep_int(weibo.find('span', attrs={'node-type': re.compile('comment')}).get_text(strip=True))
    likes = keep_int(weibo.find('span', attrs={'node-type': re.compile('like')}).get_text(strip=True))

    media_type = ''
    media_urls = ''
    media_play = ''
    media_wrap = weibo.find('div', class_=re.compile('media_wrap'))
    if media_wrap:
        picts = media_wrap.find_all('li', class_='WB_pic')
        video = media_wrap.find('li', class_='WB_video')
        if picts:
            media_type = 'image'
            media_urls = (item.img for item in picts)
            media_urls = '|'.join(get_url(item.attrs['src']) for item in media_urls)
        elif video:
            video_action = dict(parse_qsl(video.attrs['action-data']))
            media_type = 'video' if 'type' in video_action else 'live'
            media_urls = get_url(video_action['short_url'], with_query=False) \
                if 'short_url' in video_action else get_url(video_action['url'], with_query=False)
            media_play = video_action.get('play_count', '').encode('utf-8')

    location_icon = weibo.find('i', class_=re.compile('place'))
    location = ''
    if location_icon:
        location_soup = location_icon.parent
        location_soup.i.extract()
        location = location_soup.text.encode('utf-8')
        location_soup.extract()

    content = weibo.find('div', class_='WB_text')
    for icon in content.find_all('i'):
        icon.extract()
    text = content.get_text(separator=' ', strip=True).encode('utf-8')
    urls = dict((item.get_text(strip=True).encode('utf-8'), get_url(item.attrs['href']))
                for item in content.find_all('a'))
    urls = json.dumps(urls) if urls else ''
    return [uid, mid62, tms, text, urls,
            forwards, comments, likes,
            media_type, media_urls, media_play,
            location, frm]
