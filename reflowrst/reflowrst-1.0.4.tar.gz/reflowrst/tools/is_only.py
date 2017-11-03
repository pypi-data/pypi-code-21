def is_only(text, char_list):
    '''
    return true if the text is made up of only the characters in char 
    list
    '''
    text = text.strip()
    if text == '':
        return False
    for i in range(len(text)):
        if text[i] not in char_list:
            return False
    return True
