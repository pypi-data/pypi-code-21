#-*-coding:utf-8-*-
__author__ = 'cchen'

import re

from parsers_utils import parse_url_args


def retrieve_live_id(live_soup):
    try:
        live_url = live_soup.attrs['href']
        live_id = live_url[live_url.index('/l/') + 3:live_url.index('.html')]
        return live_id
    except (ValueError, KeyError, TypeError):
        pass


def parse_liveroom(soup):
    usercard = soup.find('div', class_='info')
    memberid, weiboid, nickname, level, gold, maxonline = parse_usercard(usercard)
    storecard = soup.find('div', class_='mystore')
    storeonside = parse_store(storecard)
    return [memberid, weiboid, nickname, level, gold, maxonline, storeonside]


def parse_usercard(usercard):
    link = usercard.find('a', target='_blank')
    memberid = parse_url_args(link.attrs['href'])['memberid']
    weiboid = link.attrs.get('weibo_openid', '')
    nickname = link.text.encode('utf-8')
    level = re.sub('[^0-9]', '', ' '.join(usercard.find('div', class_='level').attrs['class']))

    gold = usercard.find('span', class_='J_goldcoin')
    gold = gold.text.encode('utf-8') if gold else ''
    maxonline = usercard.find('span', class_='J_maxonline')
    maxonline = re.sub(u'\u4eba', '', maxonline.text).encode('utf-8') if maxonline else ''

    return [memberid, weiboid, nickname, level, gold, maxonline]


def parse_store(storecard):
    return 1 if storecard else 0
