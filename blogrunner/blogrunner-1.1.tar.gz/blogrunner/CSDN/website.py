#!/usr/bin/python3

import sys
from bs4 import BeautifulSoup
import requests
import urllib.request as ur
import re
import time
import hashlib
import analyse

def save_page(domain , href):
    # 本业博客提取
    information = []
    url = []
    for i in href:
        url.append((ur.urljoin(domain , i.a['href']) , i.a['href'][-8:]))
    # begin to save all the page in the url list
    for i in url:
        print('Downloading ' + i[0] + ' ...')
        try:
            # ur.urlretrieve(i[0] , filename = '/home/lantian/fortest/test/' + i[1])
            md5 = hashlib.md5()
            md5.update(i[0].encode('utf8'))
            con = md5.hexdigest()
            ans = requests.get(i[0])
            ans.encoding = 'utf8'
            information.append(analyse.crawl_sample(con , ans.text , 1))
        except:
            print('服务器正在检测爬虫，异常躲避 10s ...')
            time.sleep(10)    # 延时爬虫
    return information

# domain = sys.argv[1]

# url_page = 'http://blog.csdn.net/ltyqljhwcm'
# url_page = sys.argv[1]
# domain = url_page

def crawl(url_page , domain , limit):
    '''
    该函数是站点爬取函数，url_page是种子url，domain是域名，在之后用于给我们进行url拼接做准备，limit是我们的爬取页数限制
    '''
    information = [] 
    while limit :
        print('url_page :' , url_page)
        page = requests.get(url_page , headers = {'User-Agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})    # get the front for the page
        print('获取页面完毕')
        soup = BeautifulSoup(page.text , 'lxml')
        main = soup.find_all(id = 'article_list')[0]
        href = main.find_all(class_ = 'link_title')
        link = soup.find_all(id = 'papelist')[0]
        information.extend(save_page(url_page , href))
        link_next = [i for i in link.find_all(name = 'a') if list(i.strings)[0] == '下一页'][:limit]
        if len(link_next) == 0 : 
            print('End')
            break
        else : 
            url_page = ur.urljoin(domain , link_next[0]['href'])
        print('Used :' , url_page)
        limit -= 1
    return information

if __name__ == '__main__':
    save = crawl('http://blog.csdn.net/ltyqljhwcm' , 'http://blog.csdn.net/ltyqljhwcm' , 1)
    print(save)
