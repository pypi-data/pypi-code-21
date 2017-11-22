import markdown
from kooki import DocumentException
from . import Utensil

class MarkdownToHTML(Utensil):

    def __init__(self):

        extensions = [
            'markdown.extensions.meta',
            'markdown.extensions.tables',
            'markdown.extensions.attr_list',
            'markdown.extensions.fenced_code',
            'markdown.extensions.def_list',
            'markdown.extensions.sane_lists',
            'markdown.extensions.codehilite']

        self._md = markdown.Markdown(extensions=extensions)

    def __call__(self, **kwargs):

        if 'content' in kwargs:
            content = kwargs['content']
        else:
            raise DocumentException('MarkdownToHTML: argument error in step')

        md_content = self._md.convert(content)
        return {'content': md_content}
