import os
from markupsafe import Markup, escape
from .template import Template


class UndefinedDataError(Exception):
    def __init__(self, undefined):
        message = "Value is undefined"
        if undefined:
            message = "'%s' is undefined" % undefined.__undefined_hint__
        super().__init__(message)


class UndefinedBase:
    def __init__(self, hint=None):
        self.__undefined_hint__ = hint


class StrictUndefined(UndefinedBase):
    def __str__(self):
        raise UndefinedDataError(self)

    def __bool__(self):
        raise UndefinedDataError(self)

    def __iter__(self):
        raise UndefinedDataError(self)

    def __next__(self):
        raise UndefinedDataError(self)

    def __call__(self, *args, **kwargs):
        raise UndefinedDataError(self)

    def __getitem__(self, name):
        raise UndefinedDataError(self)

    def __gt__(self, other):
        raise UndefinedDataError(self)

    def __ge__(self, other):
        raise UndefinedDataError(self)

    def __lt__(self, other):
        raise UndefinedDataError(self)

    def __le__(self, other):
        raise UndefinedDataError(self)

    def __eq__(self, other):
        raise UndefinedDataError(self)

    def __ne__(self, other):
        raise UndefinedDataError(self)


class IgnoreUndefined(UndefinedBase):
    def __str__(self):
        return ''

    def __bool__(self):
        return False

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration()

    def __call__(self, *args, **kwargs):
        return IgnoreUndefined()

    def __getitem__(self, name):
        return IgnoreUndefined()

    def __gt__(self, other):
        return False

    def __ge__(self, other):
        return False

    def __lt__(self, other):
        return True

    def __le__(self, other):
        return True

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return False


class SafeString(str):
    pass


class Engine:
    def __init__(self, loader=None,
                 strip_comments=True,
                 lstrip_blocks=False,
                 rstrip_blocks=False,
                 autoescape=False,
                 compile_templates=False,
                 compile_cache_dir=None):
        self.undefined = IgnoreUndefined()
        self.strip_comments = strip_comments
        self.lstrip_blocks = lstrip_blocks
        self.rstrip_blocks = rstrip_blocks
        self.autoescape = autoescape
        self.compile_templates = compile_templates
        self.compile_cache_dir = compile_cache_dir

        from .ext.core import CoreExtension
        self.extensions = [
            CoreExtension()]

        self.globals = {}
        self.filters = {}
        self.tests = {}
        self.loader = loader

        # Whatever is 0 is the default. See in the `rendering` module for
        # more information.
        self.access_mode = 0

        if compile_cache_dir:
            os.makedirs(compile_cache_dir, mode=0o700, exist_ok=True)

        self._loaded = False
        self._cache = {}

    def getTemplate(self, name, cache=True, compiled=None, memmodule=False):
        if cache:
            try:
                return self._cache[name]
            except KeyError:
                pass

        if self.loader is not None:
            source = self.loader.getSource(self, name)
            if source is not None:
                if compiled is None:
                    compiled = self.compile_templates
                t = Template(None, source=source, compiled=compiled,
                             memmodule=memmodule)
                t._engine = self
                if cache:
                    self._cache[name] = t
                return t
            else:
                raise Exception("No such template: %s" % name)
        raise Exception("No loader has been defined for this engine.")

    def cacheAllTemplates(self, compiled=None, memmodule=False,
                          cache_condition=None):
        if self.loader is not None:
            for name in self.loader.findAllNames(self):
                if cache_condition is not None and not cache_condition(name):
                    continue
                t = self.getTemplate(name, cache=True, compiled=compiled,
                                     memmodule=memmodule)
                t._compileContent()
        else:
            raise Exception("No loader has been defined for this engine.")

    def getFilter(self, name):
        try:
            return self.filters[name]
        except KeyError:
            raise Exception("No such filter: %s" % name)

    def getTest(self, name):
        try:
            return self.tests[name]
        except KeyError:
            raise Exception("No such test: %s" % name)

    def escape(self, val):
        if val is not None:
            if self.autoescape:
                if isinstance(val, (Markup, SafeString)):
                    return str(val)
                else:
                    return str(escape(str(val)))
            return str(val)
        return ''

    def _ensureLoaded(self):
        if self._loaded:
            return

        for e in self.extensions:
            e.setupEngine(self)
            self.globals.update(e.getGlobals())
            self.filters.update(e.getFilters())
            self.tests.update(e.getTests())

        self._loaded = True

    def _getWriteEscapeFunc(self, out_write, autoescape=None):
        if autoescape is None:
            autoescape = self.autoescape

        if autoescape:
            def _autoescape_write_escaped(val):
                if val is not None:
                    if isinstance(val, (Markup, SafeString)):
                        out_write(val)
                    else:
                        out_write(escape(str(val)))
            return _autoescape_write_escaped

        def _write_escaped(val):
            if val is not None:
                out_write(str(val))
        return _write_escaped


class _EmbeddedEngine(Engine):
    def __init__(self, tpl):
        super().__init__()
        self._template = tpl
