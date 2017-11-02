def _(lines):
    ret = []
    for line in lines:
        string = ''
        for i in range(line[0]):
            string += '    '
        if line[2] == '-':
            line[2] = ''
        string += ''.join(line[1]) + line[2]
        ret.append(string)
    return ret
