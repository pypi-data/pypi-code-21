from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import BlankLine, syms, token
from lib2to3 import pytree


class FixImportFromReturn(BaseFix):
    BM_compatible = True
    PATTERN = "import_from< 'from' 'trollius' 'import' ['('] imports=any [')'] >"

    def transform(self, node, results):
        imports = results['imports']
        if imports.type == syms.import_as_name or not imports.children:
            children = [imports]
        else:
            children = list(imports.children)
        for i in range(len(children) - 1, -1, -2):
            child = children[i]
            if child.type == token.NAME:
                name = child.value
            elif child.type == token.STAR:
                return
            else:
                assert child.type == syms.import_as_name
                name = child.children[0].value
            if name in ['From', 'Return']:
                if i + 1 < len(children):
                    children[i + 1].remove()
                    children[i].remove()
                    del children[i : i + 2]
                elif i > 0:
                    children[i].remove()
                    children[i - 1].remove()
                    del children[i - 1 : i + 1]
                else:
                    children[i].remove()
                    del children[i]
        if not children:
            new = BlankLine()
            new.prefix = node.prefix
            return new
        else:
            return None
