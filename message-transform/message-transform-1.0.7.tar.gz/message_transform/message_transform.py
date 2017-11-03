import copy
import re
import six


def mtransform(message, transform):
    args = {}
    if not isinstance(message, dict):
        raise Exception('first argument, message, must be a dict type')
    if not isinstance(transform, dict):
        raise Exception('second argument, transform, must be a dict type')
    if '.transform_control' in transform:
        args = transform['.transform_control']
        del transform['.transform_control']
    sub_transform = copy.deepcopy(transform)
    return _mtransform(message, sub_transform, message, args)


def _mtransform(message, transform, orig_message, args):
    new_transform = {}
    for k in transform:
        if isinstance(k, six.string_types) and k.startswith(' specials/'):
            new_k = _special(k, orig_message, args)
            new_transform[new_k] = copy.deepcopy(transform[k])
        else:
            new_transform[k] = copy.deepcopy(transform[k])

    for t in new_transform:
        if isinstance(new_transform[t], dict) or \
                isinstance(new_transform[t], list):
            if isinstance(new_transform[t], dict):
                if t not in message:
                    message[t] = {}
                _mtransform(message[t], new_transform[t], orig_message, args)
            elif isinstance(new_transform[t], list):
                if t not in message:
                    message[t] = []
                ct = 0
                for sub_t in new_transform[t]:
                    if isinstance(sub_t, dict) or isinstance(sub_t, list):
                        ret = {}
                        _mtransform(ret, sub_t, orig_message, args)
                        message[t].append(ret)
                    else:
                        message[t].append(sub_t)
                    ct = ct + 1
        else:
            if t in new_transform:
                if isinstance(new_transform[t], six.string_types) and \
                        new_transform[t].startswith(' specials/'):
                    if 'no_specials' in args:
                        if 'no_over_write' in args:
                            if t not in message:
                                message[t] = new_transform[t]
                        else:
                            message[t] = new_transform[t]
                    else:
                        if 'no_over_write' in args:
                            if t not in message:
                                message[t] = _special(new_transform[t],
                                                      orig_message, args)
                        else:
                            message[t] = _special(new_transform[t],
                                                  orig_message, args)
                else:
                    if 'no_over_write' in args:
                        if t not in message:
                            message[t] = new_transform[t]
                    else:
                        message[t] = new_transform[t]


def _special(working_part, message, args):
    try:
        working_part = working_part[10:]
        return(_sub(working_part, message))
    except Exception as err:
        print('Exception: ' + str(err) + '\n')
        return(None)


def _sub(working_part, message):
    m = copy.deepcopy(message)
    main_pattern = re.compile('^(.*?)\$message->{([.A-Za-z0-9_-]*?)}(.*)')
    main_matches = main_pattern.match(working_part)
    if main_matches is None:  # no more substitution
        return(working_part)
    # else some kind of substitution
    head = main_matches.group(1)
    key = main_matches.group(2)
    tail = main_matches.group(3)
    if tail.startswith('{'):  # sub-substitution
        if key not in m:
            return(_sub(head + '$message->' + tail, m))
        m = m[key]
        return(_sub(head + '$message->' + tail, m))
    # else finish the substitution
    if key not in m:
        return(_sub(head + tail, m))
    return(_sub(head + m[key] + tail, m))
