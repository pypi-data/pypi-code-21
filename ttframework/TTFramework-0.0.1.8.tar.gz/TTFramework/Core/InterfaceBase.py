import os

from .DatetimePlus import *
from .FuncHelper import FuncHelper
from japronto.response.cresponse import Response

from enum import Enum

class APIResponse(Enum):
    NOT_INITIALIZED = "not-initialized"
    SUCCESS = "success"
    FAIL = "fail"
    UNAUTHORIZED_SERVICE_INVOKER = "unauthorized-invoker"
    VALIDATION_FAIL = "validation-fail"
    BAD_PARAMETER = "bad-parameter"
    UNAUTHORIZED = "unauthorized"
    USER_NOT_LOGIN = "user-not-login"
    RPC_FAIL = "rpc-fail"

class APIResponseMessage(Enum):
    SUCCESS = 'API调用成功'
    FAIL = 'API调用失败'
    UNAUTHORIZED_SERVICE_INVOKER = '拒绝访问,未授权的服务调用者'
    VALIDATION_FAIL = '请求参数验证失败'
    BAD_PARAMETER = '拒绝访问,请求参数错误'
    UNAUTHORIZED = '拒绝访问,您没有权限请求该资源'
    NOT_INITIALIZED = '返回值未初始化'
    USER_NOT_LOGIN = '用户未登陆'
    RPC_FAIL = '远程调用失败【{0}】'

class APIResponseHTTPCode(Enum):
    SUCCESS = 200
    FAIL = 400
    UNAUTHORIZED_SERVICE_INVOKER = 401
    VALIDATION_FAIL = 400
    BAD_PARAMETER = 400
    UNAUTHORIZED = 401
    NOT_INITIALIZED = 400
    USER_NOT_LOGIN = 401
    RPC_FAIL = 400


class InterfaceBase(object):
    def __get_message_and_httpstatus_by_code(self,code):
        key = ''
        for _v in APIResponse:
            if _v.value == code:
                key = _v.name
                break
        message = ''
        for _v in APIResponseMessage:
            if _v.name == key:
                message = _v.value
                break
        http_status = 200
        for _v in APIResponseHTTPCode:
            if _v.name == key:
                http_status = _v.value
                break
        return http_status,message


    def _create_response(self,code,data=None,message=None):
        http_status,_message = self.__get_message_and_httpstatus_by_code(code.value)
        result = {}
        result['code'] = code.value
        if message:
            if code == APIResponse.RPC_FAIL:
                result['message'] = message.format(message)
            else:
                result['message'] = message
        else:
            result['message'] = _message
        if data:
            result['data'] = data
        _v = Response(code=http_status, text=FuncHelper.dict_to_json(result), mime_type='application/json')
        return _v

    def _getFilePath(self):
        result = self.DataPath + DatetimePlus.get_nowdate_to_str() + '/'
        if not os.path.exists(result):
            os.makedirs(result)
        result = result + DatetimePlus.get_now_datetime_to_filename() + '_'
        return result

    def _decode_to_str(self,s):
        try:
            result = s.decode(encoding="utf-8")
        except:
            result = None
        return result

    def _redirect(self,module_name,path):
        if module_name == '':
            return Response(code=302, text='Not Found', headers={"Location":path})
        return Response(code=302, text='Not Found' ,headers={"Location":'/' + module_name + '/' + path})

    def _upload_files(self,request):
        '''
        客户端发送多个文件的方法
        返回文件列表 子类中直接传过来request 其他非文件参数请使用parameters or json
        files = [('file', open(u'0511490425.jpg', 'rb')),
                 ('file', open(u'b03533fa828ba61ef.jpg', 'rb')),
                 ('file',open(u'312435636g0.jpg','rb')),
                 ('file',open(u'9495454.txt','rb'))
        ]
        r = requests.post(url, files=files)
        '''
        body = request.body
        fileNameList = []
        i = body.find(b'filename=')
        while i != -1:
            i += 10
            j = body.find(b'"',i)
            name = body[i:j].decode(encoding="utf-8")

            i = j + 5
            j = body.find(b'\r\n--', i)
            value = body[i: j]

            fileName = self._getFilePath() + name
            fileNameList.append(fileName)
            with open(fileName, 'wb') as f:
                f.write(value)

            i = body.find(b'filename=',j)
        return fileNameList

    def _upload_file_stream(self,request):
        '''
        客户端发送流的方法
        返回文件名 子类中直接传过来request 其他非文件参数请使用parameters or json
        fileName = '0511490425.jpg'
        with open(fileName, 'rb') as f:
             r = requests.post(url, data=f,params={"fileName":fileName})
        '''
        try:
            fileName = request.query['fileName']
            fileName = self._getFilePath() + fileName
            with open(fileName,'wb') as f:
                f.write(request.body)
        except Exception as e:
            fileName = ''
            print(e)
        return fileName



