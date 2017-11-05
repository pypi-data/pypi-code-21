def print_lol(the_list,indent = False,level = 0):
        """这个函数有一个位置参数，名为“the_list”，
        这可以是任何Python列表（包含或不包含嵌套列表），
        所提供列表中的各个数据会（递归地）打印到屏幕上，而且各占一行。
        第二个参数（名为“level”）用来在遇到嵌套列表时插入制表符。"""
        for each_item in the_list:
                if isinstance(each_item,list):
                        print_lol(each_item,indent,level + 1)
                else:
                    if indent:
                        for tab_stop in range(level):
                                print("\t",end='')
                    print(each_item)
