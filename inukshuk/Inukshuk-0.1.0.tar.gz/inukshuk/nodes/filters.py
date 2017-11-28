from .funcbase import FuncCallNode


class FilterNode(FuncCallNode):
    def _getFunc(self, ctx, name):
        return ctx.engine.getFilter(name)

    def _compileGetFunc(self, name):
        return 'get_filter(%s)' % repr(name)
