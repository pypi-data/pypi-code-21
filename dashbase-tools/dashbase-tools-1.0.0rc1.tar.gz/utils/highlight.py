from colorama import init
from termcolor import colored

init()


def highlight_str(s, indices_list):
    if not s or not indices_list:
        return s
    temps = None
    i = 0
    for indices in indices_list:
        if 'offset' not in indices or 'length' not in indices:
            return s
        start = indices["offset"]
        length = indices["length"]
        if length > 0:
            temps = temps + s[i:start] if temps else s[i:start]
            end = start + length
            part = s[start:end]
            temps += colored(part, 'green', 'on_red')
            i = end
    if i < len(s):
        temps += s[i:]
    return temps
