import importlib
import webob
import aalam_common as zc
from aalam_common.config import cfg
from aalam_common import wsgi


class SystemHandlers(wsgi.Middleware):
    def __init__(self, app):
        self._url_prefix = "/%s/%s/_/" % (
            cfg.CONF.app_provider_code, cfg.CONF.app_code)
        super(SystemHandlers, self).__init__(app)

    def _cleanup(self, request):
        wsgi.cleanup()

    def _migrate_completed(self, request):
        if zc.CALLBACK_MIGRATE_COMPLETED in wsgi.app_callbacks:
            wsgi.app_callbacks[zc.CALLBACK_MIGRATE_COMPLETED]()

    def _invoke_method(self, request):
        method_name = request.params.get("method", None)
        if not method_name:
            return

        params = request.json
        (module_name, meth_name) = method_name.split(":")
        module = importlib.import_module(module_name)
        method = getattr(module, meth_name)
        ret = method(params['code'], params['value'])
        return ret

    def pre(self, request):
        if request.path.startswith(self._url_prefix):
            response = webob.Response()
            response.status_code = 200
            action = request.path.split(self._url_prefix, 1)[1]
            if action == "cleanup":
                self._cleanup(request)
            elif action == "migrate_completed":
                self._migrate_completed(request)
            elif action == "invoke_method":
                ret = self._invoke_method(request)
                if isinstance(ret, str) or isinstance(ret, unicode):
                    response.body = ret
                    response.content_type = "plain/text"
            return response
