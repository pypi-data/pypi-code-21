def print_lol(the_list, level):
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level+1)
        else:
            for num in range(level):
                print('\t', end='')
            print(each_item)

movies = ['abc', 'def', 'ghj',
            ['klm', 'nop', 'qrst',
                        ['uvw', 'syz']]]

print_lol(movies, 0)
