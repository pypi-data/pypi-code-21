

class StopVisit(Exception):
    pass


class ParserNodeVisitor:
    def __init__(self):
        pass

    def visit(self, node, *args, **kwargs):
        try:
            self._doVisit(node, *args, **kwargs)
        except StopVisit:
            return
        self.postVisit(node, *args, **kwargs)

    def postVisit(self, node, *args, **kwargs):
        pass

    def _doVisit(self, node, *args, **kwargs):
        visiter_name = 'visit%s' % node.__class__.__name__
        visiter = getattr(self, visiter_name, self._visitAny)
        if visiter(node, *args, **kwargs) is False:
            raise StopVisit()

        for c in node.iterChildren():
            self._doVisit(c, *args, **kwargs)

        post_visiter_name = 'postVisit%s' % node.__class__.__name__
        post_visiter = getattr(self, post_visiter_name, None)
        if post_visiter is not None:
            post_visiter(node, *args, **kwargs)

    def _visitAny(self, node, *args, **kwargs):
        return True


class Optimizer(ParserNodeVisitor):
    def __init__(self):
        super().__init__()
        self.new_root_children = []
        self.head_queries = {}

    def optimize(self, root_node):
        self.visit(root_node)

        for c in reversed(self.new_root_children):
            root_node.children.insert(0, c)

    def visitIncludeStatementNode(self, node):
        pl = _IncludeStatementPreLoader(node.include_name, node)
        self.new_root_children.append(pl)

    def visitContextQueryNode(self, node):
        if node.is_head:
            try:
                qlist = self.head_queries[node.name]
            except KeyError:
                qlist = []
                self.head_queries[node.name] = qlist
                node.force_cache_query = True
            qlist.append(node)


class _IncludeStatementPreLoader:
    def __init__(self, include_name, node):
        self.include_name = include_name
        self._node = node
        self._func_name = None

    def compile(self, ctx, out):
        func_name = ctx.varname('inc_tpl')
        self._node._pre_loaded_name = func_name

        out.indent().write('tpl = ctx_engine.getTemplate(%s)\n' %
                           repr(self.include_name))
        out.indent().write('tpl._compileContent(True)\n')
        out.indent().write(
            'tpl_mod = importlib.import_module(tpl._compiled_module_name)\n')
        out.indent().write('global %s\n' % func_name)
        out.indent().write(
            '%s = getattr(tpl_mod, "render_template")\n' % func_name)
        out.indent().write('\n')

        out.addPostCompiler(self._postCompile)
        self._func_name = func_name

    def _postCompile(self, ctx, out):
        ctx.startScope()
        out.write('%s = None' % self._func_name)
        ctx.endScope()
