from .roman import fromRoman
import string

def get_enumerator_level(enumerator, enumerator_type):
    enumerator = enumerator[0:-1]
    
    if 'hashtag' in enumerator_type:
        return 0
    
    if 'full_parenthesis' in enumerator_type:
        enumerator = enumerator[1::]
    
    if 'arabic' in enumerator_type:
        return int(enumerator)
    
    elif 'alpha' in enumerator_type:
        return string.ascii_lowercase.index(enumerator.lower()) + 1
    
    else:
        return fromRoman(enumerator)
