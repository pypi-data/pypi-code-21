# MIT License
#
# Copyright (c) 2017 Bruce Merry
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import BlankLine, syms, token


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
