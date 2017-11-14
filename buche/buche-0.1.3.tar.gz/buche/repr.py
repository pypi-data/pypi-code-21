
import os
import traceback
from hrepr import StdHRepr
from weakref import WeakValueDictionary
from collections import deque
from types import FrameType


class UNAVAILABLE:
    def __init__(self):
        pass

    def __hrepr__(self, H, hrepr):
        return H.span('<UNAVAILABLE>', style='color:#bbb')


UNAVAILABLE = UNAVAILABLE()


class Registry:
    def __init__(self, keep=10000):
        self.keep = keep
        self.id = 0
        self.weak_map = WeakValueDictionary()
        self.strong_map = {}
        self.strong_ids = deque()

    def register(self, obj):
        self.id += 1
        try:
            self.weak_map[self.id] = obj
        except TypeError:
            self.strong_map[self.id] = obj
            self.strong_ids.append(self.id)
            if len(self.strong_ids) > self.keep >= 0:
                rm = self.strong_ids.popleft()
                del self.strong_map[rm]
        return self.id

    def resolve(self, id):
        try:
            return self.weak_map[id]
        except KeyError:
            return self.strong_map.get(id, UNAVAILABLE)


id_registry = Registry()


def handle_exception(e, H, hrepr):
    tb = e.__traceback__
    entries = traceback.extract_tb(tb)
    first = e.args[0] if len(e.args) > 0 else None
    iss = isinstance(first, str)
    args_table = H.table()
    for i in range(1 if iss else 0, len(e.args)):
        arg = e.args[i]
        tr = H.tr(H.td(i), H.td(hrepr(arg)))
        args_table = args_table(tr)

    views = H.tabbedView['hrepr-Exception'](
        H.strong(type(e).__name__),
        f': {first}' if iss else '',
        args_table
    )
    if not entries:
        return views

    last = entries[-1]
    for entry in entries:
        filename, lineno, funcname, line = entry
        absfile = os.path.abspath(filename)
        view = H.view()
        tab = H.tab(
            f'{funcname}@{os.path.basename(absfile)}'
        )
        snippet = H.codeSnippet(
            src = absfile,
            language = "python",
            line = lineno,
            context = 4
        )
        if filename.startswith('<'):
            snippet = snippet(getattr(e, '__repl_string__', ""))

        pane = H.pane(snippet)
        if entry is last:
            view = view(active = True)
        views = views(view(tab, pane))

    return views


def handle_frame(fr, H, hrepr):
    views = H.tabbedView()
    code = fr.f_code
    info = dict(
        name=code.co_name,
        filename=code.co_filename,
        firstlineno=code.co_firstlineno,
        lineno=fr.f_lineno
    )
    snippet = H.codeSnippet(
        src = code.co_filename,
        language = "python",
        line = fr.f_lineno,
        context = 4
    )
    views = views(H.view(H.tab('code'), H.pane(snippet)))
    views = views(H.view(H.tab('info'), H.pane(hrepr(info))))
    return views


class HRepr(StdHRepr):
    def __default_handlers__(self):
        h = super().__default_handlers__()
        h.update({
            Exception: handle_exception,
            FrameType: handle_frame
        })
        return h

    def __call__(self, obj, **kwargs):
        res = super().__call__(obj, **kwargs)
        try:
            the_id = id_registry.register(obj)
        except TypeError as e:
            return res
        else:
            return self.H.iBox({'obj-id': the_id})(res)
