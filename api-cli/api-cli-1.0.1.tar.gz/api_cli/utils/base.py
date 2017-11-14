#coding:utf-8
'''
* coder  : Dzlua
* email  : 505544956@qq.com
* module : api-cli
* path   : api_cli/utils
* file   : base.py
* time   : 2017/10/27
'''
#--------------------#
import os, codecs
#--------------------#

#--------------------#
def read_py(filename):
    ns = {}
    with open(filename) as f:
        code = compile(f.read(), filename, 'exec')
        eval(code, ns, ns)
    return ns
#----------#
def mkdirs(path):
    try:
        os.makedirs(path)
    except:
        pass
#----------#
def is_file(name):
    return os.path.isfile(name)
#----------#
def is_dir(name):
    return os.path.isdir(name)
#----------#
def is_exist(name):
    return os.path.exists(name)
#----------#
def module_dir():
    return os.getcwd()
#----------#
def dir_home():
    return os.environ['HOME']
#----------#
def dir_name(file):
    return os.path.dirname(file)
#----------#
def file_name(file):
    return os.path.basename(file)
#----------#
def file_ext(file):
    return os.path.splitext(file)
#----------#
def path_join(path, file):
    return os.path.join(path, file)
#----------#
def listdir(path):
    return os.listdir(path)
#----------#
def create_file(file, content=u''):
    if is_exist(file):
        return False
    path = dir_name(file)
    mkdirs(path)
    #
    fp = codecs.open(file, 'w', 'utf-8')
    fp.write(content)
    fp.close()

    return True
#----------#
def read_file(file):
    if not is_exist(file):
        return None
    fp = codecs.open(file, 'r', 'utf-8')
    content = fp.read()
    fp.close()
    return content
#----------#
def file_cp(src, dst):
    cont = read_file(src)
    if not cont:
        return False
    return create_file(dst, cont)
#----------#
def del_file(file):
    if is_exist(file):
        os.remove(file)
#----------#
def del_dir(path):
    for root,dirs,files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
#----------#
def dir_files(path, dirs=[], files=[]):
    fs = []
    #
    def has(ct, dts):
        for d in dts:
            if d == ct:
                return True
        return False
    #
    def _list(root, abs=''):
        for lists in os.listdir(root):
            path = os.path.join(root, lists)
            if os.path.isfile(path):
                if not has(lists, files):
                    fs.append(os.path.join(abs, lists))
            if os.path.isdir(path):
                if not has(lists, dirs):
                    _list(path, os.path.join(abs, lists))
    #
    _list(path)
    return fs
#--------------------#

#--------------------#
def unicode_to_utf8(text):
    return text.encode('utf-8')
#----------#
def array_unicode_to_utf8(data):
    info = []
    for v in data:
        utf8 = unicode_to_utf8(v)
        info.append(utf8)
    return info
#--------------------#

#--------------------#
def call(cmd):
    return os.system(cmd)
#--------------------#

#--------------------#
def get_returns():
    return ['\r\n', '\n', '\r']
#----------#
def is_return(s):
    fs = get_returns()
    for f in fs:
        if s == f:
            return True
    return False
#----------#
def find_return(s, index=0):
    fs = get_returns()
    for f in fs:
        ret = s.find(f, index)
        if ret is not -1:
            return [ret,f]
    return [-1,'']
#--------------------#
