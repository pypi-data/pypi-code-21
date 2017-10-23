import os

from .DatetimePlus import *


class InterfaceBase(object):
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

    def _redirect(self,request,module_name,path):
        if module_name == '':
            return request.Response(code=302, text='Not Found', headers={"Location":path})
        return request.Response(code=302, text='Not Found' ,headers={"Location":'/' + module_name + '/' + path})

    def _uploadFiles(self,request):
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

    def _uploadFileStream(self,request):
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



