#压平列表，函数名为flat()
#第一个参数为要压平的列表
#第二个参数为压平的层数（输入0不压平；输入负数全部压平，成一维列表）

"""
    English:


    module name : flat
    Function name :flat()
    Two parameters:
        1)the list
        2)flat level. 0 for no action. negative numbers for completely flating.
"""

def flat (thelist,num):
    if num==0:
        return thelist
    else:
        result=list()
        for each_item in thelist:
            if isinstance (each_item,list):
                result.extend(flat(each_item,num-1))
            else:
                result.append(each_item)
        return (result)
    
