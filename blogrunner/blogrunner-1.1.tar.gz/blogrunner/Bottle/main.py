#/usr/bin/python3

'''
该模块执行对应的请求
前端发送的求情，在后端执行对应的语句或者返回对应的JSON格式数据
'''

# 库导入
from bottle import template , route , run , static_file
from bottle import request , response
import sys
sys.path.append('..')
sys.path.append('../CSDN')
import hashlib
import MYSQL.sql as sql
from CSDN import analyse
from CSDN import website
from CSDN import keyword
from AI import get_grade    # ID3 - 决策树
from AI import KNN    # K-临近算法求解最佳适应

def get_result(ans):
    return KNN.main(ans)    # 获取训练样本和测试样本,返回对应的k的number_reader的均值

@route('/' , method = 'GET')
def get_main():
    return static_file('index.html' , '../dist/')

@route('/static/css/<filename>' , method = 'GET')
def get_css(filename):
    return static_file(filename , '../dist/static/css/')

@route('/static/js/<filename>' , method = 'GET')
def get_js(filename):
    return static_file(filename , '../dist/static/js/')
    
@route('/static/img/<filename>' , method = 'GET')
def get_img(filename):
    return static_file(filename , '../dist/static/img')

@route('/static/fonts/<filename>' , method = 'GET')
def get_fonts(filename):
    return static_file(filename , '../dist/static/fonts')

@route('/urlupload' , method = 'POST')
def get_url_upload():
    import json
    # url = request.forms.get('url')    获取用户为文件定义的名字,一定要发布出去才可以使用
    response.set_header('Access-Control-Allow-Origin','*')
    data = eval((request.body.readlines()[0]).decode('utf8'))
    import requests
    page = requests.get(data['url'] , headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    page.encoding = 'utf8'
    f = page.text
    md5 = hashlib.md5()
    md5.update(data['url'].encode('utf'))
    filename = md5.hexdigest()
    ans = analyse.crawl_sample(filename , f , 1)
    ans['grade'] = data['grade']
    print(ans['grade'])
    number_reader = -1
    if ans != None :
        # 获得了对应文章的标签属性 , ans是一个含有grade但是没有number_reader的字典
        number_reader = get_result(ans)
    # 发送信号单元
    return json.dumps({'result': int(number_reader)} , ensure_ascii = False , skipkeys = True)

@route('/htmlupload' , method = 'POST')
def get_html_upload():
    response.set_header('Access-Control-Allow-Origin','*')
    data = (request.body.readlines()[0]).decode('utf8')
    import pprint
    pprint.pprint(data)

# 用户信息数据获取响应

# 用户登录路由
def check_login(username , passwd):
    print(username , passwd)
    save = sql.main(1 , **{'name' : username})
    if save[1] == passwd : return True
    else : return False

@route('/user/login' , method = 'POST')
def get_signup():
    username = request.forms.get('username')
    passwd = request.forms.get('passwd')
    if check_login(username , passwd):
        # This is the what we want to do
        # 用户的登录账号，在这里可以获取用户的model以进一步操作等等
        return '<p><b>Login successfullly!</b></p>'
    else:
        return '<p><b>Login Failed!</b></p>'

# 用户注销路由
@route('/user/delete' , method = 'POST')
def get_delete():
    username = request.forms.get('username')
    passwd = request.forms.get('passwd')
    if check_login(username , passwd):
        sql.main(9 , **{'name':username})
        return '<p><b>User has been deleted from database!</b></p>'
    else:
        return '<p><b>Password wrong or User wrong , delete user Failed!</p>'

# 用户注册
@route('/user/signup' , method = 'POST')
def get_signup():
    username = request.forms.get('username')
    passwd = request.forms.get('passwd')
    sql.main(2 , **{'name' : username , 'passwd' : passwd})
    return '<p><b>Create login successfully!</b></p>'

'''
爬虫定义数据接收路由
'''
# TODO:这里的记得要加入一个排序处理，排序处理的模块组件写在AI中，这里只是一个中间的处理过程
@route('/spider/website' , method = 'POST')
def get_website_spider():
    import json
    import operator
    response.set_header('Access-Control-Allow-Origin','*')
    data = eval(request.body.readlines()[0].decode('utf8'))
    name = data['username']
    limit = int(data['limit'])
    # root_url , limit是传递给其他组件模块的参数
    domain = 'http://blog.csdn.net/'
    root_url = domain + name
    # 处理,信息返回
    res = website.crawl(root_url , domain , limit)
    res = get_grade.analyse(res)
    res.sort(key = operator.itemgetter('grade') , reverse = True)
    return json.dumps(res , indent = 4 , ensure_ascii=False , skipkeys = True)

@route('/spider/keyword' , method = 'POST')
def get_keyword_spider():
    import json
    import operator
    # 这里因为跨域请求的问题，必须要加入该头信息
    response.set_header('Access-Control-Allow-Origin','*')
    data = eval(request.body.readlines()[0].decode('utf8'))
    limit = int(data['limit'])
    # print(data , type(data))
    root_url = 'http://so.csdn.net/so/search/s.do?q=%s&q=%s' % (data['keyword'] , data['keyword'])
    res = keyword.crawl(root_url , limit)
    res = get_grade.analyse(res)
    res.sort(key = operator.itemgetter('grade') , reverse = True)
    return json.dumps(res , indent = 4 , ensure_ascii = False , skipkeys = True)

'''
博文信息管理，删除，评价，博文打开
'''
@route('/blog/delete/<md5url>' , method = 'POST')
def blog_delete(md5url):
    '''
    删除博文，但是不删除对于博文的评价，评价是很重要的信息数据，不能随便的删除
    '''
    import json
    response.set_header('Access-Control-Allow-Origin','*')
    sql.main(10 , **{'md5url' : md5url})
    return json.dumps({'delete': True} , ensure_ascii = False , skipkeys = True)

''''
@route('/blog/batch_delete/<grade:int>')
def blog_batch_delete(grade):
    # 批量删除博文接口
    sql.main(11 , **{'grade' : grade})
    return '<p><b>Batch delete successfully!</b></p>'
'''

@route('/blog/comment' , method = 'POST')
def blog_comment():
    '''
    这里的comment的数据制定了我们对博文的评价成程度
    1,2,3,4,5几个等级
    '''
    import json
    response.set_header('Access-Control-Allow-Origin','*')
    data = eval(request.body.readlines()[0].decode('utf8'))
    sql.main(7 , **{'md5url' : data['md5url'] , 'grade' : data['grade']})
    return json.dumps({'done': True} , ensure_ascii = False , skipkeys = True)

@route('/blog/open/<md5url>')
def blog_open(md5url):
    '''
    该模块返回一个新的富文本博文给用户
    '''
    response.set_header('Access-Control-Allow-Origin','*')
    return sql.main(3 , **{'md5url' :md5url})[0][1].decode('utf8')

@route('/history' , method = 'POST')
def history():
    import json
    response.set_header('Access-Control-Allow-Origin','*')
    res = sql.main(5)
    new = []
    for i in res:
        p = {}
        p['md5url'] = i[0]
        p['size'] = i[1]
        p['number_reader'] = i[2]
        p['number_like'] = i[3]
        p['grade'] = i[4]
        p['number_code'] = i[5]
        p['number_photo'] = i[6]
        p['number_link'] = i[7]
        new.append(p)
    return json.dumps(new , ensure_ascii = False , skipkeys = True)

@route('/train' , method = "POST")
def train():
    # 该函数启动训练
    dataset , label = get_grade.load_data_for_grade(None)
    plabel = label.copy()
    model = get_grade.createtree(dataset , plabel)
    get_grade.save_model_to_sql(model)
    print(model)

# 启动服务器
if __name__ == "__main__":
    # 搭建数据库环境
    run(host = '0.0.0.0' , port = 8888)
