"""The christy.py module is to nested list from the whole list"""
def print_all(the_list):
    for each_item in the_list:
        if isinstance(each_item, list):
            print_all(each_item)
        else:
            print(each_item)

            
