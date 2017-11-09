#!/usr/bin/python3

'''利用BeautifulSoup进行富文本过滤'''

import sys
from bs4 import BeautifulSoup
sys.path.append('../')
from MYSQL import sql

def crawl_sample(filename , ans , flag):
    soup = BeautifulSoup(ans , 'lxml')
    # 提取正文，富文本化
    main = soup.article
    feature = {}
    if main == None:
        main = soup.find(id = 'article_content')
        if main == None:
            print('目标URL不是博文页面')
            return 
        else:
            # 此时进入csdn的另外的主题里面
            feature['md5url'] = filename
            feature['size'] = len(main.get_text())
            feature['number_like'] = int(soup.find(id = 'btnDigg').dd.string)
            feature['number_reader'] = int(''.join(filter(str.isdigit , soup.find(class_ = 'link_view').string)))
            feature['number_code'] = len(main.find_all(name = 'pre'))
            feature['number_photo'] = len(main.find_all(name = 'img'))
            feature['number_link'] = len(main.find_all(name = 'a'))
    else:
        feature['md5url'] = filename
        feature['size'] = len(main.get_text())
        feature['number_like'] = int(soup.find(class_ = 'left_fixed').find(class_ = 'txt').string)
        feature['number_reader'] = int(soup.find(class_ = 'btn-noborder').find(class_ = 'txt').string)
        # feature['number_comment'] = int(soup.find(class_ = 'load_comment').span.string)
        # 之后的 grade and analyse_grade 都是用户的添加和我们的自然语言文本分析的结果
        feature['number_code'] = len(main.find_all(name = 'pre'))
        feature['number_photo'] = len(main.find_all(name = 'img'))
        # feaure 存储进入数据库
        print('样本入数据库结束')
        noise = main.find_all(class_ = 'article_bar clearfix')[0]
        noise.decompose()    # 删除标签
        feature['number_link'] = len(main.find_all(name = 'a'))

    if flag != 0 : sql.main(6 , **feature)    # 只有不是测试网而言的网页才一会进入aifeature表中存储对应的网页样本信息
    else : return feature    # 信息返还给我们的后端的对应路由
    k = main.prettify().replace('"' , '\'')
    # 为了高亮代码块，我们需要将csdn的css样式表插入进来，head头需要包含
    ans = "<html><head><meta charset='utf8'></head><body>" + k + '</body></html>'
    pages = {'md5url' : filename , 'content' : ans}
    sql.main(4 , **pages)
    print('文本入数据库结束')
    feature['blog_name'] = soup.title.string
    return feature

if __name__ == "__main__":
    import requests
    f = requests.get('http://blog.csdn.net/jason_cuijiahui/article/details/74276698?locationNum=3&fps=1')
    crawl_sample('lantian' , f.text , 1)
