def f(jobs):
    ret = []
    for j in jobs:
        if 'settings' in j:
            setting = j['settings']
            if 'max_retries' in setting and setting['max_retries'] != 0:
                ret.append(j)

    return ret

def f(jobs):
    ret = []
    for j in jobs:
        if 'settings' in j:
            setting = j['settings']
            if 'max_retries' in setting and setting['max_retries'] != 2:
                ret.append(j)

    return ret

def f(jobs):
    ret = []
    for j in jobs:
        if 'settings' in j:
            setting = j['settings']
            if 'min_retry_interval_millis' in setting and setting['min_retry_interval_millis'] < 30 * 1000:
                ret.append(j)

    return ret
