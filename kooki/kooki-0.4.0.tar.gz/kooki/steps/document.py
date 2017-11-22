from kooki import DocumentException
from kooki.tools.output import Output

from . import Step

class Document(Step):

    def __init__(self, config):

        super().__init__(config)

        self._infos = []
        self._name = 'document'

    def __call__(self, template, extensions, metadata):

        Output.start_step(self._name)
        Output.info(template)

        if template in extensions:
            kooki = extensions[template]
        else:
            raise DocumentException('bad template')

        document = kooki(**metadata)

        return document
