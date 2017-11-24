"""这是"nester.py"模块，提供了一个名为print_lol()的函数，
    这个函数的作用是打印列表，其中有可能包含（也可能不包含）
    嵌套列表。"""
import sys
def print_lol(the_list, indent=False, level=0,fn=sys.stdout) :
    """这个函数取一个位置参数，名为"the_list"，这可以是任何python列表（也可以
    是包含嵌套列表的列表）。所指定的列表中的每个数据项会（递归地）输出到屏幕上，
    各数据项各占一行。第二个参数level用来在遇到嵌套列表时插入制表符。"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item, indent, level+1, fn)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t", end="", file=fn)
            print(each_item, file=fn)
