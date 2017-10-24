# -*-coding:utf-8-*-
#Author: UlionTse

import time
import random
import math
import requests
from bs4 import BeautifulSoup


class Gen_proxy:
    def __init__(self):
        self.ss = requests.Session()
        self.ss.trust_env = False
        self.host = 'http://www.xicidaili.com'
        self.category = ['nt', 'nn', 'wn', 'wt']  # 'qq'
        self.headers = {
            'Host': 'www.xicidaili.com',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
            'Referer': 'http://www.xicidaili.com/nt/2',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Cookie': (
            '_free_proxy_session=BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJTRiZTUyMzBmNTg5OTM2YmJkMjUwNzI0YzA3MmZmYzhhBjsAVEkiEF9jc3JmX3Rva2VuBjs'
            'ARkkiMW41d1hVT2lRbmx6SG05QWZzTGhsQnJMKzY0S0swNE5zcURzWERORi9QSG89BjsARg%3D%3D--75202b4ab0931f7023c611e51d6b3726333b1c83; '
            'Hm_lvt_0cf76c77469e965d2957f0553e6ecf59={0}; Hm_lpvt_0cf76c77469e965d2957f0553e6ecf59={1}'.format(
                int(time.time()), int(time.time()))),
            'If-None-Match': 'W/"6d13de41dfc71909f4b7f53fb9ad09ea"'
        }
    
    
    def get_soup(self, url):
        try:
            res = self.ss.get(url, headers=self.headers)
        except:
            res = self.ss.get(url, headers=self.headers, proxies={'http': '58.217.255.184:1080'})
        soup = BeautifulSoup(res.text, 'lxml')
        return soup
    
    
    def get_data(self, soup):
        items = soup.find_all('tr', {'class': ['odd', '']})
        for item in items:
            it = item.find_all('td')
            try:
                country = it[0].img.attrs['alt']
                source_url = self.host + it[3].a.attrs['href']
            except AttributeError:
                country = ''
                source_url = ''
            
            if '天' in it[8].get_text():
                survived_days = int((it[8].get_text())[:-1])
                speed_seconds = float((it[6].div.attrs['title'])[:-1])
                conn_seconds = float((it[7].div.attrs['title'])[:-1])
                
                if (speed_seconds < 1.0 and conn_seconds < 1.0):
                    data = {
                        'complete_ip': it[1].get_text() + ':' + it[2].get_text(),
                        'ip_address': it[1].get_text(),
                        'port': it[2].get_text(),
                        'country': country,
                        'server_area': it[3].get_text().strip('\n').replace(' ', ''),
                        'category': it[4].get_text(),
                        'http_type': it[5].get_text(),
                        'speed_seconds': speed_seconds,
                        'conn_seconds': conn_seconds,
                        'network_operator': '',
                        'survived_days': survived_days,
                        'verify_datetime': it[9].get_text(),
                        'source_url': source_url,
                        'source_host': self.host
                    }
                    yield {data['http_type'].lower(): data['complete_ip']}
                    
    
    def save_pool(self, dt):
        pool = []
        pool.append(dt)
        return pool
    
    
    def gen_pool(self, number):
        print('\n--------------------- PLEASE WAIT ---------------------\n')
        proxy_pool = []
        for cat in self.category:
            for num in range(1, number):
                url = self.host + '/{0}/{1}'.format(cat, num)
                time.sleep(9)
                soup = self.get_soup(url)
                data = self.get_data(soup)
                
                for dt in data:
                    #print(dt)
                    proxy_pool += self.save_pool(dt)
            #print(cat, '----', len(proxy_pool))
            print('Downloading proxies [{0}/4]'.format(1+self.category.index(cat)))
        print('Prepare [{}] proxies.'.format(len(proxy_pool)))
        self.ss.close()
        return proxy_pool


    def test_pool(self,pool):
        print('\nBegin to test whether `proxy_pool` can be used, you will wait about [{} minutes].\n'.format(
            math.trunc((len(pool)*5)/60)))
        url_pool = ['https://hao.360.cn/',
                    'https://www.baidu.com/',
                    'https://www.taobao.com/',
                    'https://www.jd.com/',
                    'http://www.weibo.com/',
                    'http://www.toutiao.com/']
        
        UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6'}
        sss = requests.Session()
        final_proxy_pool = []
        start = time.time()
        N = 0
        for pxy in pool:
            sss.headers.update(UA)
            sss.proxies.update(pxy)
            url = random.choice(url_pool)
            try:
                r = sss.get(url, timeout=5)
                if r.status_code == requests.codes.ok:
                    final_proxy_pool.append(pxy)
                    #print('Success num[{0}], [{1}].'.format(len(final_proxy_pool),pxy))
            except:
                pass
            finally:
                sss.close()
            N += 1
            print('Tested [{0}%] -------- Wait [{1} minutes]'.format(math.trunc((N/len(pool))*100),
                  math.trunc(-1+(len(pool)*5-(time.time()-start))/60)))
        print('\n[{0}] proxies will be loaded.'.format(len(final_proxy_pool)))
        #print('\nFinal_proxy_pool: {}'.format(final_proxy_pool))
        #print('--------------------test_time:{} seconds. Instantiation end.---------------------'.format(math.trunc(time.time()-start)))
        print('\n-------------------------------- YOU CAN BEGIN TO USE PROXY --------------------------------\n')
        return final_proxy_pool


gen = Gen_proxy()
#END