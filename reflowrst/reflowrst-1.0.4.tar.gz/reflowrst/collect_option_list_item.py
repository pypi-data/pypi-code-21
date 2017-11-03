from .is_option_list_item import is_option_list_item

def collect_option_list_item(lines, index, interspace):
    output = []
    leading_space = lines[index].replace(lines[index].lstrip(), '')
    
    option = lines[index].lstrip().split('  ')[0]
    rest_of_text = lines[index].lstrip()[len(option)::]
    
    output.append(leading_space + option + interspace + rest_of_text)
    index += 1
    
    while index < len(lines):
        if (not is_option_list_item(lines, index) and
            not lines[index] == ''
        ):
            output.append(lines[index].lstrip())
        else:
            return ' '.join(output), index
    
    return '\n'.join(output), index
    
    
