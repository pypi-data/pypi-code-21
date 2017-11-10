# -*- coding: utf-8 -*-
import inspect
import importlib


class GTool(object):
    """
    工具类
    """
    @classmethod
    def extract_class_func(cls, module, classes=None, exclude_func=()):
        """
        将一个文件中的类里面的函数提取出来，返回一个字典，每个class对应提取的func数组
        :param module: 文件路径
        :param classes: 提取的类
        :param exclude_func: 过滤掉的函数tuple
        :return:
        {
            'GBase': [],
        }
        """
        if not module:
            print u'模块为空'
            return

        result = {}
        file_module = importlib.import_module(module)
        for name, obj in inspect.getmembers(file_module):
            if not inspect.isclass(obj) or (classes and name not in classes):
                continue

            sub_attr = []
            for attr in dir(obj):
                if attr in exclude_func or attr.startswith('_'):
                    continue

                sub_attr.append(attr)
            result[name] = sub_attr

        return result

    @classmethod
    def generate_markdown_table(cls, class_2_func):
        if not class_2_func:
            return ''

        content = ''
        for class_name, funcs in class_2_func.items():
            content += '## ' + class_name + '\n\n'
            content += '|        方法        |        解释        |\n| ------------- | ------------- |\n'
            for func in funcs:
                content += '|    ' + func + '    |        |\n'

            content += '\n\n'

        return content


tool = GTool()

if __name__ == '__main__':
    class_2_func_content = tool.extract_class_func(module='GRedis')
    last_content = tool.generate_markdown_table(class_2_func_content)
