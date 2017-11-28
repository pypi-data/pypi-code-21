def _(lines):
    ret = []
    switching = False
    for line in reversed(lines):
        if line[2] == '>':
            if not switching:
                switching = True
                line[2] = ';'
            else:
                line[2] = ''
        elif line[2] == ';' and switching:
            line[2] = ''
            switching = False
        ret.insert(0,line)
    return ret
