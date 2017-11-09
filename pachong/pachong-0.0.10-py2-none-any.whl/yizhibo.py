#-*-coding:utf-8-*-
__author__ = 'cchen'

import json
import re

from bs4 import BeautifulSoup

from pachong import PaChong
from yizhibo_parsers import parse_liveroom, retrieve_live_id


class Yizhibo(PaChong):

    def crawl_userlist(self, fp_userlist, fp_id_cache, period=30):
        self._saved_users = self.read_records(fp_userlist)
        self._saved_lives = self.read_list(fp_id_cache)

        while True:
            unsvd_lives = self._crawl_livelist_from_main()
            self.write_list(unsvd_lives, fp_id_cache)
            users_info = self.crawl_userlist_from_liveroom(unsvd_lives)
            self.write_records(users_info, fp_userlist, log=u'用户')
            self.hibernate(period)

    def _crawl_livelist_from_main(self):
        print u'加载一直播主页...',
        html = self.session.get('https://www.yizhobo.com/')
        soup = BeautifulSoup(html.content, 'lxml')
        lives = soup.find_all('li', class_=re.compile('list|fl'))
        live_ids = [retrieve_live_id(live.find('a', target='_live')) for live in lives if live]

        html_more = self.session.get('https://www.yizhobo.com/www/web/get_pc_hot_list_more')
        more = json.loads(html_more.content)
        live_ids += [live['scid'] for live in more['data']]
        print u'成功加载{}个直播间!'.format(len(live_ids)),

        unsvd_lives = set(live_ids) - self._saved_lives
        self._saved_lives |= unsvd_lives
        return unsvd_lives

    def crawl_userlist_from_liveroom(self, live_ids, recommend=True):
        for live_id in live_ids:
            live_html = self.session.get('https://www.yizhobo.com/l/' + live_id + '.html')
            live_soup = BeautifulSoup(live_html.content, 'lxml')
            user_info = parse_liveroom(live_soup)
            if user_info[0] in self._saved_users:
                continue
            self._saved_users.add(user_info[0])
            yield user_info
            if recommend:
                for info in self.crawl_userlist_from_liveroom(
                        self._crawl_userlist_from_recommendation(),
                        recommend=False):
                    if info[0] in self._saved_users:
                        continue
                    self._saved_users.add(info[0])
                    yield info

    def _crawl_userlist_from_recommendation(self):
        html = self.session.get('https://www.yizhobo.com/live/h5api/get_live_over_recom')
        rcmd = json.loads(html.content)
        return {live['scid'] for live in rcmd['data'] if live['memberid'] not in self._saved_users}

    def crawl_userprofile(self, fp_userlist, fp_huifang, is_updating=False):
        self._saved_cache = self.read_records(fp_huifang, 1) if is_updating else self.read_records(fp_huifang, 0)
        userlist = self.read_records(fp_userlist, 0)
        if not is_updating:
            userlist -= self._saved_cache

        for uid in userlist:
            html = self.session.get('https://www.yizhobo.com/member/personel/user_info',
                                    params={'memberid': uid, 'jumpbrowser': '1'})
            soup = BeautifulSoup(html.content, 'lxml')
            desc = soup.find('div', class_='person_intro').get_text(strip=True, separator=u' ').encode('utf-8')
            hfid = self.crawl_livelist(uid)
            records = ([uid, desc, scid, views] for scid, views in hfid if scid not in self._saved_cache)
            self.write_records(records, fp_huifang, log=u'回放', log_prefix=u'用户{}: '.format(uid))

    def crawl_livelist(self, uid):
        html = self.session.get('https://www.yizhobo.com/member/personel/user_works', params={'memberid': uid})
        soup = BeautifulSoup(html.content, 'lxml')
        return ((retrieve_live_id(live.find('a', target='_blank')),
                 live.find('div', class_='index_num').text.encode('utf-8'))
                for live in soup.find_all('li', class_='index_hf'))
