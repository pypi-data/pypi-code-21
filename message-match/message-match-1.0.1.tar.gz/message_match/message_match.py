import re


def mmatch(message, match):
    if not isinstance(message, dict):
        raise Exception('first argument, message, must be a dict type')
    if not isinstance(match, dict):
        raise Exception('second argument, match, must be a dict type')
    return _mmatch(message, match)


def _mmatch(message, match):
    if isinstance(message, dict) and isinstance(match, dict):
        for key in match:
            if key not in message:
                return False
            sub_message = message[key]
            sub_match = match[key]
            if not _mmatch(sub_message, sub_match):
                return False
        return True
    if isinstance(message, list) and isinstance(match, list):
        # print("do list/list check")
        good_match = True
        for index, a_item in enumerate(message):
            b_item = match[index]
            if not _mmatch(a_item, b_item):
                good_match = False
        return good_match

    if isinstance(message, list) and isinstance(
       match, (int, float, complex, str)):
        found = False
        for item in message:
            if _mmatch(item, match):
                found = True
        return found

    # first check to see if it starts with ' special' and handle that
    if isinstance(match, str):
        if match.startswith(' special/'):
            p = re.compile(' special/(.*)/')
            m = p.match(match)
            inner_re_str = '.*' + m.group(1) + '.*'
            if match.endswith('i'):
                inner_re = re.compile(inner_re_str, re.IGNORECASE)
            else:
                inner_re = re.compile(inner_re_str)
            inner_match = inner_re.match(message)
            if inner_match is not None:
                return True
            return False
    # the default: just return equality check
    return(message == match)
