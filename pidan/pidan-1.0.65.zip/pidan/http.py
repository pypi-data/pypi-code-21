# -*- coding: utf-8 -*-
#http相关的函数
from urlparse import urlparse
import random
from bson.objectid import ObjectId
from django.utils.http import urlquote
import validator,date
import urllib2,urllib
import cStringIO
from PIL import Image
import html,converter,filelib
import traceback
import image as imagelib

def get_list_param_from_post(request,param_name):
    result = request.POST.getlist(param_name,[])
    return result

def get_int_param_from_post(request,param_name,default=0):
    '从request.GET获取整型参数'
    result = default
    if param_name in request.POST:
        value = request.POST.get(param_name)
        if validator.is_int(value):
            result = int(value)
    return result

def get_int_param_from_get(request,param_name,default=0):
    """从request.GET获取整型参数"""
    result = default
    if param_name in request.GET:
        value = request.GET.get(param_name)
        if validator.is_int(value):
            result = int(value)
    return result

def get_str_param_from_post(request,param_name,full_match=True,default=''):
    '从request.POST获得字符串参数'
    result = ''
    if full_match:
        result = request.POST.get(param_name,default).strip()
    else:
        if request.POST.has_key(param_name):
            result = request.POST.get(param_name,default).strip()
        else:
            for k,v in request.POST.items():
                if k.startswith(param_name):
                    result = request.POST.get(k,default).strip()
    return result

def get_str_param_from_get(request,param_name,full_match=True,default=''):
    '从request.GET获得字符串参数'
    result = ''
    if full_match:
        result = request.GET.get(param_name,default).strip()
    else:
        if request.GET.has_key(param_name):
            result = request.GET.get(param_name,default).strip()
        else:
            for k,v in request.GET.items():
                if k.startswith(param_name):
                    result = request.GET.get(k,default).strip()
    return result

def get_mongo_id_from_get(request,param_name):
    id = get_str_param_from_get(request,param_name)
    try:

        id = ObjectId(id)
    except:
        id = ''
    return id

def get_mongo_id_from_post(request,param_name):
    id = get_str_param_from_post(request,param_name)
    try:
        id = ObjectId(id)
    except:
        id = ''
    return id

def get_str_array_from_post(request,param_name):
    '''从request.POST获得字符串数组信息'''
    return request.POST.getlist(param_name,[])

def get_id_array_from_post(request,param_name):
    lst = request.POST.getlist(param_name,[])
    result = [ObjectId(item) for item in lst if item]
    return result


def get_id_array_from_get(request,param_name):
    lst = request.GET.getlist(param_name,[])
    result = [ObjectId(item) for item in lst if item]
    return result

def get_int_array_from_post(request,param_name):
    '''将post上来的同一参数有多个值的情况处理成数组'''
    lst = request.POST.getlist(param_name,[])
    result = [int(item) for item in lst if item]
    return result

def get_size_param_from_post(request,param_name):
    '''获得(123,128)格式的图片尺寸参数'''
    size = get_str_param_from_post(request,param_name)
    try:
        size = eval(size)
    except:
        size = (0,0)
    return size

def get_size_param_from_get(request,param_name):
    size = get_str_param_from_get(request,param_name)
    try:
        size = eval(size)
    except:
        size = (0,0)
    return size

def get_split_str_array_from_post(request,param_name,split=None):
    '''将用户提交的信息按照指定的分隔符分割成数组，如果不提供分隔符则使用默认规则分割'''
    value = get_str_param_from_post(request,param_name)
    result = []
    if value:
        if split:
            result = value.split(split)
        else:
            result = value.split()
    return result

def get_param_from_post(request,type,param_name):
    '''根据request和类型获得参数的值'''
    result = ''
    def get_str():
        return get_str_param_from_post(request,param_name)
    def get_date():
        return date.str_to_date(get_str_param_from_post(request,param_name))
    def get_datetime():
        return date.str_to_datetime(get_str_param_from_post(request,param_name))
    def get_number():
        result=0.0
        try:
            result = float(get_str_param_from_post(request,param_name))
        except:
            pass
        return result
    def get_int():
        return get_int_param_from_post(request,param_name)
    def get_int_array():
        result = get_str_param_from_post(request,param_name)
        result = converter.str_to_int_arry(result,',')
        return result
    def get_str_array():
        result = get_str_param_from_post(request,param_name)
        result = converter.str_to_arry(result,',')
        return result
    def get_other():
        result = get_str_param_from_post(request,param_name)
        try:
            result = eval(result)
        except:
            pass
        return result
    def get_image():
        data = upload_pic_return_dict(request,name=param_name)
        result = data.get('pic','')
        return result
    def get_file():
        data = upload_return_dict(request,name=param_name)
        result = data.get('url','')
        return result
    def get_list():
        result = request.POST.getlist(param_name)
        return result

    process_dict = {
                    'default':get_list,
                    'text':get_str,
                     'long_text':get_str,
                    'single_select':get_str,
                    'multi_select':get_list,
                    'select':get_str,
                     'rich_text':get_str,
                     'url':get_str,
                     'date':get_date,
                     'datetime':get_datetime,
                     'number':get_number,
                     'int':get_int,
                     'int_array':get_int_array,
                     'str_array':get_str_array,
                     'image':get_image,
                     'audio':get_file,
                      'video':get_file,
                     'upload_image':get_str,
                     'other':get_other,
                     }
    if not type in process_dict.keys():
        type='default'
    result = process_dict[type]()
    return result

def get_query_params(request,exclude=()):
    '''从query返回完整的查询字符串'''
    queryStr = ''
    for k,v in request.GET.items():
        if not k in exclude:
            queryStr = ''.join((queryStr,'&',k,'=',v))
    if queryStr:
        queryStr = queryStr[1:]
    return queryStr


def get_post_params(request,exclude=()):
    '''从post返回完整的提交字符串'''
    queryStr = ''
    for k,v in request.POST.items():
        if not k in exclude:
            queryStr = ''.join((queryStr,'&',k,'=',v))
    if queryStr:
        queryStr = queryStr[1:]
    return queryStr


def get_referrer(request,default_url=''):
    '返回引用页'
    f = request.META.get('HTTP_REFERER','')
    if not f:
        f=default_url
    return  f

def get_url_from(request,from_param='f',default_url=''):
    f= get_str_param_from_get(request,from_param)
    if f:
        return f
    return  default_url

def get_url_path(url):
    '''返回url的路径部分'''
    url = urlparse(url)
    return url.path

def get_client_ip(request):
    '''得到客户端的ip地址'''
    try:
        real_ip = request.META.get('HTTP_X_REAL_IP','')
        if not real_ip:
            real_ip = request.META.get('HTTP_X_FORWARDED_FOR','')
        regip = real_ip.split(",")[0]
        if not regip:
            regip = request.META.get('REMOTE_ADDR','')
    except:
        regip = ""
    return regip

def get_domain_from_url(url):
    '''从url中获取域名'''
    import urlparse
    domain = url
    try:
        domain = urlparse.urlsplit(url)[1].split(':')[0]
    except:
        pass
    return domain

def is_search_engine(request):
    '''根据user-agent判断是否为搜索引擎'''
    result = False
    user_agent = request.META.get('HTTP_USER_AGENT',None).lower()
    spider_list = ['Baiduspider','Googlebot','MSNBot','YoudaoBot','Sogou','JikeSpider','Sosospider','360Spider','iaskspider']
    for spider in spider_list:
        if spider.lower() in user_agent:
            result = True
            break
    return result

def is_mobile(request):
    '''根据user-agent判断是否为移动设备'''
    result = False
    user_agent = request.META.get('HTTP_USER_AGENT',None)
    user_agent = user_agent.lower() if user_agent else ''
    mobile_list = ["Android", "iPhone", "SymbianOS", "Windows Phone", "iPad", "iPod","wechat","micromessenger"]
    for spider in mobile_list:
        if spider.lower() in user_agent:
            result = True
            break
    return result

def is_wechat(request):
    '''根据user-agent判断是否为微信客户端'''
    result = False
    user_agent = request.META.get('HTTP_USER_AGENT',None).lower()
    mobile_list = ["micromessenger"]
    for spider in mobile_list:
        if spider.lower() in user_agent:
            result = True
            break
    return result

def strip_params_from_url(url):
    '''去除url的参数部分'''
    result=''
    lst= url.split('?')
    if lst:
        result = lst[0]
    return result

def get_params_from_url(url):
    '''从url中获取参数字典'''
    params_dict = {}
    try:
        result = urlparse(url)
        params_str = result.query

        for item in params_str.split('&'):
            k,v = item.split('=')
            params_dict[k]=v
    except:
        pass
    return params_dict

def create_url(url,new_params=None):
    '''根据url和指定的参数生成新的url'''
    #获得当前URL的参数字典
    params_dict = get_params_from_url(url)

    if new_params:
        # 删除重复的参数，以新提供的参数为主
        for k,v in new_params.items():
            if params_dict.has_key(k):
                del params_dict[k]
        params_dict.update(new_params)

    for k,v in params_dict.items():
        if isinstance(v,unicode):
            params_dict[k] = v.encode('utf-8')
    params = urllib.urlencode(params_dict)
    if params:
        params = '?' + params
    url = strip_params_from_url(url)
    result = url + params
    return result


def create_new_url(request,url,new_params=None,remove_params=None):
    '''结合request的get参数，url地址和要绑定的参数组成新的网址，new_params为要添加的新参数，remove_params为要移除的旧参数'''
    params_dict = request.GET.copy()
    params = ''
    if not params_dict:
        params_dict = {}
    if new_params:
        params_dict.update(new_params)
    #要移除的参数
    if remove_params:
        for param in remove_params:
            if params_dict.has_key(param):
                del params_dict[param]

    for k,v in params_dict.items():
        params += '%s=%s&'%(k,urlquote(v))
    if params:
        params = '?' + params[:-1]
    result = url + params
    return result

def get_current_url(request):
    '''得到当前url地址'''
    return 'http://%s%s'%(request.get_host(),request.get_full_path())

def get_url_content(url,action='',headers=None):
    '''根据url读取url的内容'''
    try:
        import cookielib
        cookie=cookielib.CookieJar()
        opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
        agents = [
            "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0)","Internet Explorer 11 (Windows Vista); Mozilla/4.0 ","Google Chrome 0.2.149.29 (Windows XP)","Opera 9.25 (Windows Vista)","Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.1)","Opera/8.00 (Windows NT 5.1; U; en)"
        ]
        agent = random.choice(agents)
        opener.addheaders=[('User-agent',agent)]
        urllib2.install_opener(opener)
        req=urllib2.Request(url+action)
        if headers:
            req.headers.update(headers)
        u=urllib2.urlopen(req)
        content=u.read()
        return content
    except Exception,e:
        return ''

def get_remote_image_info(image_url,default_title=''):
    '''获得远程图片的信息，包括尺寸，图片格式，图片地址，图片说明'''
    result={}
    try:
        file = urllib2.urlopen(image_url)
        temp_image = cStringIO.StringIO(file.read())
        im = Image.open(temp_image)
        result['media'] = image_url
        result['format'] = im.format
        result['size'] = im.size
        result['title'] = default_title
    except:
        pass
    return result

def get_images_from_url_content(url,image_count=5,min_width=100,min_height=100):
    '''根据网页地址获取网页里面的图片信息
        image_count 最多要获取的图片数量
        min_width 图片的最小宽度
        min_height 图片的最小高度
    '''
    content = get_url_content(url=url)
    image_urls = html.get_image_urls(content)[:image_count]
    images = list()
    for image_url in image_urls:
        im = get_remote_image_info(image_url=image_url,default_title='')
        if im and im['size'] and im['size'][0]>=min_width and im['size'][1]>=min_height:
            images.append(im)
    return images

def __send__(url,action='get',params=None,headers=None,proxy=None,timeout=30):
    '''
        action 支持 get 和 post
        url 要提交的网址
        params 参数，格式为字典
        headers 头信息，格式为字典
        proxy 格式:('119.168.37.22:8000','http')
        返回状态编码和内容，如：200,hello world
    '''

    def encoded_dict(in_dict):
        out_dict = {}
        for k, v in in_dict.iteritems():
            if isinstance(v, unicode):
                v = v.encode('utf8')
            elif isinstance(v, str):
                # Must be encoded in UTF-8
                v.decode('utf8')
            out_dict[k] = v
        return out_dict


    if not headers:
        headers = {}
    if not params:
        params={}
    if action.lower() == 'post':
        params = encoded_dict(params)
        data = urllib.urlencode(params)    # Use urllib to encode the parameters
        request = urllib2.Request(url, data,headers=headers)
    else:
        url = create_url(url,params)
        request = urllib2.Request(url,headers=headers)
    if proxy:
        request.set_proxy(proxy[0],proxy[1])
    response = urllib2.urlopen(request)
    return response

def get(url,params=None,headers=None,proxy=None,timeout=30):
    response = __send__(url,action='get',params=params,headers=headers,proxy=proxy,timeout=timeout)
    return response

def post(url,params=None,headers=None,proxy=None,timeout=30):
    response = __send__(url,action='post',params=params,headers=headers,proxy=proxy,timeout=timeout)
    return response

def read_binary_from_url(url):
    '''从url读取url的二进制'''
    try:
        file = cStringIO.StringIO(urllib2.urlopen(url).read())
        return file
    except:
        return None


#----------------处理文件上传-------------------
def handle_uploaded_file(request,f):
    '''
    上传文件，并返回上传文件信息
    返回结果为字典，格式如下：
    {
        'new_file' : new_file,  # 文件url地址
        'real_file' : real_file, #文件真实路径
        'small_new_file':small_new_file,  #小文件url地址（针对图片）
        'small_real_file':small_real_file,#小文件真实路径（针对图片）
        'middle_new_file':middle_new_file, #中等文件url地址（针对图片）
        'middle_real_file':middle_real_file #中等文件url地址（针对图片）
    }
    '''
    new_file_info = filelib.get_new_upload_file_info(f.name)
    destination = open(new_file_info['real_file'], 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return new_file_info


def upload_return_dict(request,name=None):
    '''上传文件，并返回一个字典格式的结果
        格式如下：
        {
        'url':new_file, #url地址
        'real_file':real_file,#真实文件地址
        'title':title,#标题，一般是获取文件名
        'state':state #状态，成功为'SUCCESS'
        }
    '''
    state = 'success'
    new_file = ''
    real_file = ''
    title = ''
    try:
        if request.FILES:
            if name:
                f=request.FILES.get(name,None)
            else:
                f = request.FILES.values()[0]
            new_file_info = handle_uploaded_file(request,f)
            new_file = new_file_info.get('new_file','')
            real_file = new_file_info.get('real_file','')
            title = f.name
        else:
            state=u'请选择文件'
    except:
        state=u'上传文件失败'
    return {'url':new_file,'real_file':real_file,'title':title,'state':state}



def upload_pic_return_dict(request,f=None,name=None,resize=(),image_quality=100,limit_size=20,limit_file_type=('jpg','jpeg','bmp','png','gif','tif'),resize_gif=False):
    '''上传图片并返回一个字典格式的结果，格式如下：
            返回格式：
            {
            'pic':pic,
            'state':state
            }
    '''
    state = 'success'
    pic = ''
    msg = ''
    real_file = ''
    try:
        if not f:
            if request.FILES:
                if name:
                    f = request.FILES[name]
                else:
                    f = request.FILES.values()[0]
        if f:
            if f.size > limit_size * 1024 * 1024:
                state = 'failed'
                msg = u'上传文件最大为%sM' % limit_size

            ext = filelib.get_file_ext(f.name)
            if not (ext.lower() in limit_file_type):
                msg = u'文件格式不正确,%s' % ext
                state = 'failed'

            new_file_info = filelib.get_new_upload_file_info(f.name)
            real_file = new_file_info['real_file']
            destination = open(real_file, 'wb+')
            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()

            if resize:
                if ext != 'gif' or resize_gif:
                    resize_image_success = imagelib.create_small_pic_from_file(file=real_file,dst_w=resize[0],dst_h=resize[1],quality=image_quality,dst_img=real_file,is_thumbnails=True)
            pic = new_file_info['new_file']
            real_file = new_file_info['real_file']
        else:
            state = 'failed'
            msg = u'请选择图片'
    except:
        state = 'failed'
        msg = traceback.format_exc()
    return {'pic': pic,'real_file':real_file, 'state': state,'msg':msg}



def remote_load_pic(request,url):
    '''从远程下载图片到文件系统'''
    state = 'FAILED'
    new_file = ''
    size = (0,0)
    file_type = ''
    try:
        if not url.lower().startswith('http://') and not url.lower().startswith('https://'):
            url = ''.join(('http://',request.get_host(),url))
        ext=filelib.get_file_ext(url)
        data=get_url_content(url=url)
        file_info = filelib.get_new_upload_file_info(url)
        with open(file_info['real_file'],'wb') as f:
            f.write(data)

        # 获取图片尺寸
        size = (0, 0)
        try:
            f = open(file_info['real_file'], 'rb')
            image = Image.open(f)
            size = image.size
            file_type = filelib.get_file_type(fp=f)
        except:
            try:
                f.close()
            except:
                pass

        if not file_type:
            file_type = ext

        new_file = file_info['new_file']
        state = 'SUCCESS'
    except:
        state=u'图片地址不正确'
    return {'file':new_file,'state':state,'size':size,'file_type':file_type}

def download(url,target_file):
    '''下载远程url文件到指定的目标文件'''
    try:
        data = urllib2.urlopen(url).read()
        f = open(target_file, 'wb')
        f.write(data)
        f.close()
        return True
    except:
        return False




if __name__ == '__main__':

    #print(remote_load_pic(request=None,url='http://www.bandao.cn/gao/upload/201701/20170109171719_Y24C3GSU.jpg'))
    response = post(url='http://muji.bandao.cn/api/blog/upload/',params={'title':u'你好','content':u'你好呀，我们很喜欢你','user_id':47})
    print(response.read())
