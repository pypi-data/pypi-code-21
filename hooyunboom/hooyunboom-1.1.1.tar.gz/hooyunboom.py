"""
This is hooyunboom's first python module,it's great~
"""
def print_lol(the_list,level=0):
    """This module reading everyone in a list"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end='')
            print(each_item)