from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import Name, syms
from lib2to3 import pytree


class FixYieldFrom(BaseFix):
    BM_compatible = True
    PATTERN = """
        yield_expr< 'yield'
            power< name=('From' | 'trollius' trailer< '.' 'From' >)
                   expr=trailer< '(' any ')' > > >
    """

    def transform(self, node, results):
        name_nodes = results['name']
        name_nodes[0].replace(Name('from', prefix=name_nodes[0].prefix))
        for node in name_nodes[1:]:
            node.remove()
