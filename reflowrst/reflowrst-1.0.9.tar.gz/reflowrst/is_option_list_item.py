def is_option_list_item(lines, index):
    if not lines[index].startswith('-') and not lines[index].startswith('/'):
        return False
    
    leading_space = lines[index].replace(lines[index].lstrip(), '')
    
    if not '  ' in lines[index]:
        if index < len(lines) - 1: 
            if lines[index + 1].startswith(leading_space + ' '):
                return True
            else:
                return False
        else:
            return False
            
        
    return True
