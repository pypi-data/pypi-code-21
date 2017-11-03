from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import Name, is_tuple, parenthesize, syms
from lib2to3 import pytree


class FixRaiseReturn(BaseFix):
    #BM_compatible = True
    PATTERN = """
        raise_stmt< 'raise' power=power< ('Return' | 'trollius' trailer< '.' 'Return' >)
            trailer=trailer< '(' expr=any ')' > > >
    """

    def transform(self, node, results):
        expr = results['expr']
        if is_tuple(expr):
            replacement = expr
        else:
            replacement = results['trailer']
        replacement.prefix = results['power'].prefix
        replacement.remove()
        return pytree.Node(syms.return_stmt, [Name('return', node.prefix), replacement])
