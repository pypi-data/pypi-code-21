#!/usr/bin/python3

from bs4 import BeautifulSoup
import requests
import sys
import urllib.request as ur
import hashlib
import time
sys.path.append('../')
import analyse

# 将一页的所有的连接加入列表并返回
def add_url(soup):
    url = []
    block = soup.find_all(class_ = 'search-list J_search')
    for i in block:
        url.append(i.find(name = 'a')['href'])
    return url

# 获取下一页
def get_next_page(next_page):
    page = requests.get(next_page)
    page.encoding = 'utf8'
    return page

# 获取关键字 
# keyword = sys.argv[1]
# keyword = 'python'

# 构建种子url
# url = 'http://so.csdn.net/so/search/s.do?q=%s&q=%s' % (keyword , keyword)
# print('URL :' , url)

def crawl(url , page_number):
    '''
    该函数抓取我们的页面并抽取数据
    '''
    page = requests.get(url , headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    page.encoding = 'utf8'
    now_url = url
    page_sum_number = page_number
    # 总的url链接
    urls = []
    while page_number:
        page_number -= 1
        soup = BeautifulSoup(page.text , 'lxml')
        urls.extend(add_url(soup))    # 扩展urls列表
        # 获取下一页链接，准备跳转,更新page
        # print('Href :' , soup.find_all(class_ = 'n')[0]['href'])
        next_page = ur.urljoin(url , soup.find_all(class_ = 'btn btn-xs btn-default')[0]['href'])
        page = get_next_page(next_page)    # 获取下一个页面,返回requests对象
        # print(urls , len(urls))
        print("page scanning ... %d / %d" % (page_number , page_sum_number))

    # save the page to the folder at /home/lantian/fortest/baidu/raw
    print('总计爬取网页 %d' % len(urls))
    information = []    # 总的消息，JSON化后传送给前端
    for j , i in enumerate(urls):
        md5 = hashlib.md5()
        md5.update(i.encode('utf8'))    # md5加密对url压缩存储
        try:
            content = md5.hexdigest()
            print('Downloading ' + i + ' ...' , j + 1)
            con = requests.get(i)
            con.encoding = 'utf8'
            filename = md5.hexdigest()
            t = analyse.crawl_sample(filename , con.text , 1)
            if t:
                information.append(t)
        except Exception as e:
            print(e)
            print('CSDN服务器正在扫描爬虫，延时 10s 躲避')
            time.sleep(10)
    print('End')
    return information

if __name__ == "__main__":
    save = crawl('http://so.csdn.net/so/search/s.do?q=python&q=python' , 1)
    print(save)
