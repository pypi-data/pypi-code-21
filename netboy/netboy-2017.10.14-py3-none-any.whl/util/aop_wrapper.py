from loader.function import load


def pre_process(payload):
    pre_func = payload.get('pre_func')
    if pre_func:
        pre_func = load(pre_func)
        pre_ret = pre_func(payload)
        if pre_ret:
            payload = pre_ret
    return payload


def post_process(payload, response):
    post_func = payload.get('post_func')
    if post_func:
        post_func = load(post_func)
        post_ret = post_func(payload, response)
        if post_ret:
            response = post_ret
    response['keep'] = payload.get('keep', {})
    return response
