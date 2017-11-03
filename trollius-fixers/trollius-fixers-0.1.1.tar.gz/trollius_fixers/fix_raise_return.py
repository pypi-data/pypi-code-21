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
from lib2to3.fixer_util import Name, is_tuple, syms
from lib2to3 import pytree


class FixRaiseReturn(BaseFix):
    BM_compatible = True
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
