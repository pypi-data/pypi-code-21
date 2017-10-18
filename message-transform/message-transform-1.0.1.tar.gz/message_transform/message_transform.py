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
                    p = re.compile(' specials/\$message->{(.*)}')
                    m = p.match(transform[t])
                    message[t] = message[m.group(1)]
                else:
                    message[t] = transform[t]
