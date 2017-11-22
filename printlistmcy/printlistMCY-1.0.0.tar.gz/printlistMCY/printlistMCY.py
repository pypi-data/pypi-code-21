'''
测试函数，输出嵌套或者不包含嵌套的列表
'''
def print_list(the_list,indent = False, level = 0):
    for each in the_list:
        if isinstance(each,list):
            print_list(each,indent,level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print('\t',end='')
            print(each)
