def print_lolo(lelo):
    '''trying to learn python '''
    for each_item in lelo:
        if isinstance(each_item,list):
            print_lolo(each_item)
        else:
            print(each_item)
