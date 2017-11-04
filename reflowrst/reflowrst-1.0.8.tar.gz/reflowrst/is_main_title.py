from .tools import is_only

def is_main_title(lines, index):
    '''
    Determine if the lines follow the format of a main title
    '''
    if index > len(lines) - 3:
        return False
    if len(lines[index]) == 0:
        return False

    symbol = lines[index][0]
    if is_only(lines[index], [symbol]):
        if is_only(lines[index + 2], [symbol]):
            if len(lines[index]) >= len(lines[index + 1]):
                if len(lines[index + 2]) >= len(lines[index + 1]):
                    return True
    return False
