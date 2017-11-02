def reflow_paragraph(text, space, leading_space=''):
    '''
    Reflow a flattened paragraph so it fits inside horizontal 
    space
    '''
    words = text.split(' ')
    growing_string = leading_space
    output_list = []
    
    while len(words) > 0:
        if growing_string == leading_space:
            growing_string += words[0]
            words.pop(0)
        elif len(growing_string + ' ' + words[0]) <= space:
            growing_string += ' ' + words[0]
            words.pop(0)
        else:
            output_list.append(growing_string + '\n')
            growing_string = leading_space
    output_list.append(growing_string)
    return ''.join(output_list)
