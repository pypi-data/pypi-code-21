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
            
        else:
            return True
    
    leading_space = lines[index].replace(lines[index].lstrip(), '')
    
    if (index < len(lines) - 1 and 
        not is_field(lines, index + 1) and 
        not lines[index + 1].startswith(leading_space + ' ') and 
        not lines[index + 1] == ''):
        return False
    
    return True
