def other_colon_present(words):
    for word in words:
        if word.endswith(':') and not word.endswith('\\:'):
            return True
    return False

def is_field(lines, index):
    words = lines[index].lstrip().split(' ')

    if not words[0].endswith(':'):
        if not words[0].startswith(':'):
            return False
        
        if not other_colon_present(words):
            return False
    
    return True
    
    '''
    leading_space = lines[index].replace(lines[index].lstrip(), '')
    
    if index > 0 and not lines[index - 1] == '':
        former_leading_space = lines[index - 1].replace(
            lines[index - 1].lstrip(), '')
            
        if not is_field(lines, index - 1):
            if len(leading_space) <= len(former_leading_space):
                return False
            else:
                return True
        else:
            return True
    else:
        return True
    '''
