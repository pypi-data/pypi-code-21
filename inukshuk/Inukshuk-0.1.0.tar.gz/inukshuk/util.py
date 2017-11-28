
def is_inukshuk_template(txt):
    index = txt.find('{')
    while index >= 0:
        ch = txt[index + 1]
        if ch == '{' or ch == '%':
            return True
        index = txt.find('{', index + 1)
    return False
