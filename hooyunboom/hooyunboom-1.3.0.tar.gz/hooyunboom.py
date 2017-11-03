"""
This is hooyunboom's first python module,it's great~
"""
def print_lol(the_list,indent=False,level=0,fh=sys.stdout):
    """This module reading everyone in a list"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1,fh)
        else:
            if indent:
                print("\t"*level,end='',file=fh)
            print(each_item,file=fh)