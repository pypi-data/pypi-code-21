"""Replace @trollius.coroutine with @asyncio.coroutine.

This ought to be handled by fix_imports, but the lib2to3 fixer doesn't
handle decorators.
"""

from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import Name


class FixDecorator(BaseFix):
    BM_compatible = True
    PATTERN = "decorator< '@' dotted_name< name='trollius' '.' any+ > any* >"

    def transform(self, node, results):
        name = results['name']
        name.replace(Name('asyncio', prefix=name.prefix))
