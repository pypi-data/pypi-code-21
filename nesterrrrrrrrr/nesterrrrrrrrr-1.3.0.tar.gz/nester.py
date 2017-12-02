def print_lol(the_list, level=0):
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level+1)
        else:
            for num in range(level):
                print('\t', end='')
            print(each_item)

movies = ['The Holy Grail', 1975, 'Terry Jones & Terry Gilliam', 91,
    ['Graham Chapman', ['Michael Palin', 'John Cleese',
        'Terry Gilliam', 'Eric Idle', 'Terry Jones']]]

print_lol(movies)
