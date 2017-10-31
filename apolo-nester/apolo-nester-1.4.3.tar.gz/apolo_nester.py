'''this is nester.py module, give a function named print_lol(), it is used to print element of a list'''
import sys

def print_lol(the_list,indent=False,level=0,file_object=sys.stdout):

    '''file_object determines standard output target, which is screen by default
    '''

    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item,indent,level+1,file_object)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end='',file=file_object)
            print(each_item,file=file_object)
