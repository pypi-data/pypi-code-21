def _(line):
    string = ''.join(line)
    stripped = string.strip()
    if "class" in stripped:
        return False
    if stripped == '':
        return False
    if stripped[0] == '[':
        return False
    if stripped[0] == '(':
        return False
    if stripped[0:2] == '//':
        return False
    if stripped[-1] == ',':
        return False
    if string[-1] == ' ':
        return False
    # filter for more open than closed brackets
    return True
