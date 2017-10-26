'''This is a test function'''
def print_lol(the_list):
    '''This function print list'''
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print(each_item)
            
