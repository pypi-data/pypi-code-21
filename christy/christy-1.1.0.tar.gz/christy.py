"""The christy.py module is to print nested list from the whole list"""
def print_all(the_list,space):
    """Each data is printed to the screen on its own line""" 
    for each_item in the_list:
        if isinstance(each_item, list):
            print_all(each_item, space+1)
        else:
            for tab_stop in range(space):
                print("\t", end='')
            print(each_item)

            
