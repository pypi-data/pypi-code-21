def get_enumerator_type(enumerator):
    '''
    Define the type of enumerator
    
    An enumerator may be hashtag, arabic, alpha, or roman 
    upper or lower
    period, full_parenthesis, or right_parenthesis
    
    For example: "II)" is an  ["roman", "upper", "right_parenthesis"]
    '''
    
    output = []
    
    if enumerator.endswith('.'):
        output.append('period')
        enumerator = enumerator[0:-1]
    elif enumerator.startswith('('):
        output.append('full_parenthesis')
        enumerator = enumerator[1:-1]
    else:
        output.append('right_parenthesis')
        enumerator = enumerator[0:-1]
    
    try:
        int(enumerator)
        output.append('arabic')
    
    except ValueError:
        if enumerator == '#':
            output.append('hashtag')
        
        elif enumerator.lower() == 'i':
            output.append('roman')
            if enumerator.isupper():
                output.append('upper')
            else:
                output.append('lower')
        
        elif len(enumerator) == 1:
            output.append('alpha')
            if enumerator.isupper():
                output.append('upper')
            else:
                output.append('lower')
        
        else:
            output.append('roman')
            if enumerator.isupper():
                output.append('upper')
            else:
                output.append('lower')
    return output
