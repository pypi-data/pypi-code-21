
import json
import os

class FuncHelper(object):
    #字典转JSON
    @staticmethod
    def dict_to_json(dValue, ensure_ascii=False):
        return json.dumps(dValue,ensure_ascii=False)

    #JSON转字典
    @staticmethod
    def json_to_dict(jValue):
        return json.loads(jValue)
    
    #创建目录树
    @staticmethod
    def create_dirs(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    #从URL返回文件名
    @staticmethod
    def get_file_name_by_url(url=''):
        i = url.rfind('/') + 1
        return url[i:]

    #获取扩展名
    @staticmethod
    def get_file_extname(s=''):
        i = s.rfind('.') + 1
        return s[i:]

    #返回程序根目录
    @staticmethod
    def get_curr_path():
        return os.getcwd()

    #字典转实例 用于向JS中访问JSON那样用.方法
    @staticmethod
    def dict_to_instance(data):
        if not isinstance(data,dict):
            return None
        result = type('myInstance',(),data)
        for key in data.keys():
            if isinstance(data[key],dict):
                setattr(result, key, FuncHelper.dict_to_instance(data[key]))
            elif isinstance(data[key],list):
                for i,d in enumerate(data[key]):
                    if isinstance(d,dict):
                        data[key][i] = FuncHelper.dict_to_instance(d)
        return result

    # JSON转实例 用于向JS中访问JSON那样用.方法
    @staticmethod
    def json_to_instance(jsonValue):
        jsonDict = FuncHelper.json_to_dict(jsonValue)
        return FuncHelper.dict_to_instance(jsonDict)
    
    # 检查文件是否存在
    @staticmethod
    def checkFileExists(filePath=''):
        return os.path.exists(filePath)

    # 检查文件夹是否存在
    @staticmethod
    def checkDirectoryExists(dirPath=''):
        return os.path.isdir(dirPath)

    @staticmethod
    def bytes_str_decode_str(s):
        try:
            result = s.decode(encoding="utf-8")
        except:
            result = ''
        return result

    # 检查文件夹是否存在
    @staticmethod
    def get_file_path_by_full_path(full_path=''):
        return full_path[:full_path.rfind('/')] #不包括/

    # 生产一个随机字符串
    @staticmethod
    def get_random_str(size = 10):
        s = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        _count = len(s)
        import random
        result = ''
        for i in range(size):
            result =  result + str(s[random.randint(0,_count)-1])
        return result

    @staticmethod
    def get_module_name_by_path(path=''):
        module_name = path[1:]
        module_name = module_name[:module_name.find('/')]
        return module_name


if __name__ == '__main__':
    # print( FuncHelper.getFileNameByUrl('http://www.evun.cc/adfklsdfjsdf/sdf/123456789.zip'))
    # print(FuncHelper.getCurrPath())
    pass


