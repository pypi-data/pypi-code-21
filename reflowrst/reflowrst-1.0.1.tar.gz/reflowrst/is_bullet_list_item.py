def is_bullet_list_item(lines, index):
    '''check if it's a bullet list item'''
    
    bullets = ['*', '-', '+', '•', '‣', '⁃']
    first_char = lines[index].lstrip().split(' ')[0]
    if first_char in bullets:
        return True
    return False
        
