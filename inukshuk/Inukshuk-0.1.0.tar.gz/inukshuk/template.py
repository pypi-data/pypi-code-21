import io
import os.path
import sys


def make_module_name(name):
    return name.replace('/', '_').replace('\\', '_') + '.py'


class Template:
    """ An Inukshuk template, which can be rendered several times with
        different data.
    """
    def __init__(self, content, source=None, compiled=False, memmodule=False):
        if source is not None:
            self._name = source.name
            self._content = source.source
            self._getmtime = source.getmtime
        else:
            self._name = str(id(self))
            self._content = content
            self._getmtime = None
        self._root_node = None
        self._engine = None
        self._compiled = compiled
        self._compiled_module_name = None
        self._compiled_module_filename = None
        self._compiled_in_memory = memmodule

    def render(self, data):
        use_join = True
        # Somehow, Python is faster at joining strings than at filling up
        # one buffer in memory... I'm keeping the other code path for a
        # little while until I've benchmarked more situations.
        if use_join:
            out = []
            self._renderWithContext(None, data, out.append)
            return ''.join(out)
        else:
            with io.StringIO() as out:
                # Reserve the same size as the original text, as a rule of
                # thumb for how much we'll need. This reduces the need for
                # Python to reallocate the buffer as we go.
                out.truncate(len(self._content))
                out.seek(0)

                self._renderWithContext(None, data, out.write)
                return out.getvalue()

    def renderInto(self, data, out_buffer):
        self._renderWithContext(None, data, out_buffer.write)

    def _renderWithContext(self, ctx, data, out):
        self._initEngine()
        self._compileContent()

        if ctx is None:
            from .rendering import RenderContext
            ctx = RenderContext(self._engine, self._engine.access_mode)

        self._doRender(ctx, data, out)

    def _compileContent(self, force_compiled=False):
        # Early out if we're all ready to go.
        if (self._root_node is not None or
                self._compiled_module_name is not None):
            return

        engine = self._engine

        # Build the compiled module filename if we can.
        if (engine.compile_cache_dir is not None and
                self._compiled_module_filename is None and
                not self._compiled_in_memory):
            self._compiled_module_filename = os.path.join(
                engine.compile_cache_dir, make_module_name(self._name))

        # See if we can just import from the compiled module cache.
        if self._compiled_module_filename is not None:
            # See if the cache is younger than the source.
            do_load_cache = False
            if self._getmtime is not None:
                cache_time = 0
                try:
                    cache_time = os.path.getmtime(
                        self._compiled_module_filename)
                except (IOError, OSError):
                    pass
                if cache_time > self._getmtime():
                    do_load_cache = True

            if do_load_cache:
                from .compiler import try_load_from_cached_filesystem_module
                module_name = try_load_from_cached_filesystem_module(
                    self._compiled_module_filename)
                if module_name is not None:
                    # Success! Loaded from cache!
                    self._compiled_module_name = module_name
                    return

        # No luck with the cache. Let's do some real work.
        # Start with parsing the source if needed.
        if self._root_node is None:
            from .lexer import Lexer
            from .parser import Parser
            lexer = Lexer()
            tokens = lexer.tokenize(self._content)
            parser = Parser(engine)
            self._root_node = parser.parse(tokens)

        # Now see if we need to compile this stuff.
        if self._compiled or force_compiled:
            from .optimizer import Optimizer
            optimizer = Optimizer()
            optimizer.optimize(self._root_node)

            from .compiler import Compiler
            compiler = Compiler(engine)
            if self._compiled_module_filename is None:
                mod_name = 'inuk_tpl_%s' % make_module_name(self._name)
                n = compiler.compileMemoryModule(self._root_node, mod_name)
            else:
                n = compiler.compileFileSystemModule(
                    self._root_node, self._compiled_module_filename)
            self._compiled_module_name = n

    def _initEngine(self):
        if self._engine is None:
            from .engine import _EmbeddedEngine
            self._engine = _EmbeddedEngine(self)
        self._engine._ensureLoaded()

    def _doRender(self, ctx, data, out):
        if self._compiled:
            module = sys.modules[self._compiled_module_name]
            render_func = getattr(module, 'render_template')
            render_func(ctx, data, out)
        else:
            self._root_node.render(ctx, data, out)
