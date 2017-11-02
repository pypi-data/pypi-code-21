def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def is_footnote(lines, index):
    if not lines[index].lstrip().startswith('.. ['):
        return False
    
    footnote_symbols = ['*', '†', '‡', '§', '¶', '#', '♠', '♥', '♦', '♣']
    if (not lines[index].lstrip()[4] in footnote_symbols and
        not is_int(lines[index].lstrip()[4])
    ):
        return False
    
    return True
