def perm(line, text, filer):
    lines = open(filer, 'r').readlines()
    lines[line] = text
    out = open(filer, 'w')
    out.writelines(lines)
    out.close()