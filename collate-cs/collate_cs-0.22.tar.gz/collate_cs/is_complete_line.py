def _(line):
    string = ''.join(line).strip()
    if string[0:4] == 'for ':
        return False
    if string[0:2] == 'if':
        return False
    if 'public class' in string:
        return False
    if 'private' in string and ')' in string:
        return False
    if 'void' in string and ')' in string:
        return False
    if 'public' in string and ')' in string:
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
