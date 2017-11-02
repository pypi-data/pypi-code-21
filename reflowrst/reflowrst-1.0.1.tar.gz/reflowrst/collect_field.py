from .is_field import is_field

def collect_field(lines, index, interspace):
    output = []
    
    words = lines[index].strip().split(' ')
    for x in range(len(words)):
        if words[x].endswith(':') and not words[x].endswith('\\:'):
            field_name = ' '.join(words[0:x + 1])
            words = words[x + 1::]
            break
    
    leading_space = lines[index].replace(lines[index].lstrip(), '')
    first_line = leading_space + field_name + interspace + ' '.join(words)
    output.append(first_line)
    
    index += 1
    while index < len(lines):
        if (not is_field(lines, index) and
            not lines[index] == ''
        ):
            output.append(lines[index].lstrip())
        else:
            return ' '.join(output), index
    
    return '\n'.join(output), index
