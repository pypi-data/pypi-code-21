""" EPub File mimetype
"""
from Products.MimetypesRegistry.MimeTypeItem import MimeTypeItem

class epub_mimetype(MimeTypeItem):
    """ Epub MimeType
    """
    __name__ = "Epub File"
    mimetypes = ('application/epub+zip',)
    extensions = ('epub',)
    globs = ('*.epub',)
    binary = 1

    def __init__(self, name='', mimetypes=None, extensions=None,
                 binary=None, icon_path='', globs=None):
        super(epub_mimetype, self).__init__()
        self.icon_path = 'epub.png'
