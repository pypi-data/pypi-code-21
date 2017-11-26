'''
Created on 2017年11月15日

@author: Johnson
'''
#coding=utf-8 
#-*-coding:utf-8-*-

#movies = ["战狼1",2016,"战狼2",2017,["吴京",["吴刚","卢靖姗","余男","丁海峰","张翰","石兆琪"]]]

"""这是一个'06DefPrintList01.py'模块，提供了一个名为print_listinlist()的函数，作用是打印列表的数据项，其中可能包含（也可能不包含）嵌套列表"""
def print_nesterlist(the_list):         #定义函数
    '''这个函数取一个位置参数，名为"the_list",它可以是任何Python列表（也可是包含嵌套列表的列表）。所指定的列表中的每个数据项会（递归地）打印输出，各数据项各占一行。'''
    for each_item in the_list:          #用一个“for”循环处理所提供的列表
        if isinstance(each_item, list): #判断列表数据项是否为列表
            print_nesterlist(each_item) #如果是，调用本函数
        else:                           #否则
            print(each_item)            #在屏幕上打印显示这个列表项
            
#print_nesterlist(movies)                #调用函数
