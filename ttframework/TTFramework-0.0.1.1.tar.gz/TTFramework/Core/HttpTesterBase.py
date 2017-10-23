import requests,re
from abc import abstractmethod
import copy
from .FuncHelper import FuncHelper

class Case(object):
    __requestData = None
    headers = None
    cookies = None
    method = None
    asserts = None
    params = None
    url = None
    body = None
    name = None
    error = None
    def __init__(self,data):
        self.error = None
        self.name = data.get('name', '')
        self.__requestData  = data
        self.__init()


    def __init(self):
        self.checkUrl()
        self.checkMethod()
        self.checkHeaders()
        self.params_all_dict = self.__requestData.pop('params')
        self.checkAssert()



    def checkUrl(self):
        try:
            pattern = "^((http)://)?\w+\.\w+\.\w+"
            self.url = self.__requestData['url']
            match = re.findall(pattern,self.url)
            if not match:
                raise Exception('url[' + self.url + ']不合法')
        except Exception as e:
            self.error = 'url:' + str(e)

    def checkMethod(self):
        try:
             self.method = self.__requestData.pop('method')
             self.method = self.method.upper()
             if self.method not in ['POST', 'GET', 'PUT', 'DELETE']:
                 raise Exception('方法不支持!')
        except Exception as e:
            self.error = 'method:' + str(e)

    def checkHeaders(self):
        try:
            self.headers = {
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding":"gzip, deflate, br",
                "Accept-Language":"zh-CN,zh;q=0.8",
                "Cache-Control":"max-age=0",
                "Connection":"keep-alive",
                "Upgrade-Insecure-Requests":"1",
                "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
                # "Content-Type":"text/html;charset=utf-8　application/octet-stream image/gif"
                "Content-Type":"application/json"
            }
            headers = self.__requestData.pop('headers')
            if headers:
                self.headers.update(headers)
        except Exception as e:
            self.error = 'header:' + str(e)


    def checkParams(self):
        if not self.params_all_dict:
            return
        try:
            params = self.params_all_dict
            for p in params:
                if p['type'] == 'url':
                    self.url = self.url.replace('{' + p['name'] + '}',p['value'])
                elif p['type'] == 'header':
                    self.headers[p['name']] = p['value']
                elif p['type'] == 'params':
                    if not self.params:
                        self.params = {}
                    self.params[p['name']] = p['value']
                elif p['type'] == 'body':
                    if not self.body:
                        self.body = {}
                    self.body[p['name']] = p['value']
                else:
                    if not self.params:
                        self.params = {}
                    self.params[p['name']] = p['value']
        except Exception as e:
            self.error = 'params:' + str(e)

    def checkAssert(self):
        try:
            self.asserts = self.__requestData.get('asserts',{})
        except Exception as e:
            self.error = 'assert:' + str(e)

class Result(object):
    requestHeaders = None
    requestBody = None
    responseHeaders = None
    responseBody = None
    globalValues = None
    status = None
    method = None
    url = None
    IsAssert = None
    assertFail = None
    error = None
    assertError = None

class HttpTester(object):
    __session = requests.session()
    __jobId = ""
    def processCase(self,case):
        result = Result()
        response = None
        try:
            result.url =  case.url
            result.method =  case.method
            result.requestBody = json.dumps(case.body,ensure_ascii=False)
            result.requestHeaders = json.dumps(case.headers,ensure_ascii=False)
            result.error = ''
            result.assertError = ''
            if case.error:
                result.error = case.error
                result.IsAssert = False
                return result, None, case
            response = self.__session.request(case.method,case.url, params=case.params, data=case.body, headers=case.headers,
                                               cookies=case.cookies,timeout=3)
            result.status = str(response.status_code)
            #
            dictHeaders = dict(response.request.headers)
            dictHeaders = copy.copy(dictHeaders)
            dictHeaders['params'] = case.params
            result.requestHeaders = json.dumps(dictHeaders,ensure_ascii=False)
            #
            dictHeaders = dict(response.headers)
            dictHeaders = copy.copy(dictHeaders)
            dictHeaders['responseMethod'] = response.request.method
            dictHeaders['responseUrl'] = response.url
            result.responseHeaders = json.dumps(dictHeaders,ensure_ascii=False)
            #
            result.responseBody = response.text
        except Exception as e:
            result.error = str(e)
            return result, response, case
        try:
            self.processAssert(result, response, case)
            return result, response, case
        except Exception as e:
            result.assertError = str(e)
            result.IsAssert = False
            return result, response, case

    def dictToInstance(self,data):
        if not isinstance(data,dict):
            return None
        result = type('myInstance',(),data)
        for key in data.keys():
            if isinstance(data[key],dict):
                setattr(result,key,self.dictToInstance(data[key]))
            elif isinstance(data[key],list):
                for i,d in enumerate(data[key]):
                    if isinstance(d,dict):
                        data[key][i] = self.dictToInstance(d)
        return result

    def processAssert(self, result, res, case):
        response = res
        request = res.request
        headers = self.dictToInstance(dict(res.headers))
        cookies_dict = requests.utils.dict_from_cookiejar(res.cookies)
        cookies = self.dictToInstance(cookies_dict)
        cookiesText = json.dumps(cookies_dict)
        bodyText = res.text
        try:
            body = self.dictToInstance(json.loads(res.text))
        except Exception as e:
            body = None
        if not case.asserts:
            result.IsAssert = True
            return
        for ast in case.asserts:
            try:
                result.IsAssert = eval(ast)
            except Exception as e:
                result.IsAssert = False
                result.assertError = '表达式[' + ast + ']计算错误,请核对原因:'  + str(e)
            if not result.IsAssert:
                result.assertFail = ast
                break

    @abstractmethod
    def start(self):
        pass


    def resultDataToDict(self,resultData):
        if resultData.IsAssert:
            assertStr = str(True)
        else:
            assertStr = str(False)
        data = {
            "isAssert":assertStr,
            "assertFail":resultData.assertFail,
            "url":resultData.url,
            "method": resultData.method,
            "status": resultData.status,
            "requestHeader": resultData.requestHeaders,
            "requestBody": resultData.requestBody,
            "responseHeader": resultData.responseHeaders,
            "responseBody": resultData.responseBody,
            "error":resultData.assertError
        }
        if hasattr(resultData,'fullGlobalValues'):
            data['globalValues'] = json.dumps(resultData.fullGlobalValues,ensure_ascii=False)
        if hasattr(resultData,'name') and (resultData.name != ''):
            data['name'] = resultData.name
        return data


class HttpSingletonTester(HttpTester):
    def __init__(self,sourceData):
        data = sourceData.pop('interface')
        self.__jobId = sourceData.pop('jobId')
        self.case = Case(data)


    def start(self):
        self.case.checkParams()
        result, response, case = self.processCase(self.case)
        dataDict = self.resultDataToDict(result)
        if (result.error != None) and (result.error != ''):
            resultDict = {
                "jobId": self.__jobId,
                "execStatus": "Error",
                "execContent": result.error,
                "data": dataDict
            }
        else:
            resultDict = {
                "jobId":self.__jobId,
                "execStatus":"Success",
                "execContent":"",
                "data":dataDict
            }
        return json.dumps(resultDict,ensure_ascii=False)







class HttpMutiTester(HttpTester):
    __cases = []
    __globalValues = {}
    def __init__(self,data):
        self.__jobId = data.pop('jobId')
        self.execType = data.pop('execType')
        interfaces = data.pop('interfaces')
        self.__cases = []
        for d in interfaces:
            globalValues = {}
            if 'globalValues' in d.keys():
                globalValues = d.get('globalValues',{})
            case = Case(d)
            self.__cases.append((case,globalValues))

    def start(self):
        fullGlobalValues = {}
        errorInterfaceName = ''
        errorInterfaceMsg =  ''
        resultDict = {
            "jobId": self.__jobId,
            "execStatus": "Success",
            "execContent": "",
            "data": []
        }
        for c in self.__cases:
            isBreak = False
            curCase = c[0]
            curGlobalValue = c[1]
            fullGlobalValuesToView = {}
            self.processSetParams(curCase, fullGlobalValues)
            curCase.checkParams()
            result, response, case = self.processCase(curCase)
            result.fullGlobalValues = json.dumps(fullGlobalValuesToView,ensure_ascii=False)
            result.name = curCase.name
            if (result.error != None) and (result.error != ''):
                errorInterfaceName = curCase.name
                errorInterfaceMsg = result.error
                if self.execType.lower() == 'ignore':
                    isBreak = False
                elif self.execType.lower() == 'failed':
                    isBreak = True
            if not (result.IsAssert):
                if self.execType.lower() == 'ignore':
                    isBreak = False
                elif self.execType.lower() == 'failed':
                    isBreak = True
            self.processGetFullGlobalValues(result, response, case,curGlobalValue,fullGlobalValues,fullGlobalValuesToView)
            dataDict = self.resultDataToDict(result)
            resultDict['data'].append(dataDict)
            if isBreak:
                break

        if errorInterfaceName != '':
            resultDict['execStatus'] = 'Error'
            resultDict['execContent'] = '接口[' + errorInterfaceName + '] 错误: ' + errorInterfaceMsg
        return json.dumps(resultDict,ensure_ascii=False)

    #设置全局变量到CASE的参数
    def processSetParams(self,case,fullGlobalValues):
        if not case.params_all_dict:
            return
        for p in case.params_all_dict:
            v = p['value']
            if v.startswith('$'):
                tmpValue = fullGlobalValues.get(v[1:],'NotFound')
                i = tmpValue.find('|')
                if i == -1:
                    p['value'] = tmpValue
                else:
                    p['value'] = tmpValue[:i]




                    # 设置返回的全局变量和参数
    def processGetFullGlobalValues(self, result, response, case,curGlobalValue,fullGlobalValues,fullGlobalValuesToView):
        if not response:
            return
        if not curGlobalValue:
            return
        response = response
        request = response.request
        headers = self.dictToInstance(dict(response.headers))
        cookies_dict = requests.utils.dict_from_cookiejar(response.cookies)
        cookies = self.dictToInstance(cookies_dict)
        cookiesText = json.dumps(cookies_dict)
        bodyText = response.text
        try:
            body = self.dictToInstance(json.loads(bodyText))
        except Exception as e:
            body = None
        #获取全局需要保存的变量
        for key in curGlobalValue.keys():
            v = curGlobalValue[key]
            try:
                if v.startswith('#'):
                    fullGlobalValues[key] = eval(v[1:])
                elif v.startswith('@'):
                    patten = 're.findall(\'{}\',bodyText)[0]'.format(v[1:])
                    evalValue = eval(patten)
                    fullGlobalValues[key] = evalValue.strip()
                else:
                    fullGlobalValues[key] = v
                fullGlobalValuesToView[key] = str(fullGlobalValues[key]) + '|' + v
            except Exception as e:
                fullGlobalValues[key] = v + ' expression error'
                fullGlobalValuesToView[key] = '表达式[' + v + ']计算错误' + str(e)
                result.assertError = '表达式[' + v + ']计算错误,请核对原因:' + str(e)


#=============================================================
import json,time

def getNowTimeToFileName(isall=False):
    result = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    if isall:
        return result
    else:
        return result[-3:]

def returnInterface():
    rootParams = {
        "jobId":getNowTimeToFileName(),
        "callBackUrl":"http://10.86.98.38:14000/unit/call-back",
        "interface":{
            "url": "http://www.igap.cn/gap/login",
            "method":"POST",
            "params":[
                {
                    "name":"loginName",
                    "type":"params",
                    "value":"13106112090"
                },
                {
                    "name": "password",
                    "type": "params",
                    "value": "a123456789"
                },
                {
                    "name": "loginType",
                    "type": "params",
                    "value": "1"
                }
            ],
            "header":{
                "Content-Type":"text/html;charset=utf-8;application/octet-stream image/gif",
                "Cookies":"JSESSIONID=ECFBA65B3D08B5D1BB67A1FD97E6AA75; Path=/gap/; HttpOnly"
            },
            "assert":['response.status_code == 200','"黄小刚" in response.text','"JSESSIONID" in cookiesText']
        }
    }
    return json.dumps(rootParams)

def returnInterfaceMuti():
    rootParams = {
        "jobId": getNowTimeToFileName(),
        "callBackUrl": "http://10.86.98.38:14000/unit/call-back",
        "execType": "ignore",  #failed   ignore
        "interfaces":[
            {
                "name": "001-登陆",
                "url": "http://www.igap.cn/gap/login1",
                "method": "POST",
                "params": [
                    {
                        "name": "loginName",
                        "type": "params",
                        "value": "13106112090"
                    },
                    {
                        "name": "password",
                        "type": "params",
                        "value": "a123456789"
                    },
                    {
                        "name": "loginType",
                        "type": "params",
                        "value": "1"
                    }
                ],
                "header": {
                    "Content-Type": "text/html;charset=utf-8;application/octet-stream image/gif",
                    "Cookies": "JSESSIONID=ECFBA65B3D08B5D1BB67A1FD97E6AA75; Path=/gap/; HttpOnly"
                },
                "assert": ['response.status_code == 200', '"黄小刚" in response.text', '"JSESSIONID" in cookiesText'],
                "globalValues":{
                    "gRealName":'@user-headimg">([\s\S]*?)</span>',
                    "gRedirect":"#response.url"
                }
            },
            {
                "name": "002-取职员编号",
                "url": "http://www.igap.cn/gap/auth/user/getallorgusers.htm",
                "method": "POST",
                "params": [
                    {
                        "name": "username",
                        "type": "params",
                        "value": "$gRealName"
                    }
                ],
                "header": {
                    "Content-Type": "text/html;charset=utf-8;application/octet-stream image/gif"
                },
                "assert": ['response.status_code == 200', '"操作成功" in bodyText', '"userlist" in response.text'],
                "globalValues": {
                    "gUserID": "@\"userID\":(.+?),\"userCode"
                }
            },
            {
                "name": "003-发任务",
                "url": "http://www.igap.cn/gap/pm/task/add.htm",
                "method": "POST",
                "params": [
                    {
                        "name": "groupType",
                        "type": "params",
                        "value": "1"
                    },
                    {
                        "name": "name",
                        "type": "params",
                        "value": "POST标题"
                    },
                    {
                        "name": "starttime",
                        "type": "params",
                        "value": "2017-08-03 08:42:00"
                    },
                    {
                        "name": "endtime",
                        "type": "params",
                        "value": "2017-08-14 08:42:00"
                    },
                    {
                        "name": "remark",
                        "type": "params",
                        "value": "这是一个备注说明__嘿嘿__哈哈哈__"
                    },
                    {
                        "name": "executorUserArr",
                        "type": "params",
                        "value": "$gUserID"
                    },
                    {
                        "name": "reportUserArr",
                        "type": "params",
                        "value": "$gUserID"
                    },
                    {
                        "name": "parentId",
                        "type": "params",
                        "value": ""
                    },
                    {
                        "name": "projectId",
                        "type": "params",
                        "value": ""
                    },
                    {
                        "name": "attachData",
                        "type": "params",
                        "value": "[]"
                    }
                ],
                "header": {
                    "Content-Type": "text/html;charset=utf-8;application/octet-stream image/gif"
                },
                "assert": ['response.status_code == 200', '"操作成功" in bodyText', '"createdon" in response.text'],
                "globalValues": {}
            }
        ]
    }
    return json.dumps(rootParams)
import time

if __name__ == '__main__':
    t = time.clock()
    #单接口
    # data = returnInterface()
    # data = json.loads(data)
    # httpTest = HttpSingletonTester(data)
    # result = httpTest.start()
    # print('singleton:',result)
    #多接口
    data = returnInterfaceMuti()
    data = json.loads(data)
    httpTestMuti = HttpMutiTester(data)
    result = httpTestMuti.start()
    print('muti:',result)

    #
    # ht = HttpTester()
    # data ={
    #     "url":"http://127.0.0.1/index",
    #     "type":"POST",
    #     "datas":[
    #         {
    #             "key1":"value1"
    #         },
    #         {
    #             "key2":{
    #                   "subKey":"subValue"
    #             }
    #         }
    #      ],
    #     "reports":{
    #         "file1": "file1Value",
    #         "file2": "file2Value",
    #         "size":{
    #             "file1Size":"2048kb"
    #         }
    #     }
    # }
    # d = ht.dictToInstance(data)
    # print(d.url)                               #http://127.0.0.1/index
    # print(d.reports.file1)                     #file1Value
    # print(d.reports.size.file1Size)            #2048kb
    # print(d.datas[0].key1)                     #value1
    # print(d.datas[1].key2.subKey)              #subValue
    #
    t = time.clock() - t
    print('used time:',t)

