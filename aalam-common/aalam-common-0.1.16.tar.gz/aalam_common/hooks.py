import importlib
import json
import re
import os
import webob
import yaml
from aalam_common import wsgi
from aalam_common.config import cfg
from aalam_common import utils as zutils


HTTP_NO_ACTION_NEEDED = 204


class Hooks(wsgi.Middleware):
    def __init__(self, app):
        self._hooks_map = dict()
        self._hooked_map = dict()
        self._restrict_map = dict()
        self._hooked_regex = None
        self._restrict_regex = None
        self._regex = None
        self._load_map()
        super(Hooks, self).__init__(app)

    def _load_map(self):
        if not getattr(cfg.CONF, "hooks_map", None) or \
                not os.path.exists(cfg.CONF.hooks_map):
            return

        with open(cfg.CONF.hooks_map, "r") as f:
            y = yaml.load(f)
            hooked = y["hook"]
            for hook in hooked:
                self._hooked_map[self._frame_url_key(hook)] = hook.copy()

            try:
                restrict = y['restrict']
                for r in restrict:
                    self._restrict_map[self._frame_url_key(r)] = {
                        "type": r['type'] if 'type' in r else 'BA',
                        "except": r['except'] if 'except' in r else []
                    }
            except KeyError:
                pass

        self._hooked_regex = re.compile(
            "(" + '$)|('.join(self._hooked_map.keys()) + "$)")
        if self._restrict_map:
            self._restrict_regex = re.compile(
                "(" + "$)|(".join(self._restrict_map.keys()) + "$)")

    def _regexify_url(self, url):
        return url.replace("*", "[^\/]*?")

    def _frame_url_key(self, dictionary):
        return " ".join([dictionary['method'].upper(),
                         self._regexify_url(dictionary['url'])])

    def add_hooks(self, request):
        try:
            hooks = request.json
        except:
            raise webob.exc.HTTPBadRequest(
                explanation="Input content not proper")
        for h in hooks:
            url_key = self._frame_url_key(h)
            final_type = ""
            for t in list(h['type']):
                if self._is_restricted(h['url'], h['method'],
                                       t, h['hooker']):
                    # This url is restricted
                    continue
                else:
                    final_type += t

            if not final_type:
                continue
            else:
                h['type'] = final_type

            if url_key in self._hooks_map:
                self._hooks_map[url_key].append(h.copy())
            else:
                self._hooks_map[url_key] = [h.copy()]

        self._regex = re.compile(
            "(" + '$)|('.join(self._hooks_map.keys()) + "$)")
        return webob.response.Response(status=200)

    def delete_hook(self, request):
        try:
            hooks = request.json
        except:
            raise webob.exc.HTTPBadRequest(
                explanation="Input content not proper")
        for h in hooks:
            url_key = self._frame_url_key(h)
            if url_key not in self._hooks_map:
                return webob.response.Resonse(status=200)
            self._hooks_map[url_key] = [
                x for x in self._hooks_map[url_key] if not
                (h['type'] == x['type'] and
                 h['hooker'] == x['hooker'])]
        self._regex = re.compile(
            "(" + '$)|('.join(self._hooks_map.keys()) + "$)")
        return webob.response.Response(status=200)

    def _import(self, name):
        mod = __import__(name)
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod

    def _call_callback(self, cb, request):
        (module, method) = cb.split(":")
        try:
            mod = importlib.import_module(module)
            meth = getattr(mod, method)
        except Exception as e:
            # Unable to call the callback - return no action
            return webob.Response(
                status=HTTP_NO_ACTION_NEEDED)

        # the call back method should do the following
        # - return None => Implies, No action need from this hook
        # - return a jsonable object => Implies, send this data to the
        #                               end client before processing
        #                               the main URL
        # - raise an Exception => Implies return this error to client
        #                         The exception object should have
        #                         an attribute named 'status_code'
        try:
            out = meth(request)
        except Exception as e:
            import traceback
            traceback.print_exc()
            status_code = getattr(e, 'status_code', HTTP_NO_ACTION_NEEDED)
            body = getattr(e, 'body', None)
            return webob.Response(
                status=status_code, body=body)

        status_code = HTTP_NO_ACTION_NEEDED
        body = None
        if out:
            try:
                body = json.dumps(out)
                status_code = 200
            except Exception as e:
                pass
        return webob.Response(
            status=status_code, body=body)

    def hook_callback(self, request):
        params = request.params.copy()
        hooked_url_key = self._match_hook_url_key(
            params['method'], params['url'],
            self._hooked_regex, self._hooked_map)
        if not hooked_url_key:
            raise webob.exc.HTTPNotFound()

        cb = self._hooked_map[hooked_url_key]['handler']
        return self._call_callback(cb, request)

    def _match_hook_url_key(self, method, path, regex, hmap):
        url_key = ' '.join([method, path])
        m = re.match(regex, url_key)
        if not m:
            return
        index = next(i for i, j in enumerate(m.groups()) if j)
        return hmap.keys()[index]

    def _is_restricted(self, method, path, before_after, hooker):
        if self._restrict_regex:
            restrict_url_key = self._match_hook_url_key(
                method, path, self._restrict_regex, self._restrict_map)
            if restrict_url_key:
                r = self._restrict_map[restrict_url_key]
                if before_after in r['type'] and \
                        hooker not in r['except']:
                    # restrict hooking
                    return True

        return False

    def process_hooks_b(self, request):
        if not self._regex:
            # No hooks registered
            return

        hook_url_key = self._match_hook_url_key(
            request.method, request.path, self._regex, self._hooks_map)
        if not hook_url_key:
            return

        hook_data = {}
        for item in self._hooks_map[hook_url_key]:
            params = dict(zip(request.params.keys(),
                              request.params.values()))
            headers = dict()
            for k in request.headers:
                headers[k] = request.headers[k]
            if 'B' in item['type']:
                data = {'type': 'B',
                        'headers': headers,
                        'params': params,
                        'data': request.body}
                kwargs = {'json': data}
                if request.auth and 'email_id' in request.auth:
                    kwargs['user'] = request.auth['email_id']
                try:
                    resp = zutils.request_local_server(
                        'POST',
                        "/%s/_/hooks?method=%s&url=%s" % (
                            item['hooker'], request.method,
                            request.path),
                        timeout=0.100,
                        **kwargs)
                    if resp.status_code == 200 and resp.text:
                        hook_data[item['hooker']] = json.loads(resp.text)
                except:
                    # probably the timeout exception
                    pass

        # give the pre-hooks data to the API for processing
        request.hook_data = hook_data

    def process_hooks_a(self, request, response):
        if not self._regex:
            # No hooks registered
            return response

        hook_url_key = self._match_hook_url_key(
            request.method,
            request.path,
            self._regex, self._hooks_map)
        if not hook_url_key:
            return response

        # pop the hooks related header from the API response
        hook_data = response.text
        for item in self._hooks_map[hook_url_key]:
            if 'A' in item['type']:
                params = dict(zip(request.params.keys(),
                                  request.params.values()))

                data = {'params': params,
                        'type': 'A',
                        'status': response.status_code,
                        'data': hook_data,
                        }
                kwargs = {'json': data}
                if 'email_id' in request.auth:
                    kwargs['user'] = request.auth['email_id']
                try:
                    zutils.request_local_server(
                        'POST',
                        "/%s/_/hooks?method=%s&url=%s" % (
                            item['hooker'],
                            request.method,
                            request.path),
                        timeout=0.100,
                        **kwargs)
                except:
                    # probably the timeout exception
                    pass
        return response

    def pre(self, request):
        if request.path == "/%s/%s/_/hooks" % (
                cfg.CONF.app_provider_code, cfg.CONF.app_code):
            if request.method == "PUT":
                return self.add_hooks(request)
            elif request.method == 'DELETE':
                return self.delete_hook(request)
            elif request.method == 'POST':
                return self.hook_callback(request)
            else:
                raise webob.exc.HTTPNotFound(
                    explanation="Invalid method(%s)" % request.method)
        return self.process_hooks_b(request)

    def post(self, request, response):
        return self.process_hooks_a(request, response)
