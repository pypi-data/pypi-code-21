def is_todo_list_item(lines, i):
    if (
      lines[i].lstrip().startswith('[ ] ') or 
      lines[i].lstrip().startswith('[x] ')
    ):
        return True
    else:
        return False
