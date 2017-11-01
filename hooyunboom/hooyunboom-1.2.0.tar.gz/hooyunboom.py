"""
This is hooyunboom's first python module,it's great~
"""
def print_lol(the_list,indent=False,level=0):
    """This module reading everyone in a list"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1)
        else:
            if indent:
                print("\t"*level,end='')
            print(each_item)