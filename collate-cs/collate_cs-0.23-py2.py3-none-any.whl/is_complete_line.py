def _(line):
    string = ''.join(line).strip()
    if "class" in string:
        return False
    if string == '':
        return False
    if string[0] == '[':
        return False
    if string[0] == '(':
        return False
    if string[0:2] == '//':
        return False
    if string == 'get':
        return False
    # filter for more open than closed brackets
    return True
