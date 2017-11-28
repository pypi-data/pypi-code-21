
ATTR_FIRST_ACCESS = 0
DICT_FIRST_ACCESS = 1


class RenderContext:
    def __init__(self, engine, mode=ATTR_FIRST_ACCESS):
        self.engine = engine
        self.locals = {}
        self.globals = engine.globals.copy()
        self.user_data = {}
        self._locals_stack = {}
        self._parent_ctx = None
        self._mode = mode

        sl = self.locals
        sg = self.globals
        if mode == ATTR_FIRST_ACCESS:
            self.query = lambda d, pn: \
                _attr_first_access(self, d, pn)
            self.queryRoot = lambda d, pn: \
                _attr_first_access_root(self, sl, d, sg, pn)
        elif mode == DICT_FIRST_ACCESS:
            self.query = lambda d, pn: \
                _dict_first_access(self, d, pn)
            self.queryRoot = lambda d, pn: \
                _dict_first_access_root(self, sl, d, sg, pn)
        else:
            raise Exception("Unknown access mode: %s" % mode)

    def createChildContext(self):
        r = RenderContext(self.engine, self._mode)
        r._parent_ctx = self
        return r

    def mergeChildContext(self, ctx, endpoint=None):
        if endpoint is None:
            self.locals.update(ctx.locals)
        else:
            self.locals[endpoint] = ctx.locals.copy()

    def pushLocalVariable(self, name, value):
        try:
            prev_value = self.locals[name]
        except KeyError:
            self.locals[name] = value
            return

        history = self._locals_stack.setdefault(name, [])
        history.append(prev_value)
        self.locals[name] = value

    def popLocalVariable(self, name):
        try:
            history = self._locals_stack[name]
        except KeyError:
            del self.locals[name]
            return

        prev_value = history.pop()
        self.locals[name] = prev_value
        if len(history) == 0:
            del self._locals_stack[name]

    def render_comment(self, text):
        return '<!-- %s -->' % text

    def invoke(self, data, out, data_func, *args, **kwargs):
        if getattr(data_func, 'needs_context', False):
            return data_func(self, data, out, *args, **kwargs)
        else:
            return data_func(*args, **kwargs)


def needs_context(f):
    f.needs_context = True
    return f


def _attr_first_access(ctx, data, prop_name):
    try:
        return getattr(data, prop_name)
    except AttributeError:
        pass

    try:
        return data[prop_name]
    except KeyError:
        pass

    return ctx.engine.undefined


def _attr_first_access_root(ctx, ctx_locals, data, ctx_globals, prop_name):
    try:
        return ctx_locals[prop_name]
    except KeyError:
        pass

    if data is not None:
        try:
            return getattr(data, prop_name)
        except AttributeError:
            pass

        try:
            return data[prop_name]
        except KeyError:
            pass

    try:
        return ctx_globals[prop_name]
    except KeyError:
        pass

    parent = ctx._parent_ctx
    if parent is not None:
        return parent.queryRoot(data, prop_name)

    return ctx.engine.undefined


def _dict_first_access(ctx, data, prop_name):
    try:
        return data[prop_name]
    except (KeyError, TypeError):
        pass

    try:
        return getattr(data, prop_name)
    except AttributeError:
        pass

    return ctx.engine.undefined


def _dict_first_access_root(ctx, ctx_locals, data, ctx_globals, prop_name):
    try:
        return ctx_locals[prop_name]
    except KeyError:
        pass

    if data is not None:
        try:
            return data[prop_name]
        except (KeyError, TypeError):
            pass

        try:
            return getattr(data, prop_name)
        except AttributeError:
            pass

    try:
        return ctx_globals[prop_name]
    except KeyError:
        pass

    if ctx._parent_ctx is not None:
        return ctx._parent_ctx.queryRoot(data, prop_name)

    return ctx.engine.undefined
