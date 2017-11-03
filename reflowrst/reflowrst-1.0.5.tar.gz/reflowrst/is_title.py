from .tools.is_only import is_only

def is_title(lines, index):
    '''check to see if the line is a title'''
    if index > len(lines) - 2:
        return False
    if len(lines[index + 1]) == 0:
        return False
    symbol = lines[index + 1][0]
    
    if is_only(lines[index + 1], [symbol]):
        if len(lines[index]) <= len(lines[index + 1]):
            return True
    
    return False
