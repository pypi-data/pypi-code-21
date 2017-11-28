from .funcbase import FuncCallNode


class TestNode(FuncCallNode):
    __op_precedence__ = 10
    __op_type__ = 2

    def _getFunc(self, ctx, name):
        return ctx.engine.getTest(name)

    def _compileGetFunc(self, name):
        return 'ctx_engine.getTest(%s)' % repr(name)
