def is_directive(lines, index):
    '''check if the line contains a directive'''
    if lines[index].startswith('.. ') and '::' in lines[index]:
        return True
    
    #Handle hyperlinks here
    if lines[index].startswith('.. _'):
        return True
    
    return False
