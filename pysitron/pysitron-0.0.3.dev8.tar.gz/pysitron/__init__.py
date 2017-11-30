"""
This module defines a base-object for building proton apps using html/css and javascript.
"""

from cefpython3 import cefpython as cef
# from werkzeug.serving import run_simple
from werkzeug.wsgi import SharedDataMiddleware
from wsgiref.simple_server import make_server
from jinja2 import Environment, BaseLoader

from threading import Thread
import platform
import sys
import win32con  # todo figure out a nice way of making the functionality used from win32 cross-platform
import win32gui
import win32api
import threading
import queue
import __main__ as main
import atexit
import os
import uuid
import functools
import base64
import tempfile


def static_path(filename):
    return "/" + filename

def jinja2_parse_str(input_string):
    env = Environment(loader=BaseLoader)
    env.filters['staticfile'] = static_path
    template = env.from_string(input_string)
    return template.render()

class Length_Correcting_Middleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):

        def custom_start_response(status, headers, exc_info=None):
            content_length = 20
            headers.append(('Content-Length', content_length))
            return start_response(status, headers, exc_info)

        return self.app(environ, custom_start_response)



def jinja2_parse_middleware(fun):
    def wrapped(environ, start_response):
        global call_args
        call_args = None

        def store_call_args(*args):
            global call_args
            call_args = args

        # Apparently we need something that also eats up writes() contents... More work
        if environ['PATH_INFO'].endswith('.html'):
            # Change the start_response so it just stores it's call, then here we change content-length and actually call it.

            text = [x for x in fun(environ, store_call_args)]

            start_response('200 OK', [('Content-Type', 'text/html')])

            text2 = [jinja2_parse_str(x.decode('utf-8')).replace('\n', '\r\n').encode('utf-8') for x in text]
            return text2
        else:
            cont = fun(environ, store_call_args)
            start_response(*call_args)
        return cont
    return wrapped


def argument_python_to_javascript(arg):
    if type(arg) is str:
        return '"' + arg + '"'
    else:
        return str(arg)


def return_value(func):
    @functools.wraps(func)
    def _wrapped(self, resolve, *args, **kwargs):
        result = func(self, *args, **kwargs)
        resolve.Call(result)
    return _wrapped


def daemon_threaded(fun):
    def wrapped(*args, **kwargs):
        t = Thread(target=fun, args=args, kwargs=kwargs, daemon=True)  # Offload work and return immidately in order to not block the gui
        t.start()
    return wrapped


def enum_handler(hwnd, results):
    results[hwnd] = {
        "title": win32gui.GetWindowText(hwnd),
        "visible": win32gui.IsWindowVisible(hwnd),
        "minimized": win32gui.IsIconic(hwnd),
        "rectangle": win32gui.GetWindowRect(hwnd),  # (left, top, right, bottom)
        "next": win32gui.GetWindow(hwnd, win32con.GW_HWNDNEXT)  # Window handle to below window
    }


def get_windows():
    enumerated_windows = {}
    win32gui.EnumWindows(enum_handler, enumerated_windows)
    return enumerated_windows


def get_window_by_title(title):
    windows = get_windows()
    gotten = next(win for win in windows if windows[win]['title'] == title)
    return gotten


def get_open_port():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def load_icon_from_file(icon_path):
    hinst = win32api.GetModuleHandle(None)
    icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
    hicon = win32gui.LoadImage(hinst, icon_path, win32con.IMAGE_ICON, 0, 0, icon_flags, )
    return hicon


class LoadHandler(object):
    def __init__(self, on_load_function=None, window_title="", window_dimensions=(800, 500), browser=None, methods=None, isClosing=None, icon_path=None):
        self.window_dimensions = window_dimensions
        self.window_title = window_title
        self.on_load_function = on_load_function
        self.windowfixed = False
        self.browser = browser
        self.methods = methods
        self.isClosing = isClosing
        self.icon_path = icon_path

    def OnBeforeClose(self, browser, **_):
        self.isClosing.set()

    def OnBeforeResourceLoad(self, browser, **_):
        if not self.windowfixed:
            app_width = self.window_dimensions[0]    # 1600
            app_height = self.window_dimensions[1]    # 932

            # hwnd = win32gui.GetForegroundWindow()
            hwnd = get_window_by_title(self.window_title)

            win32gui.MoveWindow(hwnd, 0, 0, app_width, app_height, True)

            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            style &= ~win32con.WS_SIZEBOX
            # style &= ~win32con.WS_MINIMIZEBOX
            style &= ~win32con.WS_MAXIMIZEBOX
            win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

            # Generate default icon
            from pysitron.icon import iconstr
            if self.icon_path is None:
                with tempfile.NamedTemporaryFile(delete=False) as temp:
                    temp.write(base64.b64decode(iconstr))
                    temp.close()
                    self.icon_path = temp.name

            icon = load_icon_from_file(self.icon_path)

            win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, icon)
            win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, icon)

            def destroy_icon(icon):
                win32gui.DestroyIcon(icon)

            atexit.register(destroy_icon, icon)

            print('done loading')
            self.windowfixed = True

    def OnLoadStart(self, browser, frame):
        self.browser.ExecuteJavascript("""
                                var BackEnd=window;

                                function returnwrapper(func) {
                                    async function wrapped(callback_id, ...args) {    
                                        out = await func(...args);
                                        window.javascript_return(callback_id, out);

                                    }
                                    return wrapped
                                }

                                function joiner(resolve, args){
                                    var new_args = new Array(resolve);
                                    if (args.length > 0) {
                                        new_args.push.apply(new_args, args)
                                    }
                                    return new_args;
                                }

                                function returnAsPromise(func) {
                                    function caller(...args) {
                                        return new Promise(resolve => func.apply(self, joiner(resolve, args)));
                                    }
                                    return caller;
                                };

                                """)

        # Apply wrapper to make functions return promises
        for method in self.methods:
            self.browser.ExecuteJavascript(f'{method} = returnAsPromise({method});')

    def OnLoadEnd(self, browser, frame, http_code):
        if frame.IsMain():
            if self.on_load_function is not None:
                self.on_load_function(browser)


class PysitronApp:
    def __init__(self, landing_page='', start_page = '', window_title=None,
                 port_number=None, window_dimensions = (400, 300), icon_path=None, developer_mode=False):
        self.window_dimensions = window_dimensions
        self.port_number = get_open_port() if port_number is None else port_number
        self.default_text = landing_page
        self.window_title = window_title if window_title is not None else self.__class__.__name__
        self.start_page = start_page
        self.javascript_bound = False
        self.bindings = cef.JavascriptBindings(bindToFrames=True, bindToPopups=True)
        self.queue = queue.Queue()
        self.methods = None
        self.isClosing = threading.Event()
        self._return_queue_dict = dict()
        self.icon_path = icon_path

        check_versions()
        sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
        cef.DpiAware.SetProcessDpiAware()

        # Path fix used when freezing using cx_freeze
        freeze_paths = {'browser_subprocess_path': os.path.dirname(sys.executable) + r'\cefpython3\subprocess.exe',
                 'resources_dir_path': os.path.dirname(sys.executable) + r'\cefpython3',
                 'locales_dir_path': os.path.dirname(sys.executable) + r'\cefpython3\locales'
                 } if getattr(sys, 'frozen', False) else {}

        if developer_mode:
            dev_options = {'context_menu': {'enabled': True}, 'debug': True, 'log_severity': 0}
        else:
            dev_options = {'context_menu': {'enabled': False}}

        cef.Initialize(settings={'auto_zooming': 'system_dpi',
                                 'multi_threaded_message_loop': True,
                                 **dev_options,
                                 **freeze_paths})
        browser = None

        # Dance a little jig to do synchronous asynchronous initialisation...
        postqueue = queue.Queue()

        def create_browser():
            print('Serving on localhost:' + str(self.port_number))
            postqueue.put(cef.CreateBrowserSync(url=r"http://localhost:" + str(self.port_number) + '/' + self.start_page,
                                                window_title=self.window_title))

        cef.PostTask(cef.TID_UI, create_browser)

        self.browser = postqueue.get()
        self.window = JSAcessObject(browser=self.browser, queue_ref=self.queue, app=self)

    def javascript_return(self, callback_id, returned):
        self._return_queue_dict[callback_id].put(returned)

    def ExecuteJavascript(self, string):
        self.browser.ExecuteJavascript(string)

    def ExecuteFunction(self, string_fun, *args):
        callback_id = str(uuid.uuid1())
        self._return_queue_dict[callback_id] = queue.Queue(maxsize=1)
        self.browser.ExecuteFunction(f'returnwrapper({string_fun})', callback_id, *args)
        return self._return_queue_dict[callback_id].get()

    def ExecuteJavascript_syncronous(self, string):
        callback_id = str(uuid.uuid1())
        self._return_queue_dict[callback_id] = queue.Queue(maxsize=1)
        self.browser.ExecuteJavascript(string + f'\njavascript_return("{callback_id}","");')
        self._return_queue_dict[callback_id].get()

    def set_value(self, value):
        object.__getattribute__(self, 'queue').put(value)

    def Slot(*args, **kwargs):
        def wrapper(fun):
            def wrapped(*args, **kwargs):
                return fun(*args, **kwargs)
            return wrapped
        return wrapper

    def bind_javascript(self):
        self.bindings.SetFunction('set_value', self.set_value)

        sub_class_methods = [method_name for method_name in dir(self.__class__) if (not method_name.startswith('_'))
                            and (method_name not in dir(PysitronApp))
                            and callable(getattr(self.__class__, method_name))
                            and getattr(getattr(self.__class__, method_name), 'bind_to_window', True)]
        for method in sub_class_methods:
            # Injecting the self object back into bound functions, so it's easier for the python side of things
            # to mess around with things.
            # todo review if it´s a sane thing to make all callbacks threaded
            loaded_method = lambda *args, raw_method=getattr(self.__class__, method): daemon_threaded(return_value(raw_method))(self, *args)
            self.bindings.SetFunction(method, loaded_method)


        self.methods = sub_class_methods

        self.bindings.SetFunction('javascript_return', self.javascript_return)

        self.browser.SetJavascriptBindings(self.bindings)

        self.javascript_bound = True

    def setup_server(self, on_load_function=None):
        """Start server and front-end"""

        def no_app(environ, start_response):
            """Dummy app since all files are in static directory"""
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [self.default_text.encode('utf-8')]

        # Building the wrapped app
        # Path switch used to ensure the proper path when building with cx_freeze
        get_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(main.__file__)
        app = SharedDataMiddleware(no_app, {'/': get_path})

        app2 = jinja2_parse_middleware(app)

        def starter():
            #run_simple(r'localhost', self.port_number, app2, use_reloader=False, use_debugger=False, static_files={'/': os.path.dirname(main.__file__)})
            httpd = make_server('', self.port_number, app2)
            print(f"Serving on port {self.port_number}...")
            httpd.serve_forever()

        th = threading.Thread(target=starter, daemon=True)
        th.start()

        self.browser.SetClientHandler(LoadHandler(on_load_function,
                                                  window_title=self.window_title,
                                                  window_dimensions=self.window_dimensions,
                                                  browser=self, methods=self.methods,
                                                  isClosing=self.isClosing,
                                                  icon_path=self.icon_path))

    def run(self, onload = None):
        """ Binds the javascript functions if this has not already been done, and starts the server and front-end"""
        if not self.javascript_bound:
            self.bind_javascript()

        self.setup_server(on_load_function=onload)

        self.isClosing.wait()
        cef.Shutdown()

class JSAcessObject:
    """Ad-hoc object used to make dom assignments act as if they were more naturally supported"""
    # todo: this could likely be build much much better. But for rough solution it works quite well.
    # Note throughout this code. object.__setattr__ and object.__getattribute__ are used to access object attributes,
    # because the JSAcessObject methods themselves are overwritten.
    def __init__(self, build='window', browser=None, queue_ref=None, app=None):
        object.__setattr__(self, 'app', app)
        object.__setattr__(self, 'build', build)
        object.__setattr__(self, 'browser', browser)
        object.__setattr__(self, 'queue_ref', queue_ref)

    def set_browser(self, browser):
        object.__setattr__(self, 'browser', browser)

    def __getattr__(self, item):
        if item in ('value', 'nodeValue', 'textContent', 'innerHTML'):
            # In this case, a javascript call is made to set the value in python in a queue and this part then waits on that thread to be filled.
            self.browser.ExecuteJavascript('set_value(' + self.build + '.' + item + ')')
            return object.__getattribute__(self, 'queue_ref').get()

        elif item not in ('set_browser', 'build'):
            return JSAcessObject(build=self.build + '.' + item,
                                 browser=object.__getattribute__(self, 'browser'),
                                 queue_ref=object.__getattribute__(self, 'queue_ref'),
                                 app=self.app)
        else:
            return object.__getattribute__(self, item)

    def __call__(self, *args, **kwargs):
        return JSAcessObject(self.build + '(' + ','.join(argument_python_to_javascript(x) for x in args) + ')',
                             browser=object.__getattribute__(self, 'browser'),
                             queue_ref=object.__getattribute__(self, 'queue_ref'),
                             app=self.app)

    def __setattr__(self, key, value):
        if value is not None:
            browser = object.__getattribute__(self, 'browser')
            set_string = ''.join([self.build + '.' + key, '=', argument_python_to_javascript(value), ';'])
            if browser is not None:
                self.app.ExecuteJavascript_syncronous(set_string)
            return None


def check_versions():
    print("[hello_world.py] CEF Python {ver}".format(ver=cef.__version__))
    print("[hello_world.py] Python {ver} {arch}".format(
          ver=platform.python_version(), arch=platform.architecture()[0]))
    assert cef.__version__ >= "55.3", "CEF Python v55.3+ required to run this"



__version__ = "0.0.3-dev8"
