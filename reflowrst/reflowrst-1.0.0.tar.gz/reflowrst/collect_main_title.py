def collect_main_title(lines, index):
    '''Collect a main title'''
    output = '\n'.join([lines[index], lines[index + 1], lines[index + 2]])
    return output, index + 3
