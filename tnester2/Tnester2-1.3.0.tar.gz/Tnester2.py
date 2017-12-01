#这是一个名为print_lol()的模块，包含一个位置参数‘the_list'，可以用来打印列表（可能包含嵌套列表的各数据项）；第二个参数level是用来控制嵌套列表前的制表符个数。
def print_lol(the_list,indent=False,level=0):
#函数是用来将列表各数据项在屏幕（递归地）显示出来，每个数据项各占一行。
 for each_item in the_list:
  if isinstance(each_item,list):
   print_lol(each_item,indent,level+1)
  else:
     if indent:
          for tab_stop in range(level):
               print("\t",end='')
     print(each_item)
     
  
