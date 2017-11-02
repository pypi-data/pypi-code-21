from .tools import is_only

def is_gridtable(lines, i):
    if (
        lines[i].lstrip().startswith('+-') and 
        lines[i].rstrip().endswith('-+') and 
        is_only(lines[i].strip(), ['+', '-', ' '])
       ):
        return True
    return False
