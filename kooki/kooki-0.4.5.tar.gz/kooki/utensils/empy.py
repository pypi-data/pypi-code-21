import em
from kooki.tools import DictAsMember
from kooki import DocumentException
from . import Utensil

class Empy(Utensil):

    def __init__(self, metadata={}):

        self._interpreter = em.Interpreter()
        self._interpreter.setPrefix('@')

        self._metadata = metadata

    def __call__(self, **kwargs):

        if 'content' in kwargs:
            content = kwargs['content']
        else:
            raise DocumentException('Empy: argument error in step')

        if 'metadata' in kwargs:
            metadata = kwargs['metadata']
        else:
            metadata = {}

        metadata_copy = self._metadata.copy()
        metadata_copy.update(metadata)
        metadata_member = DictAsMember.convert(metadata_copy)

        try:
            content = self._interpreter.expand(content, metadata_member)
        except KeyError as e:
            raise DocumentException('Missing variable: {0}'.format(e))

        return {'content': content}
