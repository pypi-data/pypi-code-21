"""这是“nester.py”模块，提供了一个名为print_lol()的函数用来打印列表，其中包含或不包含嵌套列表。"""

import sys


def print_lol(the_list, indent=False, level=0, fh=sys.stdout):
    """第一个参数，名为“the_list”，这可以是任何Python列表（包含或不包含嵌套列表），所提供列表中的各个数据项会（递归地）打印到屏幕上，而且各占一行。
    第二个参数，名为“indent”，用来决定是否缩进，默认不使用。
    第三个参数，名为“level”，用来决定遇到嵌套列表时插入制表符的个数，默认插入0个。
    第四个参数，名为“fh”，用来决定输出文件流，默认为stdout"""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level + 1, fh)
        else:
            if indent == True:
                for tab_stop in range(level):
                    print("\t", end="", file=fh)
            print(each_item, file=fh)
