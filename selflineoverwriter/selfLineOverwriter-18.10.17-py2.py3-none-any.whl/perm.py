def perm(line, text):
    open(__file__, 'r').readlines()[line] = text
    open(__file__, 'w').writelines(open(__file__, 'r').readlines()).close()
