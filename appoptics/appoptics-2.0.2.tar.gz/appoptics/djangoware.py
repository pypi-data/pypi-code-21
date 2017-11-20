"""AppOptics instrumentation for Django

 Copyright (C) 2016 by SolarWinds, LLC.
 All rights reserved.
"""
import time
import functools
import threading
from appoptics import util
from appoptics import imports
try:
    from django.utils.deprecation import MiddlewareMixin as AppOpticsMiddlewareBase
except ImportError:
    AppOpticsMiddlewareBase = object

# django middleware for passing values to appoptics
__all__ = ("AppOpticsDjangoMiddleware", "install_appoptics_middleware")

appoptics_logger = util.logger


class AppOpticsWSGIHandler(object):
    """ Wrapper WSGI Handler for Django's django.core.handlers.wsgi:WSGIHandler
    Can be used as a replacement for Django's WSGIHandler, e.g. with uWSGI.
    """
    def __init__(self):
        """ Import and instantiate django.core.handlers.WSGIHandler,
        now that the load_middleware wrapper below has been initialized. """
        from django.core.handlers.wsgi import WSGIHandler
        self._handler = WSGIHandler()

    def __call__(self, environ, start_response):
        return self._handler(environ, start_response)


# Middleware hooks listed here: http://docs.djangoproject.com/en/dev/ref/middleware/
class AppOpticsDjangoMiddleware(AppOpticsMiddlewareBase):
    def __init__(self, *args, **kwargs):
        from django.conf import settings
        try:
            self.layer = settings.APPOPTICS_BASE_LAYER
        except AttributeError:
            self.layer = 'django'
        super(AppOpticsDjangoMiddleware, self).__init__(*args, **kwargs)

    def _singleline(self, e):  # some logs like single-line errors better
        return str(e).replace('\n', ' ').replace('\r', ' ')

    def process_request(self, request):
        try:
            xtr_hdr = request.META.get("HTTP_X-Trace",   request.META.get("HTTP_X_TRACE"))
            util.start_trace(self.layer, xtr=xtr_hdr, store_backtrace=False)
            request.META.setdefault('APPOPTICS_SPAN_START', str(int(time.time() * 1000000)))

        except Exception as e:
            appoptics_logger.debug("AppOptics middleware error: %s" % self._singleline(e))

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not util.Context.get_default().is_sampled():
            return
        try:
            controller = getattr(view_func, '__module__', None)
            action = getattr(view_func, '__name__', None)

            kvs = {
                'Controller': controller,
                'Action': action
            }
            util.log('process_view', None, keys=kvs, store_backtrace=False)
            if controller and action:
                request.META.setdefault('APPOPTICS_SPAN_TRANSACTION', '{c}.{a}'.format(c=controller, a=action))
        except Exception as e:
            appoptics_logger.debug("AppOptics middleware error: %s" % self._singleline(e))

    def process_response(self, request, response):
        """Process the response, record some information and send the end_trace out
        """
        default_ctx = util.Context.get_default()

        if not default_ctx.is_sampled():
            response['X-Trace'] = str(default_ctx)
            return response

        try:
            kvs = {
                'HTTP-Host': request.META.get('HTTP_HOST'),
                'Method': request.META.get('REQUEST_METHOD'),
                'URL': request.build_absolute_uri(),
                'Status': response.status_code
            }

            x_trace = util.end_trace(self.layer, keys=kvs)
            if x_trace:
                response['X-Trace'] = x_trace

            span_start = request.META.pop('APPOPTICS_SPAN_START', None)
            if span_start:
                span_start = int(span_start)
                span_stop = int(time.time() * 1000000)

                transaction_name = request.META.pop('APPOPTICS_SPAN_TRANSACTION', None)
                url = None if transaction_name else request.build_absolute_uri()

                util.SwigSpan.createHttpSpan(
                    transaction_name, url, span_stop - span_start, response.status_code,
                    request.META['REQUEST_METHOD'], 499 < response.status_code < 600,
                )

        except Exception as e:
            appoptics_logger.debug("AppOptics middleware error: %s" % self._singleline(e))

        return response

    def process_exception(self, request, exception):
        try:
            util.log_exception()
        except Exception as e:
            appoptics_logger.debug("AppOptics middleware error: %s" % self._singleline(e))


def middleware_hooks(module, objname):
    try:
        # wrap middleware callables we want to wrap
        cls = getattr(module, objname, None)
        if not cls:
            return
        for method in ['process_request',
                       'process_view',
                       'process_response',
                       'process_template_response',
                       'process_exception']:
            fn = getattr(cls, method, None)
            if not fn:
                continue
            profile_name = '%s.%s.%s' % (module.__name__, objname, method)
            setattr(cls, method,
                    util.profile_function(profile_name)(fn))
    except Exception as e:
        appoptics_logger.error("AppOptics error: %s" % str(e))

load_middleware_lock = threading.Lock()


def on_load_middleware():
    """ wrap Django middleware from a list """

    # protect middleware wrapping: only a single thread proceeds
    global load_middleware_lock         # lock gets overwritten as None after init
    if not load_middleware_lock:        # already initialized? abort
        return
    mwlock = load_middleware_lock
    mwlock.acquire()                    # acquire global lock
    if not load_middleware_lock:        # check again
        mwlock.release()                # abort
        return
    load_middleware_lock = None         # mark global as "init done"

    try:
        # middleware hooks
        from django.conf import settings
        # MIDDLEWARE_CLASSES has been replaced by MIDDLEWARE since Django 1.10
        middleware = getattr(settings, 'MIDDLEWARE', None)
        if middleware is None:
            middleware = getattr(settings, 'MIDDLEWARE_CLASSES', [])

        for i in middleware:
            if i.startswith('appoptics'):
                continue
            dot = i.rfind('.')
            if dot < 0 or dot+1 == len(i):
                continue
            objname = i[dot+1:]
            imports.whenImported(i[:dot],
                                 functools.partial(middleware_hooks, objname=objname))
        # ORM
        if util.config['inst_enabled']['django_orm']:
            from appoptics import inst_django_orm
            # The wrapper path BaseDatabaseWrapper has changed in Django 1.8 and onwards.
            imports.whenImported('django.db.backends.base.base', inst_django_orm.wrap)

        # templates
        if util.config['inst_enabled']['django_templates']:
            from appoptics import inst_django_templates
            import django
            imports.whenImported('django.template.base', inst_django_templates.wrap)

        # load pluggaable instrumentation
        from .loader import load_inst_modules
        load_inst_modules()

        if isinstance(middleware, list):
            middleware.insert(0, 'appoptics.djangoware.AppOpticsDjangoMiddleware')
        # settings.MIDDLEWARE_CLASSES is a tuple in 1.9 and prior versions.
        elif isinstance(middleware, tuple):
            if hasattr(settings, 'MIDDLEWARE'):
                settings.MIDDLEWARE = ('appoptics.djangoware.AppOpticsDjangoMiddleware',) + settings.MIDDLEWARE
            else:
                settings.MIDDLEWARE_CLASSES = ('appoptics.djangoware.AppOpticsDjangoMiddleware',) + settings.MIDDLEWARE_CLASSES
        else:
            appoptics_logger.error(
                "AppOptics error: thought MIDDLEWARE_CLASSES would be either a tuple or a list, got {mw_type}"
                .format(mw_type=str(type(middleware)))
            )
    except Exception as e:
        appoptics_logger.error('AppOptics error in on_load_middleware: {e}'.format(e=e))
        
    finally:  # release instrumentation lock
        mwlock.release()


def install_appoptics_middleware(module):
    def base_handler_wrapper(func):
        @functools.wraps(func)  # XXX Not Python2.4-friendly
        def wrap_method(*f_args, **f_kwargs):
            on_load_middleware()
            return func(*f_args, **f_kwargs)
        return wrap_method

    try:
        cls = getattr(module, 'BaseHandler', None)
        try:
            if not cls or cls.APPOPTICS_MIDDLEWARE_LOADER:
                return
        except AttributeError as e:
            cls.APPOPTICS_MIDDLEWARE_LOADER = True
        fn = getattr(cls, 'load_middleware', None)
        setattr(cls, 'load_middleware', base_handler_wrapper(fn))
    except Exception as e:
        appoptics_logger.error("AppOptics error: %s" % str(e))

if util.ready():
    try:
        imports.whenImported('django.core.handlers.base', install_appoptics_middleware)
        # phone home
        util.report_layer_init(layer='django')
    except ImportError as e:
        # gracefully disable tracing if AppOptics lib not present
        appoptics_logger.error("[AppOptics] Unable to instrument app and middleware: %s" % e)
