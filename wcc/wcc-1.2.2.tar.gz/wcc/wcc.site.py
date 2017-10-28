#Wikicivi Crawler Client SDK
import os,time
import threading
import datetime
import urllib
import oss2
import shelve
import socket
import requests
import traceback
from hashlib import md5
from datetime import date
import os,sys
import struct
import random
import json
#pip install Pillow
from PIL import Image
from io import BytesIO
#tinytag对有些mp3读不出duration,我备用eyed3试下,eyed3不行的话,用mutagen
from tinytag import TinyTag
#pip3 install eyeD3(注意大小写)
import eyed3
from mutagen.mp3 import MP3  
import mutagen.id3  
from mutagen.id3 import ID3
from mutagen.easyid3 import EasyID3  
import re
import types
import traceback
import getopt
from tinytag import TinyTag
from .osskey import Osskey
from .utils import *
class Wcc:
    def __init__(self):
        self.apimap = {}
    
    wcc_headers = {
        #'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
    }
    
    #https://boonedocks.net/blog/2008/03/10/Determining-Image-File-Types-in-Ruby.html
    #def file_type(file)
    #   case IO.read(file, 10)
    #        when /^GIF8/: ‘gif’
    #        when /^\x89PNG/: 'png’
    #        when /^\xff\xd8\xff\xe0\x00\x10JFIF/: 'jpg’
    #        when /^\xff\xd8\xff\xe1(.*){2}Exif/: 'jpg’
    #        else 'unknown’
    #        end
    #    end
    #
    #最多尝试10次,判断这个远程文件的信息
    #坑：程序总是运行到中途就会卡死，经定位发现是 res = requests.get(url,timeout=1)这句代码出了问题
    #https://www.zhihu.com/question/35321993
    #我估计是GC没有正确释放资源, 卡住了.
    #像爬虫这种IO密集型的程序，本身就不适合利用多进程编程，所以题主用的应该是python的threading库而不是multiprocessing。题主可以将程序改为threading+Queue试试。
    #若要更简单点，题主可以利用gevent等并发框架试试。
    #因为使用requests.get()会卡主，这也说明了requests这种第三方库不是很厉害
    #所以使用python的官方urllib,它是python自己维护的,应该不会卡主
    #
    #第二个问题:如果urlopen目标file_url中有中文的时候,urlopen就会出现如下错误
    #http://t44.tingchina.com/yousheng/历史军事/国士无双/001_关外来的土匪.mp3?key=32bd82ce105b4741e0d7c4b08870d2c3_546431312
    #'ascii' codec can't encode characters in position 14-17: ordinal not in range(128)
    #下面这个帖子说，要对url中的中文进行parse,而且仅对中文
    #http://www.cnblogs.com/LuckyBao/p/6223443.html
    #下面这个帖子说，可以混合用
    #https://www.zhihu.com/question/22899135
    #第一方案
    #socket.setdefaulttimeout(30)    
    #urlreq = urllib.request.Request(file_url, headers=Wcc.wcc_headers)
    #if k % 2 == 1 and k > 0:
    #    #使用自定义的UA和代理IP
    #    proxy = {'http':'61.48.134.245:53109'}
    #    proxy_support = urllib.request.ProxyHandler(proxy)
    #    opener = urllib.request.build_opener(proxy_support)
    #    urllib.request.install_opener(opener)
    #with urllib.request.urlopen(urlreq) as resp:
    #    resp.read()
    #    file_size = resp.headers['content-length']
    #    mime_type = resp.headers['content-type']
    #第二方案
    #response = requests.get(file_url,stream=True,timeout=30,headers=HEAD)
    #file_size = int(response.headers['content-length'])
    #mime_type = response.headers['content-type']
    #第三方案
    #有些图片因为不存在,它们所在的server会返回一些文字
    @staticmethod
    def getFileInfo(file_url_original):
        #file_url = urllib.parse.quote(file_url_original,safe='/:?=&')
        file_url = file_url_original
        for k in range(1,6):
            file_size = 0
            mime_type = "null"
            file_text = ""
            resp = None
            try:
                resp = requests.get(file_url,timeout=300,headers=Wcc.wcc_headers)
                if 'content-length' not in resp.headers:
                    file_size = 0
                    print(resp.headers)
                else:
                    file_size = int(resp.headers['content-length'])
                if 'content-type' not in resp.headers:
                    mime_type = ""
                else:
                    mime_type = resp.headers['content-type']
                break
            except Exception as err:
                #print(traceback.print_exc())
                print(""+file_url+" info err("+str(k)+") "+str(err))
                file_size = 0
                mime_type = "null"
                time.sleep(1)
                if k == 5:
                    print(""+file_url+" info Abort")
                    if resp == None:
                        print("get resp as None")
                    else:
                        print(resp.text)
            finally:
                pass
        
        file_url_ext = file_url.split('.')[-1]
        file_url_host= file_url.replace("http://","").split("/")[0]
        if mime_type == 'image/gif':
            extension = 'gif'
        elif mime_type == 'image/png':
            extension = 'png'
        elif mime_type == 'image/jpeg':
            extension = 'jpg'
        elif mime_type == 'audio/x-m4a':
            extension = 'm4a'
        elif mime_type == 'audio/mpeg':
            extension = 'mp3'
        elif mime_type == 'video/mp4':
            extension = 'mp4'
        elif mime_type == 'text/html; charset=utf-8' and file_url_ext in ["jpg"] and file_url_host in ["www.ting56.com"]:
            #在好多网站观察到图片和m4a都变成了这种content-type
            #http://www.ting56.com/pic/images/2016-11/201611211759927267.jpg
            #未知的mime:text/html; charset=utf-8 for http://www.ting56.com/pic/images/2016-11/201611211759927267.jpg
            mime_type = "image/jpeg"
            extension = "jpg"
        elif mime_type == 'text/html' and file_url_ext in ["m4a"] and file_url_host in ["audio.xmcdn.com"]:
            #未知的mime:text/html for http://audio.xmcdn.com/group15/M02/60/ED/wKgDaFXUZH3iNnE6AJX6ZBlEXF8394.m4a
            mime_type = "audio/x-m4a"
            extension = "m4a"
        elif mime_type == 'null' and file_url_ext in ["m4a"] and file_url_host in ["audio.xmcdn.com"]:
            #未知的mime:null for http://audio.xmcdn.com/group17/M0B/67/AB/wKgJKVf6Pe7wCOrTACU75dNaD5M039.m4a
            mime_type = "audio/x-m4a"
            extension = "m4a"
        else:
            print("unkonw mime:"+mime_type+" for "+file_url)
            mime_type = "null"
            file_size =0
            extension = ''
        return mime_type,extension,file_size

    #为何要设置User Agent
    #有一些网站不喜欢被爬虫程序访问，所以会检测连接对象，如果是爬虫程序，也就是非人点击访问，它就会不让你继续访问，所以为了要让程序可以正常运行，需要隐藏自己的爬虫程序的身份。此时，我们就可以通过设置User Agent的来达到隐藏身份的目的，User Agent的中文名为用户代理，简称UA。
    #User Agent存放于Headers中，服务器就是通过查看Headers中的User Agent来判断是谁在访问。在Python中，如果不设置User Agent，程序将使用默认的参数，那么这个User Agent就会有Python的字样，如果服务器检查User Agent，那么没有设置User Agent的Python程序将无法正常访问网站。
    #Python允许我们修改这个User Agent来模拟浏览器访问，它的强大毋庸置疑。
    #为何使用IP代理
    #User Agent已经设置好了，但是还应该考虑一个问题，程序的运行速度是很快的，如果我们利用一个爬虫程序在网站爬取东西，一个固定IP的访问频率就会很高，这不符合人为操作的标准，因为人操作不可能在几ms内，进行如此频繁的访问。所以一些网站会设置一个IP访问频率的阈值，如果一个IP访问频率超过这个阈值，说明这个不是人在访问，而是一个爬虫程序。
    
    #下载网络上的一个文件,比一般的代码多了如下部分
    #1:对url中的中文进行重编码
    #2:使用UA
    #3:使用代理IP
    #4:检查content-type合content-size
    @staticmethod
    def downloadFile(local_path,file_url):
        if file_url == None:
            print("url must not be None(downloadFile)")
            print(file_url)
            return False
        download_try_count = 10
        try:
            if os.path.exists(local_path):
                return True
            dirname = os.path.dirname(local_path)
            isExists = os.path.exists(dirname)
            if not isExists:
                os.makedirs(dirname)
                print(dirname + '创建成功')
            else:
                pass #print(dirname + '目录已存在')
            t0=time.time()
            file_size = 1
            download_flag = False
            for k in range(1,download_try_count+1):
                try:
                    #坑:此处不建议使用第三方库requests.因为会卡死
                    #使用urlib.request.urlretrieve也会卡死
                    #通过socket类设置全局的超时
                    #坑,有些网站的图片下载需要header,如:http://img.2mme.tv/tu/nvlb1scr2tq.jpg
                    #Urlretrive的下载方式也需要.
                    if download_flag == False:
                        socket.setdefaulttimeout(300)
                        urlreq = urllib.request.Request(file_url,headers=Wcc.wcc_headers)
                        with urllib.request.urlopen(urlreq) as resp:
                            file_size = int(resp.headers['content-length'])
                            file_mime = resp.headers['content-type']
                            if file_mime == "text/html" :
                                print("拒绝下载text/html文件,可能爬虫已被网站封")
                                break
                            with open(local_path, 'wb') as local_file:
                                local_file.write(resp.read())
                        download_flag = True
                        if download_flag == False:
                            socket.setdefaulttimeout(300)
                            urllib.request.urlretrieve(file_url,local_path)
                            download_flag = True
                        break
                except Exception as err:
                    print("dwloadFile:"+file_url +" Fail "+str(k)+"/"+str(download_try_count)+" "+str(err))
                    time.sleep(5)
            if download_flag == True:
                t1=time.time()
                speed = file_size/(t1-t0)
                file_size = file_size/1048576
                speed = speed/1024
                print("dwloadFile:%s %0.2fM %0.2fKps" % (file_url,file_size,speed)) 
                return True
            else:
                print("dwloadFail: "+file_url)
                return False
        except Exception as err:
            print(traceback.print_exc())
            print(err)
            print("dwloadFail: "+file_url)
            return False
        finally:
            pass

    #把网络上的一个文件转移到oss上
    #如果已经存在或者成功返回oss上的url
    #如果失败返回""
    @staticmethod
    def ossUploadUrlFile(file_url,file_oss_path):
            oss_file_url = "http://files.wikicivi.com/"+file_oss_path
            print("OSS url "+oss_file_url)
            has_flag = Wcc.existsFile("wikicivi-files",file_oss_path)
            if has_flag == True:
                print("OSS has "+oss_file_url)
                return oss_file_url
            down_flag = Wcc.downloadFile(file_oss_path,file_url)
            if down_flag == False:
                print("Error:不能回避的错误,下载文件失败 "+file_url)
                return ""
            upload_flag = Wcc.uploadFile(file_oss_path,file_oss_path)
            if upload_flag == False:
                print("Error:不能回避的错误,文件上传失败 "+file_oss_path)
                return ""
            print("OSS url "+oss_file_url+" ok")
            return oss_file_url

    @staticmethod
    def urlget(url,params= None,headers = None):
        if headers != None:
            HEAD = {
                'USER-AGENT': 'MOZILLA/5.0 (WINDOWS NT 6.1; WOW64; RV:52.0) GECKO/20100101 FIREFOX/52.0',
                'ACCEPT-LANGUAGE': 'ZH-CN,ZH;Q=0.8,EN-US;Q=0.5,EN;Q=0.3',
                'CONNECTION': 'KEEP-ALIVE'
            }
        else:
            HEAD = headers
        Cfg_TimeoutDelay = 10
        resp_text = ""
        err_text = "error"
        dolog = False
        resp_status_code = 200
        try_count = 0
        for k in range(1,11):
            try:
                request = requests.get(url,params,timeout=Cfg_TimeoutDelay,headers=HEAD)
                if request.status_code != 200:
                    resp_status_code = request.status_code
                    raise Exception("错误的status_code"+str(request.status_code),request)
                resp_text = request.text
                try_count = k
                break
            except requests.exceptions.ConnectTimeout:
                err_text = "ConnectTimeout"
            except requests.exceptions.Timeout:
                err_text = "Timeout"
            except Exception as err:
                err_text = str(err)
            time.sleep(k*1)
            try_count = k
            #print(url+" err("+str(k)+") "+err_text)
            dolog = True
        if dolog == True and resp_text != "":
            print(url+" ok"+"("+str(try_count)+" th)")

        if resp_status_code == 503:
            print("503错误,您的IP可能被封")
        if resp_status_code == 504:
            print("504错误,您的IP可能被封")

        return resp_text
    @staticmethod
    def urlpost(url,payload={},headers={}):
        fixed_HEAD = {
            'USER-AGENT': 'MOZILLA/5.0 (WINDOWS NT 6.1; WOW64; RV:52.0) GECKO/20100101 FIREFOX/52.0',
            'ACCEPT-LANGUAGE': 'ZH-CN,ZH;Q=0.8,EN-US;Q=0.5,EN;Q=0.3',
            'CONNECTION': 'KEEP-ALIVE'
        }
        if headers !={}:
            HEAD = headers
        else:
            HEAD = fixed_HEAD

        Cfg_TimeoutDelay = 10
        resp_json = None
        err_text = "error"
        dolog = False
        response = None
        for k in range(1,6):
            try:
                response = requests.post(url,data=payload,timeout=Cfg_TimeoutDelay,headers=HEAD)
                if response.status_code != 200:
                    print(response.content)
                    raise Exception("错误返回代码"+str(response.status_code),response.content)
                else:
                    try:
                        resp_json = response.json()
                    except Exception as err:
                        resp_json = None
                break
            except requests.exceptions.ConnectTimeout:
                err_text = "ConnectTimeout"
            except requests.exceptions.Timeout:
                err_text = "Timeout"
            except Exception as err:
                err_text = str(err)
                #fixme:想办法在这里解决ip被封后回来的例外是response.json()出错
                # Expecting value: line 1 column 1 (char 0)
                #print(str(response)+":"+response.content)
            resp_json = None
            time.sleep(k*1)
            print(url+" err("+str(k)+") "+err_text)
            dolog = True
        if dolog == True and resp_json != None:
            print(url+" ok")
        return resp_json
 
    @staticmethod
    def getjson(url,payload={},headers={}):
        fixed_HEAD = {
            'USER-AGENT': 'MOZILLA/5.0 (WINDOWS NT 6.1; WOW64; RV:52.0) GECKO/20100101 FIREFOX/52.0',
            'ACCEPT-LANGUAGE': 'ZH-CN,ZH;Q=0.8,EN-US;Q=0.5,EN;Q=0.3',
            'CONNECTION': 'KEEP-ALIVE'
        }
        if headers !={}:
            HEAD = headers
        else:
            HEAD = fixed_HEAD

        Cfg_TimeoutDelay = 10
        resp_json = None
        err_text = "error"
        dolog = False
        response = None
        for k in range(1,6):
            try:
                response = requests.get(url,params=payload,timeout=Cfg_TimeoutDelay,headers=HEAD)
                if response.status_code != 200:
                    print(response.content)
                    raise Exception("错误返回代码"+str(response.status_code),response.content)
                else:
                    try:
                        resp_json = response.json()
                    except Exception as err:
                        resp_json = None
                break
            except requests.exceptions.ConnectTimeout:
                err_text = "ConnectTimeout"
            except requests.exceptions.Timeout:
                err_text = "Timeout"
            except Exception as err:
                err_text = str(err)
                #fixme:想办法在这里解决ip被封后回来的例外是response.json()出错
                # Expecting value: line 1 column 1 (char 0)
                #print(str(response)+":"+response.content)
            resp_json = None
            time.sleep(k*1)
            print(url+" err("+str(k)+") "+err_text)
            dolog = True
        if dolog == True and resp_json != None:
            print(url+" ok")
        return resp_json
    
    def AddArticle(self, art_info):
        batch_ins,batch_ign,batch_err = self.AddArtBatch([art_info])
        if batch_err > 0:
            return 0
        else:
            return 1

    #更新一个用户的关注/粉丝信息,这个usr_follow_info可能非常大,
    #必须分批往上传
    #真实用户的关注应该走其它接口
    def __SetUserFollows(self, uid_inc,user_follow_info):
        try:
            if user_follow_info == {}:
                return 0 ,0,0
            
            if "uid" not in user_follow_info :
                print("setuser_info中缺少uid")
                print(user_follow_info)
                return {}
            if "followers" not in user_follow_info :
                print("setuser_info中缺少followers")
                print(user_follow_info)
                return {}
            if "followees" not in user_follow_info :
                print("setuser_info中缺少followees")
                print(user_follow_info)
                return {}
            if "followoos" not in user_follow_info :
                print("setuser_info中缺少followoos")
                print(user_follow_info)
                return {}

            follows = []
            follows.extend(user_follow_info["followers"])
            follows.extend(user_follow_info["followees"])
            follows.extend(user_follow_info["followoos"])
            
            if len(follows) == 0:
                print("空的关注/粉丝列表")
                return {}
            #先把这些用户都添加注册到数据库
            match_count,ins_count,ign_count,err_count =  self.AddUsers(follows,uid_inc,0)
            if err_count > 0:
                raise Exception("添加用户组错误")
            #把关注/粉丝关系添加到数据库
            match_count,ins_count,ign_count,err_count =  self.AddFollows(user_follow_info,uid_inc)
        except Exception as err:
            print(traceback.print_exc())
            print(err)
        return ins_count,ign_count,err_count


    #更新一个用户的详细信息
    def __SetUserUpdates(self, uid_inc,usr_info):
        if usr_info == {}:
            return 0 ,0,0
        api_url_root = "http://"+self.GetApiHost("api.xdua.org")
        set_usr_msg = Wcc.MakeSetUserMsg(uid_inc,usr_info)
        ins_count = 0
        ign_count = 0
        err_count = 0
        try:
            # 如果文章不重复，并且下载成功，并且上传成功,那么需要插入本条记录
            # requests.exceptions.InvalidHeader: Header value 110 must be of type str or bytes, not <class 'int'>
            headers = {
                'Content-Type':'application/json',
                'Xdua':'110' #header里必须是字符串
            }
            add_msg = {
                "dua_id"  : 110,
                "action"  : 'setusers',
                "users"   : [set_usr_msg]
            }
            response = requests.post(api_url_root+"/users", data=json.dumps(add_msg), headers=headers)
            if response.status_code != 200:
                print(response.content)
                print("Error to post:"+api_url_root)
            else:
                response = response.json()
                if response["status"] == 0:
                    uid          = response["result"]["uid"]
                    ins_count    = response["result"]["updated"]
                    print("updateUsr:"+str(uid)+" "+str(ins_count))
                    #print(response["result"]["updates"])
                else:
                    print("AddUsrBatch Error:!")
                    print(response)
        except Exception as err:
            print(traceback.print_exc())
            print(err)
        return ins_count,ign_count,err_count
    
    #上传一批关注信息,在自然注册用户的关注情况，follow数组只有一项
    def AddFollowBatch(self,follow_batch):
        api_url_root = "http://"+self.GetApiHost("api.xdua.org")
        add_msg_batch = []
        ign_count = 0
        ins_count = 0
        err_count = 0
        all_count = len(follow_batch)
        try:
            for follow_info in follow_batch:
                if "uidfrm1" not in follow_info:
                    raise Exception("缺少uidfrm1",follow_info)
                if "uidfrm2" not in follow_info:
                    raise Exception("缺少uidfrm2",follow_info)
       
            # requests.exceptions.InvalidHeader: Header value 110 must be of type str or bytes, not <class 'int'>
            headers = {
                'Content-Type':'application/json',
                'Xdua':'110' #header里必须是字符串
            }
            add_msg = {
                "dua_id"  : 110,
                "action"  : 'addfollows',
                "follows" : follow_batch
            }
            response = requests.post(api_url_root+"/users", data=json.dumps(add_msg), headers=headers)
            if response.status_code != 200:
                print(response.content)
                print("Error to post:"+api_url_root)
                err_count +=all_count
            else:
                response = response.json()
                if response["status"] == 0:
                    inc= response["result"]["inc"]
                    added = response["result"]["added"]
                    ins_count += added
                    ign_count += all_count - added
                else:
                    print("AddUsrBatch Error:!")
                    print(response)
                    err_count += all_count
                
        except Exception as err:
            print(traceback.print_exc())
            print(err)
            err_count +=all_count
        return ins_count,ign_count,err_count


    #上传一批文章
    def AddUsrBatch(self,usr_batch):
        api_url_root = "http://"+self.GetApiHost("api.xdua.org")
        add_msg_batch = []
        ign_count = 0
        ins_count = 0
        err_count = 0
        all_count = len(usr_batch)
        try:
            for usr_info in usr_batch:
                usr_msg = Wcc.MakeAddUserMsg(usr_info)
                #False,0,'',[],{},()都可以视为假
                if usr_msg:
                    add_msg_batch.append(usr_msg)
                else:
                    print("Fail to Make UsrMsg")
                    print(usr_info)
                    err_count+=1
       
            # 如果文章不重复，并且下载成功，并且上传成功,那么需要插入本条记录
            # requests.exceptions.InvalidHeader: Header value 110 must be of type str or bytes, not <class 'int'>
            headers = {
                'Content-Type':'application/json',
                'Xdua':'110' #header里必须是字符串
            }
            add_msg = {
                "dua_id"  : 110,
                "action"  : 'addusers',
                "users"   : add_msg_batch
            }
            response = requests.post(api_url_root+"/users", data=json.dumps(add_msg), headers=headers)
            if response.status_code != 200:
                print(response.content)
                print("Error to post:"+api_url_root)
                err_count +=all_count
            else:
                response = response.json()
                if response["status"] == 0:
                    uid = response["result"]["uid"]
                    added = response["result"]["added"]
                    ins_count += added
                    ign_count += all_count - added
                else:
                    print("AddUsrBatch Error:!")
                    print(response)
                    err_count += all_count
                
        except Exception as err:
            print(traceback.print_exc())
            print(err)
            err_count +=all_count
        
        #print("addusr_batch:"+str(all_count)+ "  "+str(ins_count)+ "  "+str(ign_count)+" "+str(err_count))
        return ins_count,ign_count,err_count


    #返回的是不在数据库里的元素集合
    def HasArtBatch(self,wwwtid_from_array):
        api_url_root = "http://"+self.GetApiHost("api.wikicivi.com")
        try:
            # requests.exceptions.InvalidHeader: Header value 110 must be of type str or bytes, not <class 'int'>
            headers = {
                'Content-Type':'application/json',
                'Xdua':'110' #header里必须是字符串
            }
            has_msg = {
                "action":"has_articles",
                "wwwtids":wwwtid_from_array
            }
            response = requests.post(api_url_root+"/articles", data=json.dumps(has_msg), headers=headers)
            if response.status_code != 200:
                print(response.content)
                print("Error to post:"+api_url_root)
                return []
            response = response.json()
            if response["status"] == 0:
                wwwtid_array = response["result"]["wwwtids"]
                return wwwtid_array
            else:
                print("hasart_error:"+str(response["reason"])+ " result "+str(response["result"]))
                return []
        except Exception as err:
            #print(traceback.print_exc())
            print(err)
            return []

    #上传一批文章
    def AddArtBatch(self,art_batch):
        api_url_root = "http://"+self.GetApiHost("api.wikicivi.com")
        has_msg_batch = []
        add_msg_batch = []
        ign_count = 0
        ins_count = 0
        err_count = 0
        all_count  = len(art_batch)
        try:
            for art_info in art_batch:
                has_msg_batch.append(art_info['www_from']+":"+str(art_info['tid_from']))    
            #返回的是不在数据库里的元素 
            has_array = self.HasArtBatch(has_msg_batch)
            ign_count += all_count - len(has_array)
        
            for art_info in art_batch:
                wwwtid_from = art_info['www_from']+":"+str(art_info['tid_from'])
                if wwwtid_from in has_array:
                    art_msg = Wcc.MakeArtMsg(art_info)
                    if art_msg:
                        add_msg_batch.append(art_msg)
                    else:
                        print("Fail to Make ArtMsg")
                        print(art_info)
                        err_count+=1
            add_count = len(add_msg_batch)
            if add_count ==0:
                #print("ignArtBatch")
                return ins_count,ign_count,err_count

            # 如果文章不重复，并且下载成功，并且上传成功,那么需要插入本条记录
            # requests.exceptions.InvalidHeader: Header value 110 must be of type str or bytes, not <class 'int'>
            pmc_add_art_msg_delay = 0
            pmc_add_art_msg_t0 = time.time()
            headers = {
                'Content-Type':'application/json',
                'Xdua':'110' #header里必须是字符串
            }
            add_msg = {
                "dua_id"  : 110,
                "action"  : 'add_articles',
                "arts"      :add_msg_batch
            }
            response = requests.post(api_url_root+"/articles", data=json.dumps(add_msg), headers=headers)
            pmc_add_art_msg_t1 = time.time()
            pmc_add_art_msg_delay = pmc_add_art_msg_t1 - pmc_add_art_msg_t0
            if response.status_code != 200:
                print(response.content)
                print("Error to post:"+api_url_root)
                err_count +=add_count
            else: 
                response = response.json()
                if response["status"] == 0:
                    tid = response["result"]["tid"]
                    added = response["result"]["added"]
                    ins_count += added
                    ign_count += add_count - added
                else:
                    print("AddArtBatch Error:!")
                    print(response)
                    err_count += add_count
                
        except Exception as err:
            print(traceback.print_exc())
            print(err)
            err_count +=all_count
        return ins_count,ign_count,err_count
 
    #把一个列表的User分批发送到服务器
    #follow_info包含一个,followers或者followee中的信息可能有多个,比方说还有name,avatar等
    #对于AddFollows,应该有用到uidfrm
    #{
    #    "uid":
    #    "uidfrm":
    #    "followers":[{"uidfrm":8888}]
    #    "followees":[{"uidfrm":8888}]
    #    "followoos":[{"uidfrm":8888}]
    #}
    def AddFollows(self,user_follow_info,batch_id=0,thread_name=""):
        pmc_func_t0 = time.time()
        follow_ins_count  = 0
        follow_ign_count  = 0
        follow_err_count  = 0
        match_count       = len(user_follow_info["followers"]) + len(user_follow_info["followees"]) + 2*len(user_follow_info["followoos"])
        uid        = user_follow_info["uid"]
        uidfrm    = user_follow_info["uidfrm"]
        follows = []
        for item in user_follow_info["followers"]:
            follows.append({"uid1":uid,"uidfrm1":uidfrm,"uidfrm2":item["ustr"]})
        for item in user_follow_info["followees"]:
            follows.append({"uid2":uid,"uidfrm2":uidfrm,"uidfrm1":item["ustr"]})
        for item in user_follow_info["followoos"]:
            follows.append({"uid2":uid,"uidfrm2":uidfrm,"uidfrm1":item["ustr"]})
            follows.append({"uid1":uid,"uidfrm1":uidfrm,"uidfrm2":item["ustr"]})

        max_follow_batch_size = 100
        follow_batch = []
        for follow_info in follows:
            if len(follow_batch) < max_follow_batch_size:
                follow_batch.append(follow_info)
            else:
                batch_ins,batch_ign,batch_err = self.AddFollowBatch(follow_batch)
                follow_batch = []
                follow_ins_count += batch_ins
                follow_ign_count += batch_ign
                follow_err_count += batch_err
                follow_batch.append(follow_info)

        if len(follow_batch)>0:
            batch_ins,batch_ign,batch_err = self.AddFollowBatch(follow_batch)
            follow_batch = []
            follow_ins_count += batch_ins
            follow_ign_count += batch_ign
            follow_err_count += batch_err
        pmc_func_t1 = time.time()
        func_delay = pmc_func_t1 - pmc_func_t0
        func_time  = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print("addFollows: m:%4d i:%4d x:%4d e:%2d s:%6.1f b:%s t:%s w:%4s"
            %(match_count,follow_ins_count,follow_ign_count,follow_err_count,func_delay,batch_id,func_time,thread_name))
        return match_count,follow_ins_count, follow_ign_count, follow_err_count

    #把一个列表的User分批发送到服务器
    def AddUsers(self, users,batch_id=0,thread_name="N"):
        # 参数是个文章数组，数组里的每一项包含一个article和一个usr
        # 这个方法遍历这个数组，对每一项，先传usr后传article
        pmc_func_t0 = time.time()
        usr_ins_count = 0
        usr_ign_count = 0
        usr_err_count  = 0
        match_count = len(users)
        max_usr_batch_size = 100
        usr_batch = []
        for usr_info in users:
            if len(usr_batch) < max_usr_batch_size:
                if "add_flag" not in usr_info:
                    usr_info["add_flag"] = True
                if usr_info["add_flag"] == True:
                    usr_batch.append(usr_info)
            else:
                batch_ins,batch_ign,batch_err = self.AddUsrBatch(usr_batch)
                usr_batch = []
                usr_ins_count += batch_ins
                usr_ign_count += batch_ign
                usr_err_count += batch_err
                usr_batch.append(usr_info)

        if len(usr_batch)>0:
            batch_ins,batch_ign,batch_err = self.AddUsrBatch(usr_batch)
            usr_batch = []
            usr_ins_count += batch_ins
            usr_ign_count += batch_ign
            usr_err_count += batch_err
        pmc_func_t1 = time.time()
        func_delay = pmc_func_t1 - pmc_func_t0
        func_time  = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print("addArtUser: m:%4d i:%4d x:%4d e:%2d s:%6.1f b:%s t:%s w:%4s"
            %(match_count,usr_ins_count,usr_ign_count,usr_err_count,func_delay,batch_id,func_time,thread_name))
        return match_count,usr_ins_count, usr_ign_count, usr_err_count

    #上传WCC性能数据到服务器统计表
    def AddWccPmc(self,www_from,pmctype,m_cnt,i_cnt,x_cnt,e_cnt):
        api_url_root = "http://"+self.GetApiHost("api.wikicivi.com")
        #api_url_root = "http://api.wikicivi.com"
        try:
            headers = {'Content-Type':'application/json','Xdua':'110'} #header里必须是字符串
            api_url = api_url_root+"/wccpmc/"+pmctype+"/"+www_from+"/"+str(m_cnt)+"_"+str(i_cnt)+"_"+str(x_cnt)+"_"+str(e_cnt)
            response = requests.post(api_url,headers=headers)
            if response.status_code != 200:
                print(response.content)
                print("Error to post:"+api_url_root)
                return False
            else: 
                response = response.json()
                if response["status"] == 0:
                    pass
                    return True
                else:
                    print("AddWccPmc Error:!")
                    print(response)
                    return False
        except Exception as err:
            print(traceback.print_exc())
            print(err)
            return False
        return True
 
    def AddArticles(self, articles,batch_id=0,thread_name="N"):
        # 参数是个文章数组，数组里的每一项包含一个article和一个usr
        # 这个方法遍历这个数组，对每一项，先传usr后传article
        pmc_func_t0 = time.time()
        www_from = "editor"
        art_ins_count = 0
        art_ign_count = 0
        art_err_count  = 0
        usr_ins_count = 0
        usr_ign_count = 0
        usr_err_count  = 0

        match_count = len(articles)
        
        max_art_batch_size = 20
        max_usr_batch_size = 100
        usr_batch = []
        for item in articles:
            if 'user' not in item:
                print("item should have user")
                print(item)
                continue
            usr_info = item['user']
            if len(usr_batch) < max_usr_batch_size:
                if "add_flag" not in usr_info:
                    usr_info["add_flag"] = True
                if usr_info["add_flag"] == True:
                    usr_batch.append(usr_info)
            else:
                batch_ins,batch_ign,batch_err = self.AddUsrBatch(usr_batch)
                usr_batch = []
                usr_ins_count += batch_ins
                usr_ign_count += batch_ign
                usr_err_count += batch_err
                usr_batch.append(usr_info)

        if len(usr_batch)>0:
            batch_ins,batch_ign,batch_err = self.AddUsrBatch(usr_batch)
            usr_batch = []
            usr_ins_count += batch_ins
            usr_ign_count += batch_ign
            usr_err_count += batch_err

        art_batch = []
        for item in articles:
            if 'article' not in item:
                print("item should have article")
                print(item)
                continue
            art_info  = item['article']
            www_from = art_info["www_from"]
            art_batch.append(art_info)
            if len(art_batch) >= max_art_batch_size:
                batch_ins,batch_ign,batch_err = self.AddArtBatch(art_batch)
                art_batch = []
                art_ins_count += batch_ins
                art_ign_count += batch_ign
                art_err_count += batch_err

        if len(art_batch)>0:
            batch_ins,batch_ign,batch_err = self.AddArtBatch(art_batch)
            art_batch = []
            art_ins_count += batch_ins
            art_ign_count += batch_ign
            art_err_count += batch_err

        pmc_func_t1 = time.time()
        func_delay = pmc_func_t1 - pmc_func_t0
        func_time  = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print("addArticle: m:%4d i:%4d x:%4d e:%2d s:%6.1f b:%s t:%s w:%4s"
            %(match_count,art_ins_count,art_ign_count,art_err_count,func_delay,batch_id,func_time,thread_name))
        print("addArtUser: m:%4d i:%4d x:%4d e:%2d s:%6.1f b:%s t:%s w:%4s"
            %(match_count,usr_ins_count,usr_ign_count,usr_err_count,func_delay,batch_id,func_time,thread_name))
        self.AddWccPmc(www_from,"AddArt",match_count,art_ins_count,art_ign_count,art_err_count)
        self.AddWccPmc(www_from,"AddUser",match_count,usr_ins_count,usr_ign_count,usr_err_count)
        return match_count,art_ins_count, art_ign_count, art_err_count
    
    #坑,当客户端线程64+的时候,负载均衡服务器的cpu利用率一直降不下来，以为这些线程每时每刻都在调用这个接口
    #导致负载均衡服务器压力大
    def GetApiHost(self,api_name):
        try:
            apimap = self.apimap
            #apimap = Wcc.getParam("apimap","apimap",None)
            cur_time = time.time()
            
            #多线程情况下访问shelve会经常瞬时并发,导致resource temporaly unavailable,
            #我们使用random来使得resource的访问有一点偏差，不要都在60秒后一起访问
            if api_name in apimap and apimap[api_name]["utime"] > cur_time - (60 +random.random()*5):
                api_iport = apimap[api_name]["iport"]
                return api_iport 

            
            # 查询对应的content在服务器是否有重复，原理就是查询content_md5是否重复
            # requests.exceptions.InvalidHeader: Header value 110 must be of type str or bytes, not <class 'int'>
            headers = {
                'Content-Type':'application/json',
                'Xdua':'110' #header里必须是字符串
            }
            msg_api_url = "http://slb.xdua.org/apimap/http/" + api_name;
            response = requests.get(msg_api_url,headers=headers,timeout=30)
            if response.status_code != 200:
                print(response.content)
                return api_name
            response = response.json()
            if response["status"] == 0:
                result = response["result"]
                api_iport =  result["iport"]
                apimap[api_name] = {"iport":api_iport,"utime":time.time()}
                #Wcc.setParam("apimap","apimap",apimap)
                self.apimap = apimap
                return api_iport
            else:
                print('服务器GetApiHost出错')
                return api_name
        except Exception as err:
            print(err)
            print(traceback.print_exc())
            print("fail to get slb. use default api_name "+api_name)
            return api_name


    #根据www_from返回inc
    def GetArtTidByFrom(self,site_from_str):
        get_msg = {
            "action"  : 'get_article_tid_by_from',
            "art_from": site_from_str,
        }
        headers = {
            'Content-Type':'application/json'
        }
        response = requests.post("http://api.wikicivi.com/articles", data = json.dumps(get_msg), headers=headers)
        response = response.json()
        if response["status"] == 0:
            result = response["result"]
            tid = result["tid"]
            return tid
        else:
            return 0

    ##返回值 tid_inc,tid_from,last_comment_tid_from
    #tid_inc:文章的inc
    #tid_From:文章的来源网站tid
    #last_comment_tid_from:最后一个评论的tid
    def GetNextArtLikeFrom(self,www_from,ref_inc):
        api_url_root = "http://"+self.GetApiHost("api.wikicivi.com")
        headers = {
            'Content-Type':'application/json',
            'Xdua':'110' #header里必须是字符串
        }
        msg_api_url = api_url_root+'/article/tidfrm/next/'+www_from+"/"+str(ref_inc)
        response = requests.get(msg_api_url,headers=headers)
        if response.status_code != 200:
            print(response.content)
            return 0,0,0,0
        response = response.json()
        if response["status"] == 0:
            result  = response["result"]
            tid_inc = result["tid_inc"]
            tid_from = result["tid_from"]
            comt_ctime = result["comt_ctime"]
            comt_count = result["comt_count"]
            return tid_inc,tid_from,comt_ctime,comt_count
        else:
            return 0,0,0,0 

    def GetPrevArtLikeFrom(self,www_from,ref_inc):
        api_url_root = "http://"+self.GetApiHost("api.wikicivi.com")
        headers = {
            'Content-Type':'application/json',
            'Xdua':'110' #header里必须是字符串
        }
        msg_api_url = api_url_root+'/article/tidfrm/prev/'+www_from+"/"+str(ref_inc)
        response = requests.get(msg_api_url,headers=headers)
        if response.status_code != 200:
            print(response.content)
            return 0,0,0,0
        response = response.json()
        if response["status"] == 0:
            result  = response["result"]
            tid_inc = result["tid_inc"]
            tid_from = result["tid_from"]
            comt_ctime = result["comt_ctime"]
            comt_count = result["comt_count"]
            return tid_inc,tid_from,comt_ctime,comt_count
        else:
            print(response)
            return 0,0,0,0 


    def GetNextUidLikeFrom(
        self,
        usr_inc,
        usr_from,        
    ):
        api_url_root = "http://"+self.GetApiHost("api.xdua.org")
        get_msg = {
            "action"  : 'get_next_uid_like_from',
            "usr_inc": usr_inc,
            "usr_from": usr_from,
        }
        headers = {
            'Content-Type':'application/json'
        }
        response = requests.post(api_url_root+"/users", data = json.dumps(get_msg), headers=headers)
        if response.status_code != 200:
            print(str(response))
            print(response.content)
            return 0,"null"
        response = response.json()
        if response["status"] == 0:
            result = response["result"]
            uid = result["uid"]
            isfrom = result["isfrom"]
            return uid,isfrom
        else:
            return 0,"null"

    def GetPrevUidLikeFrom(
            self,
        usr_inc,
        usr_from,        
    ):
        api_url_root = "http://"+self.GetApiHost("api.xdua.org")
        get_msg = {
            "action"  : 'get_prev_uid_like_from',
            "usr_inc": usr_inc,
            "usr_from": usr_from,
        }
        headers = {
            'Content-Type':'application/json'
        }
        response = requests.post(api_url_root+"/users", data = json.dumps(get_msg), headers=headers)
        if response.status_code != 200:
            print(str(response))
            print(response.content)
            return 0,"null"
        response = response.json()
        if response["status"] == 0:
            result    = response["result"]
            uid        = result["uid"]
            isfrom    = result["isfrom"]
            return uid,isfrom
        else:
            return 0,"null"

    def __getMaxart(self,www_from):
        #api_url_root = "http://"+self.GetApiHost("api.wikicivi.com")
        api_url_root = "http://api.wikicivi.com"
        headers = {
            'Content-Type':'application/json',
            'Xdua':'110' #header里必须是字符串
        }
        msg_api_url = api_url_root+'/article/maxart/'+www_from
        try:
            response = requests.get(msg_api_url,headers=headers)
            if response.status_code != 200:
                print(response.content)
                return 0,0
            response = response.json()
            if response["status"] == 0:
                result  = response["result"]
                max_ctime = result["max_ctime"]
                max_tid_from = result["max_tid_from"]
                return max_ctime,max_tid_from
            else:
                print(response)
                return 0,0 
        except Exception as err:
            print(err)
            return 0,0 


        get_msg = {
            "action"  : 'get_prev_uid_like_from',
            "usr_inc": usr_inc,
            "usr_from": usr_from,
        }
        headers = {
            'Content-Type':'application/json'
        }
        response = requests.post(api_url_root+"/users", data = json.dumps(get_msg), headers=headers)
        if response.status_code != 200:
            print(str(response))
            print(response.content)
            return 0,"null"
        response = response.json()
        if response["status"] == 0:
            result    = response["result"]
            uid        = result["uid"]
            isfrom    = result["isfrom"]
            return uid,isfrom
        else:
            return 0,"null"



    def setUserInc(self,www_from,user_inc):
        return Wcc.setParam(www_from,"usr_inc",user_inc)
    def getUserInc(self,www_from):
        return Wcc.getParam(www_from,"usr_inc",0)
    def setArtInc(self,www_from,art_inc):
        return Wcc.setParam(www_from,"art_inc",art_inc)
    def getArtInc(self,www_from):
        return Wcc.getParam(www_from,"art_inc",0)
    def setPrevArtInc(self,www_from,art_inc):
        return Wcc.setParam(www_from,"prev_art_inc",art_inc)
    #-1表示最大值,服务器也知道
    def getPrevArtInc(self,www_from):
        return Wcc.getParam(www_from,"prev_art_inc",-1)
    #获取key的值
    @staticmethod
    def getParam(www_from,pkey,default_value):
        www_from_db = www_from+".pdb"
        value = None
        while True:
            try:
                dbase = shelve.open(www_from_db)
                if pkey in dbase:
                    value = dbase[pkey]
                    if value == None:
                        value = default_value
                else:
                    value = default_value
                dbase.close()
                break
            except Exception as err:
                print(err)
                print("retry pdb "+www_from_db)
                time.sleep(0.1)
                continue
        #print("GetParam "+pkey+"'s value: "+str(value))
        return value
    @staticmethod
    def setParam(www_from,pkey,pvalue):
        www_from_db = www_from+".pdb"
        while True:
            try:
                dbase = shelve.open(www_from_db)
                dbase[pkey]  = pvalue
                dbase.close()
                break
            except Exception as err:
                print(err)
                print("retry pdb "+www_from_db)
                time.sleep(0.1)
                continue
        #print("SetParam "+pkey+"'s value: "+str(pvalue))
    #page_url就是包含所有集列表的页面,抓取每一集的信息
    def __addArtbookThread(self,thread_id,www_from,artbooks_array,max_run_seconds):
        exit_reason = "unknown exception"
        time_begin = time.time()
        while True:
            #获取一个artbooks_array的号
            artbook_inc = 0
            try:
                self.lock.acquire()
                artbook_inc = Wcc.getParam(www_from,"artbook_inc",0)
                Wcc.setParam(www_from,"artbook_inc",artbook_inc+1)
                print("thread "+str(thread_id)+" aquire "+str(artbook_inc))
                self.lock.release()
            except Exception as err:
                print(err)
                print("访问pdb例外: 因为涉及线程锁。退出本次爬虫")
                break 
            if artbook_inc >= len(artbooks_array):
                #print("没有合法的artbook_inc了,退出线程."+str(artbook_inc)+" Thread exit: "+str(thread_id))
                #设为1表示这个线程退出了
                break
            
            #print('Thread '+str(thread_id)+' crawl book:'+str(artbook_inc))
            try:
                articles = artbooks_array[artbook_inc]
                if len(articles) > 0:
                    match_count,insert_count, ignore_count, error_count = self.AddArticles(articles,artbook_inc,thread_id)
            except Exception as e:
                exit_reason = "exception="+str(e)
                print(traceback.print_exc())
                print(e)
            if max_run_seconds > 0 and time.time() - time_begin > max_run_seconds:
                exit_reason = "run time expired"
                break
        print("Thread "+str(thread_id)+" exit due to "+exit_reason)

    def __addArtbookParallel(self,www_from,artbooks_array,max_wmt,max_run_seconds):
        #下面是用多线程来爬去数据
        self.artbook_inc  = 0
        threads = []
        self.lock = threading.Lock()
        #创建max_wmt个线程
        for tk in range(max_wmt):
            try:
                thread_id = tk
                t = threading.Thread(target = self.__addArtbookThread, args = (thread_id,www_from,artbooks_array,max_run_seconds))
                t.start()
                threads.append(t)
                print("Thread "+str(thread_id)+" spawn")
            except Exception as err:
                print(err)
                print("线程创建失败:"+err)
                time.sleep(1)
        #等待所有线程执行完毕,退出
        for t in threads:
            t.join()
        print("wcc exit")

    def __addArtbookSerial(self,www_from,artbooks_array,max_run_seconds):
        exit_reason = "unknown exception"
        artbook_inc = 0
        time_begin = time.time()
        max_run_out = False
        while True:
            artbook_inc = Wcc.getParam(www_from,"artbook_inc",0)
            Wcc.setParam(www_from,"artbook_inc",artbook_inc+1)
            if artbook_inc >= len(artbooks_array):
                exit_reason = "job finished with book_inc:"+str(artbook_inc)
                break
            #print('Crawl Book:'+str(artbook_inc))
            try:
                articles = artbooks_array[artbook_inc]
                if len(articles) > 0:
                    match_count,insert_count, ignore_count, error_count = self.AddArticles(articles,artbook_inc,"0")
            except Exception as e:
                exit_reason = "exception="+str(e)
                print(traceback.print_exc())
                print(e)
            if max_run_seconds > 0 and time.time() - time_begin > max_run_seconds:
                exit_reason = "run time expired"
                max_run_out = True
                break
        print("wcc exit")

        #当走完一遍以后，就要把artbook_inc置为0,下次就又可以从头开始
        if max_run_out == False:
            Wcc.setParam(www_from,"artbook_inc",0)
        return
    #子类要实现这个函数,默认只有一个thread,而且当前是1
    def asmArtbooks(self,www_from,max_ctime,max_tid_from,thread_count = 1,tk = 1):
        return []

    
    #子类要实现这个函数
    def hasCommentsOfArt(self):
        return False

    #子类要实现这个函数
    def getCommentsOfArt(self,thread_id,www_from,tid_from,cur_art_inc,comt_ctime,comt_count):
        return []
    
    #子类要实现这个函数
    def hasArticlesOfUsr(self):
        return False


    #子类要实现这个函数
    def getArticlesOfUsr(self,thread_id,www_from,usr_id_str,cur_user_inc):
        return []

    #子类要实现这个函数
    def hasUpdatesOfUsr(self):
        return False


    #子类要实现这个函数
    def getUpdatesOfUsr(self,thread_id,www_from,usr_id_str,cur_user_inc):
        return {}

    #子类要实现这个函数
    def hasFollowsOfUsr(self):
        return False


    #子类要实现这个函数
    def getFollowsOfUsr(self,thread_id,www_from,usr_id_str,cur_user_inc):
        return {}

    #子类要实现这个函数
    def __asmArtbooksMt(self,www_from,max_ctime,max_tid_from,thread_count,tk):
        books = self.asmArtbooks(www_from,max_ctime,max_tid_from,thread_count,tk)
        self.__asmlock.acquire()
        self.__asmbooks.extend(books)
        self.__asmlock.release()
        return
    #子类要实现这个函数
    def __asmArtbooksSt(self,www_from,max_ctime,max_tid_from,thread_count,tk):
        books = self.asmArtbooks(www_from,max_ctime,max_tid_from,thread_count,tk)
        self.__asmbooks.extend(books)
        return


    #每个book表示一个妹子的写真集
    #how有两种可能:new/all
    def __getArtbooks(self,www_from,how,pdb_books_file,thread_count,param_after_time):
        if pdb_books_file.endswith(".pdb"):
            pdb_books_file = pdb_books_file.replace(".pdb","")
        books_info = None
        if pdb_books_file != "":
            books_info = Wcc.getParam(pdb_books_file,"books_info",{"books":[],"utime":0})
        if books_info == None or len(books_info["books"]) == 0:
            print("本地books列表不存在")
            if how == "all":
                max_ctime = 0
                max_tid_from = 0
            else:
                max_ctime,max_tid_from = self.__getMaxart(www_from)
            
            if param_after_time > 0:
                print("max_ctime override to:"+str(param_after_time))
                max_ctime = param_after_time
            print("max_tid_from: "+str(max_tid_from))
            print("max_ctime: "+str(max_ctime) +" "+str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(max_ctime))))
            #创建max_wmt个线程
            self.__asmbooks = []
            if thread_count > 1:
                self.__asmlock = threading.Lock()
                threads = []
                for tk in range(1,thread_count+1):
                    try:
                        thread_id = tk
                        t = threading.Thread(target = self.__asmArtbooksMt, args = (www_from,max_ctime,max_tid_from,thread_count,tk))
                        t.start()
                        threads.append(t)
                        print("Thread "+str(thread_id)+" spawn")
                    except Exception as err:
                        print("Thread spawn fail:"+str(err))
                        time.sleep(1)
                for t in threads:
                    t.join()
                print("thread all joined")
            else:
                self.__asmArtbooksSt(www_from,max_ctime,max_tid_from,1,1)
            books_info = {"books":self.__asmbooks,"utime":time.time()}
            Wcc.setParam(www_from+".big","books_info",books_info)
            print("更新本地books列表")
        
        books = books_info["books"]
        if len(books) == 0:
            print("错误:空的books列表")
            return []
        print("本地books列表一共 "+str(len(books))+" 本书")
        return books

    #用"__"做为前缀定义类的内部函数之后，实践发现这个函数将不能被继承。即使子类继承并重新实现了这个函数，那么当父类引用指向子类对象的时候，调用这个函数调用的还是父类的这个函数。
    def __getUsrUpdatesThread(self,thread_id,www_from,max_run_seconds):
        exit_reason = "unknown exception"
        try:
            time_begin = time.time()
            while True:
                if max_run_seconds > 0 and time.time() - time_begin > max_run_seconds:
                    exit_reason = "run time expired"
                    break
                try:
                    self.lock.acquire()
                    usr_updated_inc = Wcc.getParam(www_from,"usr_updated_inc",0)
                    usr_updated_inc,isfrom = self.GetNextUidLikeFrom(usr_updated_inc,www_from+":")
                    if usr_updated_inc == None:
                        usr_updated_inc = 0
                    if usr_updated_inc != 0:
                        usr_id_str = isfrom.replace(www_from+":", "")
                        Wcc.setParam(www_from,"usr_updated_inc",usr_updated_inc)
                except Exception as err:
                    usr_updated_inc = 0
                    print(err)
                finally:
                    self.lock.release()
                if usr_updated_inc != 0:
                    usr_info = self.getUpdatesOfUsr(thread_id,www_from,usr_id_str,usr_updated_inc)
                    if usr_info !={}:
                        self.__SetUserUpdates(usr_updated_inc,usr_info)
                else:
                    print("Find no User to crawl article")
                    print("Restart from the min uid")
                    Wcc.setParam(www_from,"usr_updated_inc",0)
                    continue
        except Exception as err:
            print(traceback.print_exc())
            print(err)
        print("Thread "+str(thread_id)+" exit due to "+exit_reason)

    #用"__"做为前缀定义类的内部函数之后，实践发现这个函数将不能被继承。即使子类继承并重新实现了这个函数，那么当父类引用指向子类对象的时候，调用这个函数调用的还是父类的这个函数。
    def __getUsrFollowsThread(self,thread_id,www_from,max_run_seconds):
        exit_reason = "unknown exception"
        try:
            time_begin = time.time()
            while True:
                if max_run_seconds > 0 and time.time() - time_begin > max_run_seconds:
                    exit_reason = "run time expired"
                    break
                try:
                    self.lock.acquire()
                    usr_follow_inc = Wcc.getParam(www_from,"usr_follow_inc",0)
                    usr_follow_inc,isfrom = self.GetNextUidLikeFrom(usr_follow_inc,www_from+":")
                    if usr_follow_inc == None:
                        usr_follow_inc = 0
                    if usr_follow_inc != 0:
                        usr_id_str = isfrom.replace(www_from+":", "")
                        Wcc.setParam(www_from,"usr_follow_inc",usr_follow_inc)
                except Exception as err:
                    usr_follow_inc = 0
                    exit_reason = "exception="+str(err)
                finally:
                    self.lock.release()
                if usr_follow_inc != 0:
                    usr_follow_info = self.getFollowsOfUsr(thread_id,www_from,usr_id_str,usr_follow_inc)
                    if usr_follow_info !={}:
                        self.__SetUserFollows(usr_follow_inc,usr_follow_info)
                else:
                    print("Find no User to crawl article")
                    print("Restart from the min uid")
                    Wcc.setParam(www_from,"usr_follow_inc",0)
                    continue
        except Exception as err:
            print(traceback.print_exc())
            print(err)
            exit_reason = "exception="+str(err)
        print("Thread "+str(thread_id)+" exit due to "+exit_reason)


    #用"__"做为前缀定义类的内部函数之后，实践发现这个函数将不能被继承。即使子类继承并重新实现了这个函数，那么当父类引用指向子类对象的时候，调用这个函数调用的还是父类的这个函数。
    def __getUsrArticleThread(self,thread_id,www_from,max_run_seconds):
        exit_reason = "unknown exception"
        try:
            time_begin = time.time()
            while True:
                if max_run_seconds > 0 and time.time() - time_begin > max_run_seconds:
                    exit_reason = "run time expired"
                    break
                try:
                    self.lock.acquire()
                    cur_user_inc = self.getUserInc(www_from)
                    cur_user_inc,isfrom = self.GetNextUidLikeFrom(cur_user_inc,www_from+":")
                    if cur_user_inc == None:
                        cur_user_inc = 0
                    if cur_user_inc != 0:
                        usr_id_str = isfrom.replace(www_from+":", "")
                        self.setUserInc(www_from,cur_user_inc)
                except Exception as err:
                    cur_user_inc = 0
                    print(err)
                    exit_reason = "exception="+str(err)
                finally:
                    self.lock.release()
                if cur_user_inc != 0:
                    articles = self.getArticlesOfUsr(thread_id,www_from,usr_id_str,cur_user_inc)
                    if len(articles) >0:
                        self.AddArticles(articles,str(cur_user_inc)+"/"+usr_id_str,thread_id)
                else:
                    print("Find no User to crawl article")
                    print("Restart from the min uid")
                    self.setUserInc(www_from,0)
                    continue
        
        except Exception as err:
            print(traceback.print_exc())
            print(err)
            exit_reason = "exception="+str(err)
        print("Thread "+str(thread_id)+" exit due to "+exit_reason)


    #坑:用try要非常小心,任何一个语句都会导致进入except,处理不当会导致死锁
    #坑:getPrevArtInc会调用shelve,这个在多线程下回出现Resource temporarily unavailable的例外
    #   这个地方一定要放到try里
    #    一定要放对位置,别让excpetion调到while循环外,让线程退出而self.lock没释放
    # 因为主线程保证了缺一个线程就会spawn一个线程，所以这个时候，只要保证self.lock/release就行，不要太care线程退出问题

    def __getArtCommentThread(self,thread_id,www_from,max_run_seconds):
        exit_reason = "unknown exception"
        try:
            time_begin = time.time()
            while True:
                if max_run_seconds > 0 and time.time() - time_begin > max_run_seconds:
                    exit_reason = "run time expired"
                    break
                try:
                    self.lock.acquire()
                    cur_art_inc = self.getPrevArtInc(www_from)
                    cur_art_inc,tid_from,comt_ctime,comt_count = self.GetPrevArtLikeFrom(www_from,cur_art_inc)
                    #如果函数运行错误,导致获取的是空值,要退出执行
                    if cur_art_inc == None:
                        print("Found not int cur_art_inc "+str(cur_art_inc))
                        cur_art_inc = 0
                    if cur_art_inc != 0 :
                        self.setPrevArtInc(www_from,cur_art_inc)
                except Exception as err:
                    print(err)
                    exit_reason = "exception="+str(err)
                    cur_art_inc = 0
                finally:
                    self.lock.release()
                if cur_art_inc != 0:
                    articles = self.getCommentsOfArt(thread_id,www_from,str(tid_from),cur_art_inc,comt_ctime,comt_count)
                    if len(articles) > 0:
                        self.AddArticles(articles,str(cur_art_inc)+"/"+str(tid_from),thread_id)
                else:
                    print("Find bad cur art_inc is:"+str(cur_art_inc))
                    print("Restart:")
                    self.setPrevArtInc(www_from,-1)
                    break
        except Exception as err:
            print(err)
            exit_reason = "exception="+str(err)
        print("Thread "+str(thread_id)+" exit due to "+exit_reason)


    #多线程爬虫
    #循环,等待所有子线程退出
    #第一个参数是线程函数变量，
    #第二个参数args是一个数组变量参数，如果只传递一个值，就只需要i, 
    #如果需要传递多个参数，那么还可以继续传递下去其他的参数，其中的逗号不能少，少了就不是数组了，就会出错。
    #我们都知道python中可以是threading模块实现多线程, 但是模块并没有提供暂停, 恢复和停止线程的方法, 一旦线程对象调用start方法后, 只能等到对应的方法函数运行完毕. 也就是说一旦start后, 
    #线程就属于失控状态. 不过, 我们可以自己实现这些. 一般的方法就是循环地判断一个标志位, 一旦标志位到达到预定的值, 就退出循环. 这样就能做到退出线程了. 但暂停和恢复线程就有点难了, 我一直也不清除有什么好的方法, 直到我看到threading中Event对象的wait方法的描述时.
    def __runThreads(self,www_from,max_pmt,max_wmt,max_run_seconds,thread_func):
        print("本次运行时长最大"+str(max_run_seconds))
        self.lock = threading.Lock()
        self.apimap = {}
        last_sleep_time = time.time()
        threads = []
        for tk in range(max_wmt):
            try:
                thread_id = tk
                t = threading.Thread(target = thread_func, args = (thread_id,www_from,max_run_seconds))
                t.start()
                threads.append(t)
                print("Thread "+str(thread_id)+" spawn")
            except Exception as err:
                print("线程创建失败:"+err)
                time.sleep(1)
        #等待所有线程执行完毕,退出
        for t in threads:
            t.join()
        return
   
    #如果是获取新文章,根本不用保存本地
    #所有操作全部在内存进行
    def __getWwwArticles(self,www_from,how,pdb_books_file,max_pmt,max_wmt,max_run_seconds,param_after_time):
        Wcc.setParam(www_from,"artbook_inc",0)
        books = self.__getArtbooks(www_from,how,pdb_books_file,max_pmt,param_after_time)
        if max_wmt < 1:
            self.__addArtbookSerial(www_from,books,max_run_seconds)
        else:
            self.__addArtbookParallel(www_from,books,max_wmt,max_run_seconds)
        return

    #按用户获取最新的属性,私有,不可重载
    def __getUsrUpdates(self,www_from,max_pmt,max_wmt,max_run_seconds):
        return self.__runThreads(www_from,max_pmt,max_wmt,max_run_seconds,self.__getUsrUpdatesThread)
    #按用户获取关注列表和粉丝列表
    def __getUsrFollows(self,www_from,max_pmt,max_wmt,max_run_seconds):
        return self.__runThreads(www_from,max_pmt,max_wmt,max_run_seconds,self.__getUsrFollowsThread)


    #按用户获取文章,私有,不可重载
    def __getUsrArticles(self,www_from,max_pmt,max_wmt,max_run_seconds):
        return self.__runThreads(www_from,max_pmt,max_wmt,max_run_seconds,self.__getUsrArticleThread)
    #按文章获取评论,私有,不可重载
    def __getArtComments(self,www_from,max_pmt,max_wmt,max_run_seconds):
        return self.__runThreads(www_from,max_pmt,max_wmt,max_run_seconds,self.__getArtCommentThread)

    def __getAllArtbooks(self,www_from,max_pmt,max_wmt,max_run_seconds):
        books = self.asmArtbooks(www_from)
        if max_wmt < 1:
            self.__addArtbookSerial(www_from,books)
        else:
            self.__addArtbookParallel(www_from,books,max_pmt,max_wmt,max_run_seconds)
        return


    #------爬虫入口程序,子类调用的唯一入口
    def run(self,www_from,argv):
        usage = """Usage: """+argv[0]+"""
    -h,--help: 打印本条帮助
    -v,--version: 爬虫框架版本
    -i,--info: 打印wcc爬虫的相关
    -m,--mode: 爬虫的模式,可选有:
        UsrArticle 根据用户id爬取关联文章
        ArtComment 爬取文章的评论
        NewArticle 爬取网站新的文章 [默认]
        AllArticle 爬取网站所有文章
        UsrFollows 爬取用户的粉丝和关注
        UsrUpdates 爬取用户信息的更新
    --pmt: 组装线程数,爬虫第一步,页面爬取的线程数目,默认1
    --wmt: 上传线程数,爬虫第二步,把本地book上传到服务器,默认8
    --books: 在NewArticle,AllArticle 模式下,如有指明,将从pdb文件中读取books进行上传.
    --afterdate: 在NewArticle,AllArticle 模式下,如有指明,将以对应的时间覆盖max_ctime
    --lot: 爬虫的最大运行时间,默认0=无限制。
    """
        #-------------------------------
        wcc_info = """Wcc Help Information:
    Wcc由爱蓝地球工作室开源的爬虫框架.目前仅服务于向wikicivi数据库爬取内容
    开源:https://git.oschina.net/lovearthstudio/wikicivi-wcc-python-sdk
    使用wcc的步骤
    1. 搭建python3环境
    2. pip3 install wcc
    3. 新建python文件,import wcc.Wcc 编写一个类继承wcc.Wcc类
    4. 重载wcc.Wcc类的asmArtBooks方法
    4. 调用类的run方法
    注意: wcc框架是个多线程框架. 爬虫过程分为两步
        1. 启动多线程访问网页,把整个网站分而治之,把内容组装在一个数组,通常命名为books
        2. 再次启动多个线程把books数组加工,验证,上传到wikicivi数据库
    """
        #-------------------------------
        param_mode = "NewArticle"
        param_pmt  = 1
        param_wmt  = 8
        param_lot  = 0
        param_books_file = ""
        param_after_date = 0
        #默认为空,wcc将不会从本地pdb中读取books
        try:
            opts, args = getopt.getopt(argv[1:], 'hivm:', ['help', 'info','version', 'mode','pmt=','wmt=','lot=','books=','afterdate='])
        except Exception as err:
            print(err)
            print(usage)
            return False
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print(usage)
                return False
            if opt in ('-i', '--info'):
                print(wcc_info)
                return False
            elif opt in ('-v', '--version'):
                print('wcc is a PYPI package')
                print('run "pip show wcc" to see details')
                return False
            elif opt in ('-m', '--mode'):
                param_mode = arg
            elif opt in ('--pmt'):
                param_pmt = int(arg)
            elif opt in ('--wmt'):
                param_wmt = int(arg)
            elif opt in ('--lot'):
                param_lot = int(arg)
            elif opt in ('--books'):
                param_books_file = arg
            elif opt in ('--afterdate'):
                param_after_date = int(arg)
            else:
                pass
        if  param_after_date != 0:
            param_after_time = time.mktime(time.strptime(str(param_after_date), "%Y%m%d"))
        else:
            param_after_time = 0
        max_wmt = param_wmt
        max_pmt = param_pmt
        crawl_type = param_mode
        max_run_seconds = param_lot
        pdb_books_file  = param_books_file
        print("Cur Time:"+str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
        """
        wcc 为了防止同意爬虫的同一模式运行多次,搞了个这么lock文件,从而在进程级避免多次运行.
        """
        lock_file_name = www_from+"_"+crawl_type+".lock"
        if os.path.exists(lock_file_name):
            print("Exit due to Found lock file: "+lock_file_name)
            exit()
        lock_file = open(lock_file_name,'w')
        lock_file.write("this lock file exist to prevent wcc run twice with similar mode")
        lock_file.close()
        if  crawl_type == "NewArticle":
            self.__getWwwArticles(www_from,"new",pdb_books_file,max_pmt,max_wmt,max_run_seconds,param_after_time)
        elif crawl_type == "AllArticle":
            self.__getWwwArticles(www_from,"all",pdb_books_file,max_pmt,max_wmt,max_run_seconds,param_after_time)
        elif crawl_type == "UsrArticle":
            if self.hasArticlesOfUsr():
                self.__getUsrArticles(www_from,max_pmt,max_wmt,max_run_seconds)
            else:
                print("爬虫"+www_from+"不支持"+crawl_type)
        elif crawl_type == "UsrUpdates":
            if self.hasUpdatesOfUsr():
                self.__getUsrUpdates(www_from,max_pmt,max_wmt,max_run_seconds)
            else:
                print("爬虫"+www_from+"不支持"+crawl_type)
        elif crawl_type == "UsrFollows":
            if self.hasFollowsOfUsr():
                self.__getUsrFollows(www_from,max_pmt,max_wmt,max_run_seconds)
            else:
                print("爬虫"+www_from+"不支持"+crawl_type)
        elif crawl_type == "ArtComment":
            if self.hasCommentsOfArt():
                self.__getArtComments(www_from,max_pmt,max_wmt,max_run_seconds)
            else:
                print("爬虫"+www_from+"不支持"+crawl_type)
        else:
            print("不支持的模式"+crawl_type)
        
        if os.remove(lock_file_name):
            print("remove lock file: "+lock_file_name)
        exit()

    # 'log_on' #是否打印
    # 'cato'   #文章的种类
    # 'tmpl'   #文章的模板：图片是202
    # 'media'  #文章的媒体
    # 'title'  #文章的题目
    # 'brief'  #文章的描述
    # 'text'   #文章的正文
    # 'param'  #文章的参数
    # 'texts'  #文章的正文
    # 'itemg'  #文章的文件组
    # 'lovec'  #文章强赞数
    # 'likec'  #文章点赞数
    # 'fairc'  #文章一般数
    # 'hatec'  #文章讨厌数
    # 'sickc'  #文章恶心数
    # 'sharc'  #文章分享数
    # 'comtc'  #文章评论数
    # 'starc'  #文章收藏数
    # 'hot'         #文章是否是热点文章
    # 'rid_from'    #根文章在豆瓣网站的tid,电影本身是根文章,所以,rid_from为""
    # 'pid_from'    #父文章在豆瓣网站的tid,电影本身没有父文章,pid_from为""
    # 'tid_from'    #本文章在豆瓣网站的tid,
    # 'eid_from'    #这篇文章的导演列表的第一个:dbn.cbt:***
    # 'www_from'    #作者用户在豆瓣网站上的唯一标识:dbn.cbt:***
    # 'art_ctime'   #文章的创建时间
    # 'art_tags'    #文章的tags

    ##输入一个art_info,输出一个art_msg
    @staticmethod
    def MakeArtMsg(art_info):
        try:
            if "log_on" not in art_info :
                art_info['log_on'] = False
            if art_info['log_on'] == True:
                print("\n")
                currentTime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                print("currenTime:"+currentTime)
        
            if "eid" not in art_info :
                art_info['eid'] = 0
            if "sid" not in art_info :
                art_info['sid'] = 0
        
            if "cato" not in art_info :
                print("Error: cato not in keys of art_info\n")
                print(art_info)
                return None
            
            if "tmpl" not in art_info :
                print("Error: tmpl not in keys of art_info\n")
                print(art_info)
                return None
        
            if "media" not in art_info :
                print("Error: media not in keys of art_info\n")
                print(art_info)
                return None
        
            tags = []
            if "tags" in art_info and art_info['tags'] != []:
                tags.extend(art_info['tags'])
            else:
                print("Error: tags not in keys of art_info\n")
                print(art_info)
                return None
        
            if "likec" not in art_info :
                art_info['likec'] = 0
        
            if "lovec" not in art_info :
                art_info['lovec'] = 0
        
            if "hatec" not in art_info :
                art_info['hatec'] = 0
        
            if "sickc" not in art_info :
                art_info['sickc'] = 0
        
            if "fairc" not in art_info :
                art_info['fairc'] = 0
        
            if "comtc" not in art_info :
                art_info['comtc'] = 0
        
            if "sharc" not in art_info :
                art_info['sharc'] = 0
        
            if "starc" not in art_info :
                art_info['starc'] = 0
        
            if "viewc" not in art_info :
                art_info['viewc'] = 0
        
            if "hitdc" not in art_info :
                art_info['hitdc'] = 0
        
            if "hot" not in art_info :
                art_info['hot'] = 0
        
            if "eid_from" not in art_info :
                print("Error: eid_from not in keys of art_info\n")
                print(art_info)
                return None
        
            if art_info["eid_from"]=="":
                print("Error: eid_from can not be empty string\n")
                print(art_info)
                return None
        
            if "tid_from" not in art_info :
                print("Error: tid_from not in keys of art_info\n")
                print(art_info)
                return None
        
            if "www_from" not in art_info :
                print("Error: www_from not in keys of art_info\n")
                print(art_info)
                return None
        
            if "rid_from" not in art_info :
                art_info['rid_from'] = 0
        
            if "pid_from" not in art_info :
                art_info['pid_from'] = 0
        
            if "art_ctime" not in art_info :
                print("Error: art_ctime not in keys of art_info\n")
                print(art_info)
                return None
 
            if "art_utime" not in art_info :
                art_info["art_utime"] = 0 

            content = {}
            if "title" in art_info and art_info['title'] != "":
                content["title"] = art_info['title']
        
            if "brief" in art_info and art_info['brief'] != "":
                content["brief"] = art_info['brief']
        
            if "text" in art_info and art_info['text'] != "":
                content["text"] = art_info['text']
        
            if "texts" in art_info and art_info['texts'] != []:
                content["texts"] = art_info['texts']
        
            if "param" in art_info and art_info['param'] != {}:
                content["param"] = art_info['param']
        
            if "itemg" in art_info and art_info['itemg'] != {}:
                content["itemg"] = art_info['itemg']
        
            if "itemg" in art_info:
                for art_item in art_info['itemg']["main"]:
                    if "datas" in art_item:
                        new_datas = []
                        for art_file in art_item["datas"]:
                            new_art_file = Wcc.make_fitem(art_file)
                            if new_art_file == None:
                                print("制作datas fitem失败")
                                return None
                            else:
                                new_datas.append(new_art_file)
                        art_item["datas"] = new_datas

                    if "cover" in art_item:
                        new_cover = []
                        for art_file in art_item["cover"]:
                            new_art_file = Wcc.make_fitem(art_file)
                            if new_art_file == None:
                                print("制作cover fitem失败")
                                return None
                            else:
                                new_cover.append(new_art_file)
                        art_item["cover"] = new_cover
                    if "video" in art_item:
                        new_video = []
                        for art_file in art_item["video"]:
                            new_art_file = Wcc.make_fitem(art_file)
                            if new_art_file == None:
                                print("制作video fitem失败")
                                return None
                            else:
                                new_video.append(new_art_file)
                        art_item["video"] = new_video
                        
        
            # 生成本地的url
            #content字段一定不能为空
            if content =={}:
                raise Exception("意料之外的content字段,不应该为空")
        
             #json_dumps的参数 sort_key: 默认是False，即不对进行排序操作
            #如果不加sort_key,每次dumps出来的key的顺序是随机的,这个导致md5失效
            #参考：https://git.oschina.net/lovearthhome/radar.wikicivi.com/issues/3
            msg = {
                "flag"      : 94,
                "cato"      : art_info['cato'],
                "tmpl"      : art_info['tmpl'],
                "media"      : art_info['media'],
                "tags"      : json.dumps(tags, ensure_ascii=False,sort_keys=True),
                "content" : json.dumps(content, ensure_ascii=False,sort_keys=True),
                "likec"   : art_info['likec'],
                "lovec"   : art_info['lovec'],
                "fairc"   : art_info['fairc'],
                "hatec"   : art_info['hatec'],
                "sickc"   : art_info['sickc'],
                "sharc"   : art_info['sharc'],
                "comtc"   : art_info['comtc'],
                "starc"   : art_info['starc'],
                "viewc"   : art_info['viewc'],
                "hitdc"   : art_info['hitdc'],
                "hot"     : art_info['hot'],
                "sid"     : art_info['sid'],
                "rid_from": art_info['rid_from'],
                "pid_from": art_info['pid_from'],
                "tid_from": art_info['tid_from'],
                "eid_from": art_info['eid_from'],
                "www_from": art_info['www_from'],
                "ctime"   : art_info['art_ctime'],
                "utime"   : art_info['art_utime'],
            }
            return msg 
        except Exception as err:
            print(traceback.print_exc())
            print(err)
            return None


    @staticmethod
    def make_fitem(farray):
        try:
            if "src" not in farray:
                farray["src"]=""
            if "bak" not in farray:
                print("fatal: bak missing")
                return None
            bak_new = []
            for bak_url in farray["bak"]:
                if bak_url == None or bak_url == "":
                    print("url must not be None(make_fitem)")
                    print(farray)
                    continue
                mime_type,file_ext,file_size = Wcc.getFileInfo(bak_url)
                if mime_type == "null" or file_size ==0 or file_ext == "" :
                    print("ErrbakUrl:"+bak_url)
                    print(farray)
                    continue
                else:
                    bak_new.append(bak_url)
            if len(bak_new) == 0:
                print("EmptybakNew exit.")
                print(farray)
                return None
            farray["bak"] = bak_new
            farray["mime"] = mime_type 
            mime_main = mime_type.split("/")[0]
            mime_sub = mime_type.split("/")[1]
            file_url = bak_new[0]
            #获取file_url的md5码.如果bak地址是files.wikicivi.com或者files.xdua.org里的文件,那么我们md5码就是原来的MD5码
            #生成src字段
            if "http://files.wikicivi.com/" in file_url:
                file_urlmd5_localpath = file_url.replace("http://files.wikicivi.com/","")
                file_datmd5_localpath = file_urlmd5_localpath
            elif "http://files.xdua.org/" in file_url:
                file_urlmd5_localpath = file_url.replace("http://files.xdua.org/","")
                file_datmd5_localpath = file_urlmd5_localpath
            else:
                file_urlmd5 = md5(file_url.encode(encoding='utf_8')).hexdigest()
                #如果src里有暗示文件的存放目录，那么使用这个目录
                file_urlmd5_localpath = file_urlmd5+'.' +file_ext
                file_datmd5_localpath = '#datmd5#'+file_urlmd5+'#datmd5#.'+file_ext
                if mime_main == "image":
                    file_urlmd5_localpath = "Images/" +file_urlmd5_localpath
                    file_datmd5_localpath = "Images/" +file_datmd5_localpath
                elif mime_main == "audio": 
                    file_urlmd5_localpath = "Audios/" +file_urlmd5_localpath
                    file_datmd5_localpath = "Audios/" +file_datmd5_localpath
                elif mime_main == "video": 
                    file_urlmd5_localpath = "Videos/" +file_urlmd5_localpath
                    file_datmd5_localpath = "Videos/" +file_datmd5_localpath
                else:
                    print("未知的mime:"+mime_type+" for "+file_url)
                    print(farray)
                    return None
            
            farray["src"] = file_urlmd5_localpath
            if "Images/Images/"  in file_urlmd5_localpath:
                print("出错的file_urlmd5_localpath:"+file_urlmd5_localpath)
                print("这种情况经常是因为，一个article被放入多个book里面,book注意清空")
                print(traceback.print_exc())
                return None
            
            if "Audios/Audios/"  in file_urlmd5_localpath:
                print("出错的file_urlmd5_localpath:"+file_urlmd5_localpath)
                print("这种情况经常是因为，一个article被放入多个book里面,book注意清空")
                print(traceback.print_exc())
                return None
            if "Videos/Videos/"  in file_urlmd5_localpath:
                print("这种情况经常是因为，一个article被放入多个book里面,book注意清空")
                print("出错的file_urlmd5_localpath:"+file_urlmd5_localpath)
                print(traceback.print_exc())
                return None
            
            
            if Wcc.existsFile('wikicivi-files',file_urlmd5_localpath) == True:
                print("existsUrlmd5File:"+file_urlmd5_localpath)
            else:
                if Wcc.downloadFile(file_urlmd5_localpath, file_url) == False:
                    print("dwloadFile:"+file_url+" Fail")
                    return None
                else:
                    filedatmd5 = md5_file(file_urlmd5_localpath)
                    if filedatmd5 == None:
                        print("getmd5File:"+file_urlmd5_localpath+" Fail")
                        return None
                    file_datmd5_localpath = file_datmd5_localpath.split("#datmd5#")[0]+filedatmd5+file_datmd5_localpath.split("#datmd5#")[2]
                    farray["src"] = file_datmd5_localpath
                    farray["md5"] = filedatmd5
                    print("md5map:"+file_urlmd5_localpath +" >> "+file_datmd5_localpath)
                    if Wcc.existsFile('wikicivi-files',file_urlmd5_localpath) == True:
                        print("hasurlFile:"+file_urlmd5_localpath)
                    elif Wcc.existsFile('wikicivi-files',file_datmd5_localpath) == True:
                        print("hasmd5File:"+file_datmd5_localpath)
                    else:
                        if Wcc.uploadFile(file_urlmd5_localpath, file_datmd5_localpath,'wikicivi-files') == False:
                            print("uploadFile:"+file_urlmd5_localpath+" Fail")
                            return None
                        else:
                            print("uploadFile:"+file_datmd5_localpath+" Ok from "+file_urlmd5_localpath)
            if mime_main == "image":
                do_get_image_info = False
                if file_ext == "":
                    do_get_image_info = True
                if "w" not in farray.keys():
                    do_get_image_info = True
                if "h" not in farray.keys():
                    do_get_image_info = True
                if "s" not in farray.keys():
                    farray["s"] = file_size
                if do_get_image_info == True:
                    success,image_width, image_height  = Wcc.get_image_info(file_url,file_urlmd5_localpath)
                    if success == False:
                        print("infoxImage:"+file_url)
                        return None
                    farray["w"] = image_width
                    farray["h"] = image_height
                    farray["s"] = file_size
            
            elif mime_main == "video":
                do_get_video_info = False
                if file_ext == "":
                    do_get_video_info = True
                if "w" not in farray.keys():
                    print("video must has width\n")
                    return None
                if "h" not in farray.keys():
                    print("video must has height\n")
                    return None
                if "s" not in farray.keys():
                    farray["s"] = file_size
            
                if "def" not in farray.keys():
                    vdef = "other"
                    if farray["h"] >= 240:
                        vdef = "240p"
                    if farray["h"] >= 360:
                        vdef = "360p"
                    if farray["h"] >= 480:
                        vdef = "480p"
                    if farray["h"] >= 720:
                        vdef = "720p"
                    if farray["h"] >= 1080:
                        vdef = "1080p"
                    farray["def"] = vdef
            
                if "lot" not in farray.keys():
                    do_get_video_info = True
                if do_get_video_info == True:
                    duration  = Wcc.get_avdio_duration(file_url,file_urlmd5_localpath)
                    if duration == 0:
                        print("infoxVideo:"+file_url)
                        return None
                    farray["lot"] = duration
                return farray
            
            elif mime_main == "audio":
                farray["s"] = file_size
                do_get_audio_info = False
                if "lot" not in farray.keys() or farray["lot"] == 0:
                    #这里要下载文件，然后在本地获得文件的duration\
                    #想法是:直接下载到本地目录，然后在真正下载的时候,判断一下是否在本地有了，如果有，直接上传
                    do_get_audio_info = True
            
                if do_get_audio_info == True:
                    audio_duration = Wcc.get_avdio_duration(file_url,file_urlmd5_localpath)    
                    if audio_duration == 0: 
                        print("infoxAudio:"+file_url)
                        return None
                    else:
                        farray["lot"]   = audio_duration
            else:
                print("不支持的格式:"+mime_main+" with file_type: "+mime_main)
                return None
        except Exception as err:
            print("---------")
            print(farray)
            print(bak_new)
            print(traceback.print_exc())
            print(traceback.format_exc())
            log.error(e)
            print("发生了例外"+str(err))
            return None
        return farray

    # 返回值
    # existed:1=存在 0=不存在
    # uid: >0:号  0=未知
    def MakeSetUserFollowMsg(uid_inc,user_info):
        try:
            user_info["by"] = "Crawler"
            if "uid" not in user_info :
                print("setuser_info中缺少uid")
                print(user_info)
                return{}
            if "followers" not in user_info :
                print("setuser_info中缺少followers")
                print(user_info)
                return{}
            if "followees" not in user_info :
                print("setuser_info中缺少followees")
                print(user_info)
                return{}
            follows = []
            follows.extend(user_info["followers"])
            follows.extend(user_info["followees"])
            for userf in follows:
                if "uidfrm" not in userf:
                    print("缺少uidfrm字段(follows)")
                    return {}
                if "name" not in userf:
                    print("缺少name字段(follows)")
                    return {}
                if "avatar" not in userf:
                    print("缺少avatar字段(follows)")
                    return {}

                set_user_msg = user_info
            return set_user_msg    
        except Exception as err:
            print(traceback.print_exc())
            print(err)
            return {}

    # 返回值
    # existed:1=存在 0=不存在
    # uid: >0:号  0=未知
    def MakeSetUserMsg(uid_inc,user_info):
        user_info["by"] = "Crawler"
        if "uid" not in user_info :
            print("setuser_info中缺少uid")
            print(user_info)
            return{}
        if "uidfrm" not in user_info :
            print("setuser_info中缺少uidfrm")
            print(user_info)
            return{}
        if "fields" not in user_info :
            print("setuser_info中缺少fields")
            print(user_info)
            return{}
        fields = user_info["fields"]

        if "name" not in fields:
            print("setuser_info中缺少name")
            print(user_info)
            return {}

        if "sex" in fields:
            if  fields["sex"] not in ["U","F","M"]:
                print("setuser_info中sex不合法")
                print(user_info)
                return {}

        if "bloc"  in fields :
            pass

        if "bday"  in fields :
            if fields['bday'] < 19170000 or fields['bday'] > 20110000:
                print("setuser_info中bday不合法")
                print(user_info)
                return {}

        if "bmonth"  in fields :
            fields['bmonth'] = int(fields['bmonth'])
            if fields['bmonth'] > 1231 or fields['bmonth'] < 0:
                print("setuser_info中bmonth不合法")
                print(user_info)
                return {}

        if "ctime"  in fields :
            if fields['ctime'] < 0:
                print("setuser_info中ctime不合法")
                print(user_info)
                return {}
 
        if "starc"  in fields :
            if fields['starc'] < 0:
                print("setuser_info中starc不应为0")
                print(user_info)
                return {}
   
        if "comtc"  in fields :
            if fields['comtc'] < 0:
                print("setuser_info中comtc不应为0")
                print(user_info)
                return {}

        if "artc"  in fields :
            if fields['artc'] < 0:
                print("setuser_info中artc不应为0")
                print(user_info)
                return {}
        if "exp"  in fields :
            if fields['exp'] < 0:
                print("setuser_info中exp不应为0")
                print(user_info)
                return {}

        if "isvip" in fields:
            if  fields["isvip"] not in [0,1]:
                print("setuser_info中isvip不合法")
                print(user_info)
                return {}

        if "followee" in fields:
            if  fields["followee"] <0:
                print("setuser_info中followee不应为0")
                return {}

        if "follower" in fields:
            if  fields["follower"] <0:
                print("setuser_info中follower不应为0")
                return {}

        if "level" in fields:
            if  fields["level"] <0:
                print("setuser_info中level不合法")
                print(user_info)
                return {}

        #有的网站如不得姐,可以同时拿到大头像,小头像,所以支持avatars选项 
        avatar_obj = {"urls":[]}
        print() 
        if "avatar" in fields  and fields['avatar'] != '':
            avatar_obj["urls"].append({"url":fields['avatar']})
        
        if "avatars" in fields:
            for url in fields['avatars']:
                avatar_obj["urls"].append({"url":url})
        if len(avatar_obj["urls"]) == 0:
            print("应该至少有一个头像url")
            print(fields)
            return {}       
        user_info["fields"]["avatar"] =json.dumps(avatar_obj,ensure_ascii=False,sort_keys=True)

        wallimage_obj = {"urls":[]}
        if "wallimage" in fields:
            wallimage_obj["urls"].append({"url":fields['wallimage']})
            if len(wallimage_obj["urls"]) == 0:
                print("应该至少有一个墙纸url")
                print(fields)
                return {}       
            user_info["fields"]["wallimage"] =json.dumps(wallimage_obj,ensure_ascii=False,sort_keys=True)

        try:
            set_user_msg = user_info
            return set_user_msg    
        except Exception as err:
            print(traceback.print_exc())
            print(err)
            return {}
    #类似于bdj:3894334456的写法
    #豆瓣里的明星是:dbn:cbt:***写法， cbt=celebrity
    #豆瓣里的用户是:dbn:***写法
    #内涵社的用户是:nhs:***写法
    #返回值
    # existed:1=存在 0=不存在
    #返回值
    # existed:1=存在 0=不存在
    # uid: >0:号  0=未知
    @staticmethod
    def MakeAddUserMsg(user_info):
        if "name" not in user_info :
            print("缺少用户名")
            print(user_info)
            return {}       
        #去掉用户名中的空格
        user_info["name"] = user_info["name"].replace(" ","")

        if "bloc" not in user_info :
            user_info['bloc'] = ''
        
        if "locs" not in user_info :
            user_info['locs'] = ''
        
        if "brief" not in user_info :
            user_info['brief'] = ''
        
        if "saying" not in user_info :
            user_info['saying'] = ''
        
        if "job" not in user_info :
            user_info['job'] = ''
        
        if "sex" not in user_info :
            user_info['sex'] = 'U'
        
        if "bday" not in user_info :
            user_info['bday'] = 19000000
        
        if "ustr" not in user_info :
            user_info['ustr'] = ''
        
        if "isfrom" in user_info :
            print("Error: isfrom is deprecated\n")
            print(user_info)
            return {}       


        if "follower" not in user_info:
            user_info["follower"] = 0

        if "followee" not in user_info:
            user_info["followee"] = 0

        if "ctime" not in user_info:
            user_info["ctime"] = 0
        
        if "utime" not in user_info:
            user_info["utime"] = 0

        if "artc" not in user_info:
            user_info["artc"] = 0


        #有的网站如不得姐,可以同时拿到大头像,小头像,所以支持avatars选项 
        avatar_obj = {"urls":[]}
        if "avatar" in user_info  and user_info['avatar'] != '':
            avatar_obj["urls"].append({"url":user_info['avatar']})
        
        if "avatars" in user_info:
            for url in user_info['avatars']:
                avatar_obj["urls"].append({"url":url})
        
        if len(avatar_obj["urls"]) == 0:
            print("应该至少有一个头像url")
            print(user_info)
            return {}       
        
        if user_info['ustr'] == '':
            print("Error: Bad ustr\n")
            print(user_info)

        try:
            pwd = "123456"
            add_user_msg = {
                "ustr"  : user_info["ustr"],
                "pwd"   : md5(pwd.encode(encoding='utf_8')).hexdigest(),
                "by"    : 'Crawler',
                "kind"  : 'C',
                "name"  : user_info["name"],
                "sex"   : user_info["sex"], #M,F,U
                "bday"  : user_info["bday"], #M,F,U
                "bloc"  : user_info["bloc"], #birthday localtion
                "locs"  : user_info["locs"],
                "brief" : user_info["brief"],
                "saying": user_info["saying"],
                "job"   : user_info["job"],
                "artc"  : user_info["artc"],
                "follower"   : user_info["follower"],
                "followee"   : user_info["followee"],
                "utime"   : user_info["utime"],
                "ctime"   : user_info["ctime"],
                "incode": 'null', #M,F,U
                "vfcode": 'FFFFFF', #M,F,U
                "avatar": json.dumps(avatar_obj,ensure_ascii=False,sort_keys=True),
            }
            return add_user_msg    
        except Exception as err:
            print(traceback.print_exc())
            print(err)
            return {}

    #参考https://github.com/devsnd/tinytag
    def tinytag_class2dict(tag_class):
        tag_dict = {}
        tag_dict['album']        =tag_class.album#albumasstring
        tag_dict['albumartist']  =tag_class.albumartist#albumartistasstring
        tag_dict['artist']       =tag_class.artist#artistnameasstring
        tag_dict['audio_offset'] =tag_class.audio_offset#numberofbytesbeforeaudiodatabegins
        tag_dict['bitrate']      =tag_class.bitrate#bitrateinkBits/s
        tag_dict['disc']         =tag_class.disc#discnumber
        tag_dict['disc_total']   =tag_class.disc_total#thetotalnumberofdiscs
        tag_dict['duration']     =tag_class.duration#durationofthesonginseconds
        tag_dict['filesize']     =tag_class.filesize#filesizeinbytes
        tag_dict['genre']        =tag_class.genre#genreasstring
        tag_dict['samplerate']   =tag_class.samplerate#samplespersecond
        tag_dict['title']        =tag_class.title#titleofthesong
        tag_dict['track']        =tag_class.track#tracknumberasstring
        tag_dict['track_total']  =tag_class.track_total#totalnumberoftracksasstring
        tag_dict['year']         =tag_class.year#yearordataasstringtag.album#albumasstring
        return tag_dict
    HEAD = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive'
    }


    #来自github TinyTag
    def get_avdio_duration(file_url,local_path):
        try:
            if os.path.exists(local_path):
                print("retrieFile:"+local_path)
            else:
                flag = Wcc.downloadFile(local_path, file_url)
                if flag == False:
                    return {}
                else:
                    pass
            okFlag = True
            duration = 0
            try:
                tinytag_class = TinyTag.get(local_path)
                duration = tinytag_class.duration
            except Exception as err:
                #print(err)
                print("TinyTag Fail to get info of "+local_path)
                okFlag = False
            if okFlag == False:
                try:
                    mp3_eyed3 = eyed3.load(local_path)
                    duration = mp3_eyed3.info.time_secs
                    okFlag = True
                except Exception as err:
                    #print(err)
                    print("Eyed3 Fail to get info of "+local_path)
            #if okFlag == False:
            #    try:
            #        mutagen_audio = MP3(local_path)
            #        print(mutagen_audio.items())
            #        for k, v in mutagen_audio.items():
            #            print(str(k)+":"+str(v))
            #        okFlag = True
            #    except Exception as err:
            #        print(err)
            #        print("mutagen Fail to get info of "+local_path)
            #获取音频长度的最后一道方案.github上的一个项目
            #https://github.com/philippbosch/mp3duration
            if okFlag == False:
                try:
                    response = requests.get("http://mp3duration.herokuapp.com/?url="+file_url)
                    response_json = response.json()
                    duration = response_json["seconds"]
                    okFlag = True
                except Exception as err:
                    #print(err)
                    print("herokuapp Fail get duration: "+local_path)
        
            print("audio/video:"+file_url+" lot:"+str(duration))
            if okFlag == True:
                return duration
            else:
                return 0
        
        except Exception as err:
            print(traceback.print_exc())
            print(err)
            return 0
        finally:
            pass
        return 0

    def get_image_info(file_url,local_path):
        ok_flag = False
        try:
            if os.path.exists(local_path):
                #print("retrieFile:"+local_path)
                pass
            else:
                flag = Wcc.downloadFile(local_path, file_url)
                if flag == False:
                    return False,0,0    
                else:
                    pass
            im = Image.open(local_path);
            width,height = im.size
            ok_flag = True
        except Exception as err:
            print(traceback.print_exc())
            print(err)
            width = 0
            height = 0
            ok_flag = False
        finally:
            pass
        
        return ok_flag,width, height

    def existsFile(oss_bucket,file_localname):
        #如果用bucket.get_object(key),目测会真实下载object,会带来很大出网流量
        #目前暂时使用False
        #return False
        access_key_id = Osskey.getKey()
        access_key_secret = Osskey.getSecret()
        bucket_name = oss_bucket
        endpoint    = 'http://oss-cn-qingdao.aliyuncs.com'
        #endpoint = os.getenv('OSS_TEST_ENDPOINT','http://oss-cn-qingdao-internal.aliyuncs.com')
        # 确认上面的参数都填写正确了
        for param in (access_key_id, access_key_secret, bucket_name, endpoint):
            assert '<' not in param, '请设置参数：' + param
        
        bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
        
        # 获取不存在的文件会抛出oss2.exceptions.NoSuchKey异常
        #"""如果文件存在就返回True，否则返回False。如果Bucket不存在，或是发生其他错误，则抛出异常。"""
        #https://github.com/aliyun/aliyun-oss-python-sdk/blob/master/oss2/api.py
        flag = False
        try:
            flag = bucket.object_exists(file_localname)
        except oss2.exceptions.NoSuchKey as e:
            print(e)
            return False
        except Exception as err:
            print(err)
            return False
        return flag

    def uploadFile(file_localname, file_cloudname,oss_bucket='wikicivi-files'):
        access_key_id = Osskey.getKey()
        access_key_secret = Osskey.getSecret()
        bucket_name = oss_bucket
        endpoint = 'http://oss-cn-qingdao.aliyuncs.com'
        #确认上面的参数都填写正确了
        for param in (access_key_id, access_key_secret, bucket_name, endpoint):
            assert '<' not in param, '请设置参数：' + param
        # 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
        bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
        # 把本地文件 “座右铭.txt” 上传到OSS，新的Object叫做 “我的座右铭.txt”
        # 注意到，这次put_object()的第二个参数是file object；而上次上传是一个字符串。
        # put_object()能够识别不同的参数类型
        success = True
        for k in range(1,6):
            try:
                bucket.put_object_from_file(file_cloudname, file_localname)
                success = True
                break
            except Exception as err:
                #print(err)
                success = False
                time.sleep(1.0)
                print("uploadFile:"+file_cloudname+" Fail "+str(k)+"/3")
                continue
        if success == True:
            print("uploadFile:"+file_cloudname+" Ok from "+file_localname)
        else:
            print("uploadFile:"+file_cloudname+" Abort")
        # # 上面两行代码，也可以用下面的一行代码来实现
        
        # bucket.put_object_from_file(file_localname, file_localname)
        return success
