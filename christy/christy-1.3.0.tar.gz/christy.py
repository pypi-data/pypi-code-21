"""The christy.py module is to print nested list from the whole list"""
def print_all(the_list,indent=False,space=0):
    """Each data is printed to the screen on its own line""" 
    for each_item in the_list:
        if isinstance(each_item, list):
            print_all(each_item,indent, space+1)
        else:
            if indent:
                for tab_stop in range(space):
                    print("\t", end='')
            print(each_item)

            
