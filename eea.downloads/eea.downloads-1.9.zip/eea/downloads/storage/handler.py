""" File-system storage adapters

    >>> from eea.downloads.interfaces import IStorage

    >>> portal = layer['portal']
    >>> sandbox = portal._getOb('sandbox')

"""
import os
from zope.component import queryAdapter
from zope.component.hooks import getSite
from eea.downloads.config import ENVNAME, ENVPATH
from plone.uuid.interfaces import IUUID

class Storage(object):
    """ File-sytem storage

        >>> storage = IStorage(sandbox).of('pdf')
        >>> storage
        <eea.downloads.storage.handler.Storage object at ...>

    """
    def __init__(self, context):
        self.context = context
        self.path = ENVPATH()
        self.folder = ENVNAME()

    def of(self, extension):
        """ Storage for
        """
        self.__name__ = extension
        return self

    @property
    def extension(self):
        """ File extension
        """
        return self.__name__

    #
    # File-system API
    #
    def filefolder(self, relative=False):
        """ File-system absolute or relative path to containing folder

            >>> storage.filefolder()
            '/tmp/tmp.../.../...'

            >>> storage.filefolder(relative=1)
            '.../...'

        """
        paths = []
        if not relative:
            paths.append(self.path)

        uid = queryAdapter(self.context, IUUID)
        if uid:
            paths.append(uid)

        modified = getattr(self.context, 'modified', lambda: None)()
        modified = getattr(modified, 'asdatetime', lambda: None)()
        modified = getattr(modified, 'strftime', lambda format: '0')('%s')
        if modified:
            paths.append(modified)

        if paths:
            return os.path.join(*paths)
        return ''

    def filepath(self, relative=False):
        """ Absolute or relative file-system path to file

            / <ENVPATH> / <o.UID> / <o.modified> / <o.id>.pdf
            >>> storage.filepath()
            '/tmp/tmp.../.../.../sandbox.pdf'

            <o.UID> / <o.modified> / <o.id>.pdf
            >>> storage.filepath(relative=1)
            '.../.../sandbox.pdf'

        """
        return os.path.join(
            self.filefolder(relative),
            self.filename
        )

    @property
    def filename(self):
        """ File-system file name

            >>> storage.filename
            'sandbox.pdf'

        """
        return '.'.join((
            self.context.getId(),
            self.extension
        ))

    #
    # Web API
    #
    def absolute_url(self, relative=False):
        """ Web URL to file

            >>> storage.absolute_url()
            'http://nohost/plone/downloads/.../.../sandbox.pdf'

            >>> storage.absolute_url(1)
            'plone/downloads/.../.../sandbox.pdf'

        """

        site = getSite()
        return os.path.join(
            site.absolute_url(relative),
            self.folder,
            self.filepath(relative=True)
        )
