'''this is a function that can deal a list.it can print a list into a document,
tab it in different line.
'''

import sys
def print_lol(the_list,indent=False,level=0,fn=sys.stdout):

    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1,fn)
        else:
            if indent:
                for tab_stop in range(level+1):
                    print("\t",end='',file=fn)
                print(each_item,file=fn)
