from .is_bullet_list_item import is_bullet_list_item
from .is_enumerated_list_item import is_enumerated_list_item
from .is_todo_list_item import is_todo_list_item

from .tools import make_enumerator
from .tools import space_fill

def collect_enumerated_list_item(lines, index, max_ewidth):
    '''Collect an enumerated list item'''
    output= []
    leading_space = lines[index].replace(lines[index].lstrip(), '')
    enumerator = lines[index].lstrip().split(' ')[0]
    initial = len(leading_space) + len(enumerator)
    rest_of_text = lines[index][initial::].lstrip()
    
    espace = space_fill(len(enumerator), ' ')
    interspace = space_fill(max_ewidth - len(enumerator), ' ')
    
    lines[index] = leading_space + enumerator + interspace + ' ' + rest_of_text
    output.append(lines[index])
    index += 1
    
    lspace = leading_space + espace + interspace
    while index < len(lines):
        if (lines[index].startswith(lspace) and
          not is_bullet_list_item(lines, index) and
          not is_enumerated_list_item(lines, index) and
          not is_todo_list_item(lines, index)
        ):
            output.append(lines[index].lstrip())
            index += 1
        else:
            return ' '.join(output), index
    
    return ' '.join(output), index
