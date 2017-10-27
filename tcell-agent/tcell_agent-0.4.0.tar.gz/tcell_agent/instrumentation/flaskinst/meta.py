from future.utils import iteritems

from tcell_agent.appsensor.params import flatten_clean
from tcell_agent.appsensor.meta import AppSensorMeta, headers_from_environ
from tcell_agent.instrumentation.better_ip_address import better_ip_address
from tcell_agent.instrumentation.context import TCellInstrumentationContext
from tcell_agent.request_metrics.timing import start_timer


def create_meta(request):
    appsensor_meta = AppSensorMeta()
    request._appsensor_meta = appsensor_meta
    appsensor_meta.set_raw_remote_address(request._tcell_context.remote_addr)
    appsensor_meta.method = request.environ.get("REQUEST_METHOD")
    appsensor_meta.user_agent_str = request._tcell_context.user_agent
    appsensor_meta.location = request.url
    appsensor_meta.path = request.path
    appsensor_meta.route_id = request._tcell_context.route_id

    appsensor_meta.get_dict = request.args
    appsensor_meta.cookie_dict = request.cookies
    appsensor_meta.headers_dict = headers_from_environ(request.environ)
    try:
        appsensor_meta.json_body_str = request.get_json() or {}
    except:
        appsensor_meta.json_body_str = None
    appsensor_meta.request_content_bytes_len = request.content_length or 0

    appsensor_meta.post_dict = flatten_clean(request.charset, request.form)
    appsensor_meta.path_dict = request.view_args

    files_dict = {}
    for param_name, file_obj in iteritems(request.files or {}):
        files_dict[param_name] = file_obj.filename

    appsensor_meta.files_dict = flatten_clean(request.charset, files_dict)


def update_meta_with_response(appsensor_meta, response, response_code):
    appsensor_meta.response_code = response_code
    if response is not None:
        appsensor_meta.response_content_bytes_len = response.content_length or 0


def set_context_and_start_timer(request):
    from tcell_agent.instrumentation.flaskinst.routes import calculate_route_id

    request._tcell_context = TCellInstrumentationContext()

    if request.url_rule is not None:
        request._tcell_context.route_id = calculate_route_id(request.environ.get("REQUEST_METHOD"),
                                                             request.url_rule.rule)
    request._tcell_context.user_agent = request.environ.get("HTTP_USER_AGENT")
    raw_ip_address = better_ip_address(request.environ)
    request._tcell_context.set_remote_addr(raw_ip_address)
    request._tcell_context.method = request.environ.get("REQUEST_METHOD")

    start_timer(request)
