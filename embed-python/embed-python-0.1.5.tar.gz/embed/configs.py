domain_request_method = {
    'fiverr.com': 'request_normal',
}


def get_request_method(domain, default=None):
    return domain_request_method[domain] if domain in domain_request_method else default
