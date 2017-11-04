from .tools import space_fill

def reflow_enumerated_list_item(text, space):
    '''
    reflow an enumerated list item
    '''
    leading_space = text.replace(text.lstrip(), '')
    lines = text.split('\n')
    enumerator = text.lstrip().split(' ')[0]
    initial = len(leading_space) + len(enumerator)
    rest_of_text = text[initial::]
    interspace = rest_of_text.replace(rest_of_text.lstrip(), '')
    words = [enumerator]
    words.extend(rest_of_text.lstrip().split(' '))
    growing_string = leading_space
    
    output_list = []
    while len(words) > 0:
        if len(growing_string) == len(leading_space):
            growing_string += words[0]
            words.pop(0)
        elif len(growing_string) == len(leading_space) + + len(enumerator):
            growing_string += interspace + words[0]
            words.pop(0)
        elif len(growing_string + ' ' + words[0]) <= space:
            growing_string += ' ' + words[0]
            words.pop(0)
        else:
            output_list.append(growing_string + '\n')
            growing_string = leading_space + space_fill(len(enumerator), ' ')
    output_list.append(growing_string + '\n')
    return ''.join(output_list).rstrip()

    return '\n'.join(lines)
