from .is_field import is_field
from .tools import get_field_name

def collect_field(lines, index, interspace):
    output = []
    words = lines[index].strip().split(' ')
    
    field_name, words = get_field_name(words)

    leading_space = lines[index].replace(lines[index].lstrip(), '')
    first_line = leading_space + field_name + interspace + ' '.join(words).lstrip()
    output.append(first_line.rstrip())
    
    index += 1

    while index < len(lines):
        if (not is_field(lines, index) and
            not lines[index] == ''
        ):
            output.append(lines[index].lstrip())
            index += 1
        else:

            return ' '.join(output), index
    return ' '.join(output), index
