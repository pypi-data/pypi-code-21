def is_option_list_item(lines, index):
    if not lines[index].startswith('-') and not lines[index].startswith('/'):
        return False
    
    if not '  ' in lines[index]:
        return False
        
    return True
