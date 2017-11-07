from tcell_agent.config import CONFIGURATION


def better_ip_address(request_env):
    if CONFIGURATION.reverse_proxy != True:
        return request_env.get('REMOTE_ADDR', '1.1.1.1')
    else:
        try:
            reverse_proxy_header = CONFIGURATION.reverse_proxy_ip_address_header
            if reverse_proxy_header is None:
                reverse_proxy_header = "HTTP_X_FORWARDED_FOR"
            else:
                reverse_proxy_header = "HTTP_" + reverse_proxy_header.upper().replace('-', '_')
            x_forwarded_for = request_env.get(reverse_proxy_header, request_env.get('REMOTE_ADDR', '1.1.1.1'))
            if x_forwarded_for and x_forwarded_for != '':
                ip = x_forwarded_for.split(',')[0].strip()
            else:
                ip = request_env.get('REMOTE_ADDR', '1.1.1.1')
            return ip
        except:
            return request_env.get('REMOTE_ADDR', '1.1.1.1')
