'''
Copyright by Michał Olszak
Mysłowice, Poland, 30-10-2017
This is nested.py module, and it provides one function called print_lol()
which prints lists that may or may not include nested lists.
Version 1.2.0
'''


def print_lol(the_list, level=0):
    '''
    You have to pass the_list = list name to function.
    When it'll get to nested list each item will be printed in its own line.
    level -> checks wheter its nested item, and indent it.
    '''
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level+1)
        else:
            for tab_stop in range(level):
                print("\t", end="")
            print(each_item)
