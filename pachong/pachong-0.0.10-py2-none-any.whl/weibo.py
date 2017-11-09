#-*-coding:utf-8-*-
__author__ = 'cchen'

import json
import random
import re
import time
from urlparse import urljoin

from bs4 import BeautifulSoup

from pachong import PaChong
from weibo_login import WeiboLogin
from weibo_parsers import parse_weibostore, parse_weibo


class Weibo(PaChong):

    def login(self, username, password):
        self.session = WeiboLogin(self.session).login(username, password)

    def streaming(self, fp_timeline, fp_uids, period=30):
        whatwehave = self.read_records(fp_timeline, col_id=(0, 1))
        trgt_users = self.read_records(fp_uids, col_id=1) if not isinstance(fp_uids, (set, list)) else set(fp_uids)

        while True:
            new_weibos = []
            for uid in trgt_users:
                has_next, weibos, page_property = self._crawl_timeline_feed(uid, page=1, pagebar=-1)
                for weibo in weibos:
                    uid_mid = weibo[0] + '_' + weibo[1]
                    if uid_mid in whatwehave:
                        continue
                    new_weibos.append(weibo)
                    whatwehave.add(uid_mid)
            self.write_records(new_weibos, fp_timeline, log=u'微博')
            self.hibernate(period)

    def crawl_timeline(self, fp_timeline, fp_uids):
        targt_uids = self.read_records(fp_uids, col_id=0) if not isinstance(fp_uids, (set, list)) else set(fp_uids)
        saved_uids = self.read_records(fp_timeline, col_id=0)
        for uid in targt_uids - saved_uids:
            print uid,
            page = 1
            wbs = []
            while True:
                has_next, wb_c = self._crawl_timeline(uid, page)
                print page,
                page += 1
                if not has_next:
                    break
                wbs += wb_c
            self.write_records(wbs, fp_timeline)
            print

    def _crawl_timeline_feed(self, uid, page, pagebar, page_property=None):
        params = {
            'is_search': '0',
            'visible': '0',
            'is_all': '1',
            'is_tag': '0',
            'profile_ftype': '1',
            'page': page,
        }

        if pagebar != -1:
            params.update({
                'ajwvr': '6',
                'domain': page_property['pid'],
                'pl_name': 'Pl_Official_MyProfileFeed__23',
                'id': page_property['page_id'],
                'script_uri': '/' + page_property['oid'],
                'feed_type': '0',
                'pagebar': pagebar,
                'pre_page': page,
                'domain_op': page_property['pid'],
                '__rnd': int(self.utc_now() * 1000)
            })
        if pagebar == -1:
            soup = self.get_soup('https://weibo.com/{}'.format(uid), params=params)
            feed = soup.find('script',
                             text=lambda x: self.json_has(self.parse_script(x, within='FM\\.view\((.*)\)'),
                                                          attrs={'ns': 'pl.content.homeFeed.index',
                                                                 'domid': re.compile('MyProfileFeed')}))
            if not feed:
                with open('error.html', 'w') as o:
                    o.write(soup.prettify())
                raise LookupError('cao')
            feed_html = self.parse_script(feed.text, within='FM\\.view\((.*)\)')
            feed_soup = BeautifulSoup(feed_html['html'], 'lxml')

            if page_property is None:
                page_property = self.get_page_property(
                    soup.find('script', type='text/javascript', text=re.compile('\\$CONFIG')).get_text(strip=True),
                    var_name='$CONFIG')
        else:
            feed_html = self.get_json('http://weibo.com/p/aj/v6/mblog/mbloglist', params=params)
            feed_soup = BeautifulSoup(feed_html['data'], 'lxml')
        feed_list = feed_soup.find_all('div', attrs={'class': 'WB_cardwrap', 'action-type': 'feed_list_item'})
        has_next = True if feed_list else False

        weibos = []
        for weibo in feed_list:
            record = parse_weibo(weibo, target_uid=uid)
            if record:
                weibos.append(record)
        return has_next, weibos, page_property

    def _crawl_timeline(self, uid, page=1):
        weibos = []
        page_property = None
        has_next = True
        for pagebar in xrange(-1, 2):
            has_next, feeds, page_property = self._crawl_timeline_feed(uid, page, pagebar, page_property=page_property)
            weibos += feeds
        return has_next, weibos

    def crawl_weibostores(self, fp_userlist, fp_goodlist, fp_emptycache):
        targt_users = self.read_records(fp_userlist, col_id=1)
        saved_users = self.read_records(fp_goodlist)
        empty_users = self.read_list(fp_emptycache)

        print u'开始获取微博橱窗.',
        print u'网址: https://shop.sc.weibo.com/h5/shop/index?weiboUid={}'
        print u'总用户数量: {}, 已获取: {}'.format(len(targt_users), len(saved_users) + len(empty_users))

        for weibo_uid in targt_users - saved_users - empty_users:
            items = self.crawl_weibostore(weibo_uid)
            if items:
                self.write_records(items, fp_goodlist, log=u'商品', log_prefix=u'用户')
            else:
                self.write_line(weibo_uid, fp_emptycache)

    def crawl_weibostore(self, uid):
        page = 0
        store_goods = []
        while True:
            page += 1
            goods = self._crawl_weibostore(uid, page)
            if not goods:
                break
            store_goods += goods
        time.sleep(random.uniform(3, 10))
        return [uid] + store_goods if store_goods else []

    def _crawl_weibostore(self, uid, page=1):
        store_params = {'weiboUid': uid, '__rnd': int(self.utc_now() * 1000)} \
            if page==1 else {'weiboUid': uid, 'page': page, 'shopId': ''}
        store_url = urljoin('https://shop.sc.weibo.com/aj/h5/shop/', 'index' if page==1 else 'recvlist')
        store_html = self.session.get(store_url, params=store_params)
        store_json = json.loads(store_html.content)
        return parse_weibostore(store_json)

    @staticmethod
    def retrieve_script(script):
        return re.compile('FM\\.view\((.*)\)').search(script).group(1)

    @staticmethod
    def is_loggedin(soup):
        return False if 'sina visitor system' in soup.head.get_text(strip=True).lower() else True
