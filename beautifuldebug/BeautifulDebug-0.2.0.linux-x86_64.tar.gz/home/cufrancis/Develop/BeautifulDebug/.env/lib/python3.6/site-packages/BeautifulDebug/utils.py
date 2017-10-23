from .settings import Setting
import time
import traceback
import sys
from colorama import Fore, Back, Style, init
import types
import inspect
from .defines import ATTR_MAP, ATTR_EXCEPTION_MAP
import pprint
import parser
import cProfile
import pstats
import tracemalloc


init(autoreset=True)

class Dump(object):
    def __init__(self, setting={}):
        self.setting = setting
        self.content = None

    def run(self, obj, *args, **kw):
        self.obj = obj
        self.setting.update(**kw)
        # 分隔符
        self.separator()

        stack = traceback.format_stack()
        stack.pop(-1)
        for line in stack:
            print(Style.DIM + '>> '+line.strip())

        type_ = type(obj)
        print(Fore.YELLOW + 'type:')
        print(Fore.CYAN + '\t{}'.format(type_))

        print(Fore.YELLOW + 'Address: ')
        print(Fore.CYAN + '\t{}'.format(id(self.obj)))

        if obj is None:
            self.dump_None()
        elif inspect.isclass(obj):
            self.dump_class()
        if isinstance(obj, str):
            self.dump_str(*args, **kw)
        elif isinstance(obj, dict):
            self.dump_dict(*args, **kw)
        elif isinstance(obj, list):
            self.dump_list(*args, **kw)
        elif isinstance(obj, types.ModuleType):
            self.dump_module(*args, **kw)
        elif isinstance(obj, types.FunctionType):
            self.dump_function(*args, **kw)

        if self.content is not None and self.setting.content is True:
            print(Fore.YELLOW + 'content:')
            print(self.content)

        # 是否显示对象方法
        if self.setting.show_function is True:
            print("Function")
            self.show_function()

    def dump_function(self, *args, **kw):
        '''调试 函数'''
        pass

    def separator(self):
        '''显示分隔符'''
        if self.setting.separator is not None:
            print(Style.DIM + self.setting.separator)

    def call_stack(self):
        '''显示调用栈'''
        index = 1
        stack = tuple(reversed((inspect.stack())))
        # print(stack)
        update = []
        for i, s in enumerate(stack):
            tmp = inspect.getframeinfo(s[0])
            update.append({
                'filename': tmp[0],
                'lineno': tmp[1],
                'function': tmp[2],
                'code_context': tmp[3],
            })
        update = update[:-3]
        for index, stack in enumerate(update):
            print(Fore.YELLOW + "\t{}: filename = {}, lineno = {}, function = {}"
                    .format(index, stack['filename'], stack['lineno'], stack['function']))
            for code in stack['code_context']:
                print(Style.DIM + "\t\t{}".format(code))

    def dump_class(self, *args, **kw):
        '''
        dump class
        1. doc
        2.
        '''
        print(Fore.YELLOW+"Description:")
        doc = self.obj.__doc__.split('\n')
        doc = "\t" + "\n\t".join(doc)
        print(Style.DIM + doc)

        # function = []
        # for name in self.obj.__dict__:
        #     # 获取 attr 的文档
        #     if name not in ATTR_MAP:
        #         doc = inspect.getdoc(getattr(self.obj, name)).split('\n', 1)[0]
        #         function.append({
        #             'name': name,
        #             'doc': doc
        #         })
        # # 显示数据
        # print(Fore.YELLOW + "Function:")
        # for func in function:
        #     print(Fore.CYAN + "\t{} : \t".format(func['name']), end="")
        #     print(Style.DIM + "{}".format(func['doc']))

    def show_function(self):
        '''显示对象函列表'''

        profile = cProfile.run(self.obj)
        print(pstats.Stats(profile).print_callees(self.obj))
        function = []
        for name_tup in inspect.getmembers(self.obj):
            name, text = name_tup
                # 获取 attr 的文档
            if name not in ATTR_MAP:
                doc = inspect.getdoc(getattr(self.obj, name)).split('\n', 1)[0]
                function.append({
                    'name': name,
                    'doc': doc
                })

        # 显示数据
        print(Fore.YELLOW + "Function:")
        for func in function:
            print(Fore.CYAN + "\t{} : \t".format(func['name']), end="")
            print(Style.DIM + "{}".format(func['doc']))

    def check(self):
        '''检查 obj 类型'''
        pass

    def dump_list(self, *args, **kw):
        '''调试列表'''
        self.content = Fore.CYAN + '\t{}'.format(self.obj)

    def dump_None(self):
        print("None")
        pass

    def dump_object(self):
        ''' 对象类型'''
        pass

    def dump_dict(self, *args, **kw):
        '''调试字典'''
        content = Fore.CYAN + '\t{\n'
        for key, value in self.obj.items():
            content += Fore.CYAN + "\t   '{}'".format(key)
            content += Fore.CYAN + " : "
            format_ = "'{}'"
            if isinstance(value, int):
                format_ = "{}"
            content += Fore.CYAN + format_.format(value) + '\n'

        content += Fore.CYAN + '\t}'

        self.content = content

    def dump_module(self,*args, **kw):
        ''' 模块'''
        print(dir(self.obj))

    def dump_str(self, *args, **kw):
        ''' 字符串 '''
        self.content = Fore.CYAN + '\t{}'.format(self.obj)

    def check_attribute(self):
        '''显示对象的方法'''
        # arithmetic = {}
        # function = {}
        for key in self.obj.__dict__.keys():
            # print(getattr(obj, key).__doc__)
            doc = getattr(obj, key).__doc__
            print(Fore.CYAN + key+ ':\t', end='')
            if doc is not None:
                print(Style.DIM + doc)

    def show_arthmetic(self, data, separator = '\t{}:\t', detail = True):
        '''显示操作符'''
        for key, value in data.items():
            print(separator.format(Fore.CYAN + key), end='')
            if detail is True:
                print(Style.DIM + str(value))

    arithmetic = [
        '__add__',
        '__mod__',
        '__mul__',
        '__rmod__',
        '__rmul__'
    ]

# Copied from http://stackoverflow.com/a/3681323/2142577.
def get_dict_attr(obj, attr):
    for obj in [obj] + list(obj.__class__.__mro__):
        if attr in obj.__dict__:
            return obj.__dict__[attr]
    raise AttributeError


def is_descriptor(obj):
    return (hasattr(obj, "__get__") or
            hasattr(obj, "__set__") or
            hasattr(obj, "__delete__"))
