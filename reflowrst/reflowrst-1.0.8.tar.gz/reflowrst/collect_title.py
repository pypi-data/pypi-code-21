def collect_title(lines, index):
    '''Collect title'''
    output = '\n'.join([lines[index], lines[index + 1]])
    return output, index + 2
