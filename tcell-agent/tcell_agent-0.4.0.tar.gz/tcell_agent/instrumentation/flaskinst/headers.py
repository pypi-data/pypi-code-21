from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.instrumentation.better_ip_address import better_ip_address


def set_csp_headers(request, response, transaction_id):
    if TCellAgent.get_policy(PolicyTypes.CSP):
        meta = request._appsensor_meta
        csp_headers = TCellAgent.get_policy(PolicyTypes.CSP).headers(
            transaction_id,
            meta.route_id,
            meta.session_id,
            meta.user_id,
            request.path)
        if csp_headers:
            for csp_header in csp_headers:
                response.headers[csp_header[0]] = csp_header[1]


def add_clickjacking(request, response, transaction_id):
    if TCellAgent.get_policy(PolicyTypes.CLICKJACKING):
        meta = request._appsensor_meta
        clickjacking_headers = TCellAgent.get_policy(PolicyTypes.CLICKJACKING).headers(
            transaction_id,
            meta.route_id,
            meta.session_id,
            meta.user_id,
            request.path)
        if clickjacking_headers:
            for clickjacking_header in clickjacking_headers:
                header_name = clickjacking_header[0]
                header_value = clickjacking_header[1]
                if response.headers.get(header_name, None):
                    response.headers[header_name] = response.headers[header_name] + ", " + header_value
                else:
                    response.headers[header_name] = header_value


def add_secure_headers(response):
    if TCellAgent.get_policy(PolicyTypes.SECURE_HEADERS):
        secure_headers = TCellAgent.get_policy(PolicyTypes.SECURE_HEADERS).headers()
        if secure_headers:
            for secure_header in secure_headers:
                response.headers[secure_header[0]] = secure_header[1]


def check_location_redirect(request, response):
    redirect_policy = TCellAgent.get_policy(PolicyTypes.HTTP_REDIRECT)

    if redirect_policy and response.location:
        meta = request._appsensor_meta
        response.headers['location'] = redirect_policy.process_location(
            better_ip_address(request.environ),
            request.environ.get("REQUEST_METHOD", None),
            request.host,
            request.path,
            response.status_code,
            response.location,
            user_id=meta.user_id,
            session_id=meta.session_id,
            route_id=meta.route_id)
