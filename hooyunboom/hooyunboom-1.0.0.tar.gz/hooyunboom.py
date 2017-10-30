"""
This is hooyunboom's first python module,it's great~
"""
def print_lol(the_list):
    """This module reading everyone in a list"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print(each_item)