import copy
import re


def mtransform(message, transform):
    if not isinstance(message, dict):
        raise Exception('first argument, message, must be a dict type')
    if not isinstance(transform, dict):
        raise Exception('second argument, transform, must be a dict type')
    sub_transform = copy.deepcopy(transform)
    return _mtransform(message, sub_transform)


def _mtransform(message, transform):
    for t in transform:
        if isinstance(transform[t], dict) or isinstance(transform[t], list):
            if t not in message:
                message[t] = {}
            if isinstance(transform[t], dict):
                _mtransform(message[t], transform[t])
            elif isinstance(transform[t], list):
                message[t] = transform[t]
        else:
            if t in transform:
                if transform[t].startswith(' specials/'):
                    p = re.compile(' specials/(.*?)\$message->{(.*?)}(.*)')
                    m = p.match(transform[t])
                    out = m.group(1)
                    if isinstance(message[m.group(2)], dict):
                        second = message[m.group(2)]
                        third = m.group(3)
                        inner_p = re.compile('->{(.*)}(.*)')
                        inner_m = inner_p.match(third)
                        out = out + second[inner_m.group(1)] + inner_m.group(2)
                    else:
                        out = out + message[m.group(2)]
                    message[t] = out
                else:
                    message[t] = transform[t]
