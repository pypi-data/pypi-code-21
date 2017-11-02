def reflow_todo_list_item(text, space):
    '''
    reflow a todo list item
    '''
    if space == 0:
        return text
        
    leading_space = text.replace(text.lstrip(), '')
    line = text.lstrip()
    words = line.split(' ')
    growing_string = leading_space
    
    output_list = []
    while len(words) > 0:
        if len(growing_string) == len(leading_space):
            growing_string += words[0]
            words.pop(0)
        elif len(growing_string) == len(leading_space) + 3:
            growing_string += ' ' + words[0]
            words.pop(0)
        elif len(growing_string + ' ' + words[0]) <= space:
            growing_string += ' ' + words[0]
            words.pop(0)
        else:
            output_list.append(growing_string + '\n')
            growing_string = leading_space + '   '
    output_list.append(growing_string + '\n')
    return ''.join(output_list).rstrip()
