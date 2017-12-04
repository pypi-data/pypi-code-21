#-*- coding:utf-8 -*-
__version__='0.1'
from robot.api import logger
from selenium import webdriver
from time import sleep
import re
import datetime,time
import random
import json
import types
import os
import webbrowser



class OlymKeywords(object):

    def split_data(self,value,fh=" "):
        '''
        切分数据,返回数组,例如:
        str=3.14.15

        |split data|str|

        return ['3','14','15']
        '''
        if not fh:
            fh=" ";
        return value.split(fh)

    def re_search(self,str,Ls,Rs):
        '''
        通过正则查询结果

        str 被切的数据
        Ls  左边界
        Rs  右边界
        如有多个只取第一个
        Examples:

        | re search | abcd | a | d                                           | # 返回结果是bc

        '''
        m=re.search( Ls+'(.*?)'+Rs,str)
        if m is not None:
            return m.group(1)
            logger.debug('return'+m.group(1))
        else:
            logger.info(str)

    def re_search_all(self,str,Ls,Rs):
        '''
        通过正则查询结果

        str 被切的数据
        Ls  左边界
        Rs  右边界
        返回list
        Examples:

        | re search all | A111B  A222B | A | B                                          | # 返回结果是['111','222']

        '''

        pat=re.compile(Ls+'(.*?)'+Rs)
        m=re.findall(pat,str)
        if m is not None:
            return m
        else:
            logger.info('re_search_all >> None')


    def Get_Time_Modified(self,addnumber='0'):
        '''
        获得当前日期. 可以通过参数加减日期

        :param addnumber: 加减天数, 默认是今天

        :return: str

        '''
        d1 = datetime.date.today()
        d2=d1+datetime.timedelta(int(addnumber))
        return d2

    def Get_Timestamp(self):
        '''
        获得时间戳

        :return: str , 保证数字唯一
        如: 1464921407
        '''
        res=time.time()
        return str(int(res))

    def Random_Num(self,start=1,stop=10000,times=1):
        '''
        随机产生一个随机数

        :param start 随机数最小值 默认是1

        :param stop  随机数最大值 默认是10000

        :param times 倍数,用于凑整随机, 默认是1

        :return: str
        如:

        Random Num | start=1 | stop=10 | times=100  返回 100 ~ 1000 的随机 返回结果为 100 或 200 等
        '''
        num=random.randint(int(start),int(stop))
        num=num*times
        logger.debug('生成随机数:'+str(num))
        return num

    def Random_Choice(self,sequence):
        '''
        随机选择有序类型(如数组)中的某一个值

        :param sequence 有序类型.
        :return 根据你传的参数决定类型
        如:

        Random Choice | ['a','b','c']  返回 a,b,c中的随机一个

        Random Choice | hello    返回h,e,l,l,o 中的随机一个
        '''
        res=random.choice(sequence)
        return res

    def json_Dumps(self,obj):
        '''
        :param obj: 字典或者str类型dumps后会变成json格式. 注意其他类型的会报错
        :return: json
        '''
        if type(obj) is types.UnicodeType:
            obj=obj.encode('utf-8')
        logger.debug(type(obj))
        logger.debug(obj)
        if isinstance(obj,str):
            d=json.JSONDecoder().decode(obj)
            data=json.dumps(d)
        elif isinstance(obj,dict) or isinstance(obj,list):
            data=json.dumps(obj)

        else:
            logger.error("typeError: can't dumps "+str(type(obj)) +" . must <str> or <dict> ")

        return data

    def FormData_to_Dict(self,text):
        '''
        text格式参考 casenumber=&searoute=null&isExsitAdjunct=&currentDate=2016-02-05
        :param text: str
        :return:dict
        '''
        adict={}
        for a in text.split('&'):
            (key,value)= a.split('=')
            adict[key]=value
        return adict

    def Jsonstr_to_Dict(self,jsonStr):
        '''
        text格式参考json 如 {"a":1,"b":2,"3":"c","4":["k","k1"]}
        '''
        d=json.JSONDecoder().decode(jsonStr)
        return d
        
    def code_str(self,s,y):
        '''
        将enicode去掉U
        用逗号分割
        '''
        data=y.join(s)
        return data
        

    def dict_values(self,s):
        '''
        获取dictionary中的values值
        '''
        data=s.values()
        return data
        

    def steplog(self,msg):
        '''
        写入格式如:
        2015-12-14   XXXXX
        '''
        #print type(msg)
        #print msg
        #RF传入的是UnicodeType,先转成str
        if type(msg) is types.UnicodeType:
            msg=msg.encode('utf-8')
        path=os.getcwd()
        projectpath=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        logpath=projectpath+os.sep+"steplog"
        if not os.path.exists(logpath):
            logpath=os.mkdir(projectpath+os.sep+"steplog")
        print logpath
        try:
            with open(logpath+os.sep+time.strftime("%Y-%m-%d")+'log.txt','a') as logs:
                logs.write(time.strftime("%H:%M:%S") + "    "+msg+"\n")
        except Exception, e:
            raise e


    def Get_advancedConditionsString(self,str):
        '''
        str demo : 起运港=NINGBO,目的港=DUBAI

        目前支持: 起运港 目的港
        '''
    def clear_host(self):
        '''
        清空文本中的内容
        说明：
        第一个参数是文件名称，包括路径如：C:\Windows\System32\drivers\etc\HOSTS；第二个参数是打开的模式mode
        'r'：只读（缺省。如果文件不存在，则抛出错误）
        'w'：只写（如果文件不存在，则自动创建文件）
        'a'：附加到文件末尾
        'r+'：读写
        '''
        print os.path.isfile("C:\Windows\System32\drivers\etc\HOSTS")


        file1 = open("C:\Windows\System32\drivers\etc\HOSTS","r+")

        file1.truncate()

        file1.close()

    def clear_document(self,str):
        '''
        清空文本中的内容
        str:文件所在目录
        '''
        file1 = open (str,"r+")
        file1.truncate()
        file1.close()

    def write_host(self,str2):
        '''
        内容写入文本
        参数说明：
        str:文本所在路径
        str1:打开的模式mode,'r'：只读（缺省。如果文件不存在，则抛出错误）
        'w'：只写（如果文件不存在，则自动创建文件）
        'a'：附加到文件末尾
        'r+'：读写
        str2:写入的内容
        '''
        file ("C:\Windows\System32\drivers\etc\HOSTS","r+").writelines(str2)
        file1 = open ("C:\Windows\System32\drivers\etc\HOSTS","r+")
        file2 = file1.readlines()
        print file2

        file1.close()

    def write_document(self,str,str1):
        '''
        写入文件内容
        str:文件所在路径
        str1:写入的内容
        '''

        print os.path.isfile(str)
        file (str,"r+").writelines(str1)
        file1 = open(str,"r+")
        print file1.readlines()
        file1.close()

    def read_document(self,str):
        '''
        读取文本中的多行
        str:文件所在路径
        '''
        file1 = open (str,"r+")
        file2 = file1.readlines()
        return file2
        file1.close()

    def set_download_dir(self,dir1,dir2):
    	
    	
    	'''
    	指定谷歌浏览器下载路径，但是下载动作需要自己添加click

    	dir1:下载的路径

    	dir2:浏览器驱动所在的路径

    	url:下载的链接

    	location:定位附件位置

    	eg: 在某个链接下载zip文件
    	file_download   dir1 = "d:\\"   dir2 ='D:\\python\\chromedriver.exe'  url = 'http://sahitest.com/demo/saveAs.htm'  location = '//a[text()="testsaveas.zip"]'
    	
    	'''
    	
    	options = webdriver.ChromeOptions()
    	prefs = {'profile.default_content_settings.popups': 0,'download.default_directory': dir1}
    	options.add_experimental_option('prefs',prefs)
    	options.add_argument('--user-agent=iphone')
    	driver = webdriver.Chrome(executable_path=dir2, chrome_options=options)
    	sleep (10)
    	'''
    	driver.get(url1)
    	driver.switch_to.frame(0)
    	elem=driver.find_element_by_id('username')
    	elem.send_keys(username)
    	elem=driver.find_element_by_id('password')
    	elem.send_keys(password)
    	driver.find_element_by_id('btn-submit').click()
    	driver.switch_to_window(driver.window_handles[-1])
    	sleep(2)
    	js='window.open("http://saas.800jit.com/modelhome/services/getResource?filePath=.%2Fupload_public%2Fsites%2F6%2Forgs%2F39926%2Fusers%2F585627%2Ffiles%2Ftext_plain%2Fc5d3.1502180179724.txt")'
    	driver.execute_script(js)
    	
    	driver.find_element_by_xpath(location).click()
    	
    	driver.quit()
    	
    	driver.get(url)

    	
    	
		'''
    	
        
    def select_frame_by_index(self,locator,index):
        '''
        sets frame identified by 'locator' as current frame,
        if 'locator'is not unique,use index key attributes for frames are 'id' and 'name'
        Example:
        | select_frame_by_index | tag=iframe | 1|

        '''

        self._info("Selecting frame '%s'." % locator)
        if locator.startswith("tag"):
            elements = self._element_find(locator,False,True)
            if index < 0: 
                index = index + elements.length

            element = elements[int(index)]
        else:
            element = self._element_find(locator,True,True)
        self._current_browser().switch_to_frame(element)

    




    

if __name__ == '__main__':

	
    dir1 = "d:\\"
    
    dir2 ='D:\\python\\chromedriver.exe'
    
    test=OlymKeywords().file_download(dir1,dir2)
   
    
    print test
    
   

   
    
    