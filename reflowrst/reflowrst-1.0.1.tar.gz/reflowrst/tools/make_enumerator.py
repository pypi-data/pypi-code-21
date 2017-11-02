import string
from .roman import toRoman

def make_enumerator(enumerator_type, enumerator_level):
    '''Make an enumerator given the type and level'''
    enumerator = ''
    
    if 'hashtag' in enumerator_type:
        enumerator = '#'
    
    elif 'arabic' in enumerator_type:
        enumerator = str(enumerator_level)
    
    elif 'alpha' in enumerator_type:
        enumerator = string.ascii_lowercase[enumerator_level - 1]
    
    elif 'roman' in enumerator_type:
        enumerator = toRoman(enumerator_level)
    
    if 'upper' in enumerator_type:
        enumerator = enumerator.upper()
    
    elif 'lower' in enumerator_type:
        enumerator = enumerator.lower()
    
    if 'period' in enumerator_type:
        enumerator = enumerator + '.'
    
    elif 'full_parenthesis' in enumerator_type:
        enumerator = '(' + enumerator + ')'
    
    elif 'right_parenthesis' in enumerator_type:
        enumerator = enumerator + ')'
    
    return enumerator



