from kooki.tools import get_front_matter
from kooki import DocumentException
from . import Utensil
import yaml

class FrontMatter(Utensil):

    def __call__(self, **kwargs):

        arguments = kwargs

        if 'content' in arguments:
            content = arguments['content']
        else:
            raise DocumentException('Frontmatter argument error')

        if 'metadata' in arguments:
            metadata = arguments['metadata']
        else:
            metadata = {}

        front_matter, content = get_front_matter(content)

        if not isinstance(front_matter, dict):
            raise DocumentException('Bad front matter, kooki only support yaml dict front matter for now')

        front_matter.update(metadata)
        metadata = front_matter

        arguments.update({'metadata': metadata, 'content': content})

        return arguments
