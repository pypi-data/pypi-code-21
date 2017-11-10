#_*_coding:utf-8_*_

def print_lol(the_list,level):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,level+1)
        else:
            for num in range(level):
                print('\t',end='')
            print(each_item)

