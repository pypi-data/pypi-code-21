import io
import os.path
import sys
import types
import importlib.machinery
import importlib.util


class CompilerContext:
    def __init__(self):
        self.varnames = []
        self.query_cache = []
        self._var_idx = 1

    def varname(self, prefix):
        self._var_idx += 1
        return '%s%s' % (prefix, self._var_idx - 1)

    def pushvar(self, name):
        self.varnames.append(name)

    def popvar(self):
        return self.varnames.pop()

    def cacheQuery(self, name, varname):
        self.query_cache[0][name] = varname

    def getCachedQuery(self, name):
        for c in self.query_cache:
            try:
                return c[name]
            except KeyError:
                pass
        return None

    def uncacheQuery(self, name):
        del self.query_cache[0][name]

    def startScope(self):
        self.query_cache.insert(0, {})

    def endScope(self):
        self.query_cache.pop(0)


class CompilerOutput:
    def __init__(self, buf):
        self._buf = buf
        self._indent = 0
        self._post_compilers = []
        self._is_post_compiling = False

    def write(self, data):
        self._buf.write(data)
        return self

    def writePushLocalVariable(self, name, var):
        self.write('ctx_pushLocalVariable("%s", %s)\n' % (name, var))
        return self

    def writePopLocalVariable(self, name):
        self.write('ctx_popLocalVariable("%s")\n' % name)
        return self

    def writeSetLocalVariable(self, name, var):
        self.write('ctx_locals["%s"] = %s\n' % (name, var))
        return self

    def indent(self):
        self._buf.write('\t' * self._indent)
        return self

    def push(self, indent_now=True):
        self._indent += 1
        if indent_now:
            self.indent()
        return self

    def pull(self):
        self._indent -= 1
        if self._indent < 0:
            raise Exception("Pulled too much!")
        return self

    def addPostCompiler(self, callback):
        if self._is_post_compiling:
            raise Exception("Can't add post compilers while post-compiling!")
        self._post_compilers.append(callback)


def write_render_opt_aliases(out):
    out.indent().write('# Loop optimization\n')
    out.indent().write('ctx_engine = ctx.engine\n')
    out.indent().write('ctx_invoke = ctx.invoke\n')
    out.indent().write('ctx_locals = ctx.locals\n')
    out.indent().write('ctx_query = ctx.query\n')
    out.indent().write('ctx_queryRoot = ctx.queryRoot\n')
    out.indent().write('ctx_pushLocalVariable = ctx.pushLocalVariable\n')
    out.indent().write('ctx_popLocalVariable = ctx.popLocalVariable\n')
    out.indent().write('get_filter = ctx_engine.getFilter\n')
    out.indent().write('out_write_escaped = '
                       'ctx_engine._getWriteEscapeFunc(out_write)\n')
    out.indent().write('\n')


def try_load_from_cached_filesystem_module(module_path):
    module_name, _ = os.path.splitext(os.path.basename(module_path))
    module_name = module_name.replace('.', '_')
    try:
        spec = importlib.util.spec_from_file_location(module_name,
                                                      module_path)
        if spec is None:
            return None

        module = importlib.util.module_from_spec(spec)
        if module is None:
            return None

        spec.loader.exec_module(module)
    except:
        return None

    sys.modules[module_name] = module
    return module_name


class InMemorySyntaxError(Exception):
    def __init__(self, inner, source_code):
        super().__init__()
        self.inner = inner
        self.source_code = source_code

    def __str__(self):
        return str(self.inner)


class Compiler:
    def __init__(self, engine):
        self.engine = engine
        self._imports = None

    def compileMemoryModule(self, root_node, module_name):
        self._compile(root_node, module_name, '<string>', True)
        return module_name

    def compileFileSystemModule(self, root_node, module_path):
        module_name, _ = os.path.splitext(os.path.basename(module_path))
        module_name = module_name.replace('.', '_')
        self._compile(root_node, module_name, module_path)
        return module_name

    def getCompileUnit(self, root_node):
        with io.StringIO() as buf:
            self._buildCompileUnit(root_node, buf)
            return buf.getvalue()

    def _compile(self, root_node, module_name, module_path, in_memory=False):
        with io.StringIO() as buf:
            self._buildCompileUnit(root_node, buf)

            if in_memory:
                try:
                    bytecode = compile(buf.getvalue(), module_path, 'exec')
                except SyntaxError as se:
                    # Wrap this in another exception that has the module's
                    # source code so we know what happened.
                    raise InMemorySyntaxError(se, buf.getvalue())

                module = types.ModuleType(module_name)
                exec(bytecode, module.__dict__)
                sys.modules[module_name] = module
            else:
                with open(module_path, 'w') as mfp:
                    mfp.write(buf.getvalue())

                spec = importlib.util.spec_from_file_location(
                    module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                sys.modules[module_name] = module

    def _buildImports(self):
        if self._imports is not None:
            return

        imports = []

        if self.engine is not None:
            for ext in self.engine.extensions:
                for sn_cls in ext.getStatementNodes():
                    imps = sn_cls.compiler_imports
                    if imps:
                        imports += imps

        self._imports = sorted(set(imports))

    def _buildCompileUnit(self, root_node, buf):
        self._buildImports()

        buf.write("# Inukshuk compiled template\n")
        buf.write("# Generated by Inukshuk version <unknown>.\n")
        buf.write("# flake8: noqa\n")
        buf.write("\n")

        for i in self._imports:
            buf.write(i)
            buf.write('\n')
        buf.write('\n')

        ctx = CompilerContext()
        out = CompilerOutput(buf)
        root_node.compile(ctx, out)

        out.write('\n')
        for callback in out._post_compilers:
            out._indent = 0
            out.write('\n\n')
            callback(ctx, out)
