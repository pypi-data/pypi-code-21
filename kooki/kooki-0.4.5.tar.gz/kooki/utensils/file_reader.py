from kooki.tools import read_file
from kooki import DocumentException
from . import Utensil

class FileReader(Utensil):

    def __call__(self, **kwargs):

        arguments = kwargs

        if 'source' in arguments:
            source = arguments['source']
        else:
            raise DocumentException('FileReader: argument error in step')

        content = read_file(source)
        arguments.update({'content': content})

        return arguments
