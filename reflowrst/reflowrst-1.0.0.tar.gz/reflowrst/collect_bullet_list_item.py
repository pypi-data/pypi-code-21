from .is_bullet_list_item import is_bullet_list_item
from .is_enumerated_list_item import is_enumerated_list_item
from .is_todo_list_item import is_todo_list_item

def collect_bullet_list_item(lines, index):
    '''Collect a bullet list item'''
    output = [lines[index]]
    leading_space = lines[index].replace(lines[index].lstrip(), '')
    index += 1
    
    while index < len(lines):
        if (
          lines[index].startswith(leading_space + ' ') and
          not lines[index] == '' and
          not is_bullet_list_item(lines, index) and
          not is_enumerated_list_item(lines, index) and
          not is_todo_list_item(lines, index)
        ):
            output.append(lines[index].lstrip())
            index += 1
        else:
            return ' '.join(output), index
    return ' '.join(output), index
