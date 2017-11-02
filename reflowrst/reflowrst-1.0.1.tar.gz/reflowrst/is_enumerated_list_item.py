from .tools import fromRoman

def is_enumerated_list_item(lines, index):
    '''Check if it's an enumerated list item'''
    if len(lines[index].lstrip()) == 0:
        return False
    
    enumerator = lines[index].lstrip().split(' ')[0]
    if not enumerator.endswith('.') and not enumerator.endswith(')'):
        return False
    
    enumerator = enumerator[0:-1]
    if enumerator.startswith('('):
        enumerator = enumerator[1::]
        
    try:
        int(enumerator)
        return True
    except:
        try:
            fromRoman(enumerator)
            return True
        except:
            if len(enumerator) == 1 and enumerator.isalpha():
                return True
            else:
                return False
