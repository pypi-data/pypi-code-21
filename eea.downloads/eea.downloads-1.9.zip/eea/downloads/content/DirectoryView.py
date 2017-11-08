""" Custom Filesystem Directory View
"""
import logging
import os

from Products.CMFCore import DirectoryView, FSFile
from Products.CMFCore.DirectoryView import createDirectoryView
from eea.downloads.config import PROJECTNAME

logger = logging.getLogger('eea.downloads')


class PatchedDirectoryInformation(DirectoryView.DirectoryInformation):
    """ Custom Directoy Information
    """
    def _changed(self):
        """ Changed
        """
        mtime = 0
        filelist = []
        try:
            mtime = os.stat(self._filepath)[8]
            if not self.use_dir_mtime:
                # some Windows directories don't change mtime
                # when a file is added to or deleted from them :-(
                # So keep a list of files as well, and see if that
                # changes
                os.path.walk(self._filepath, self._walker, filelist)
                filelist.sort()
        except Exception, err:
            logger.exception(err)

        if (mtime != getattr(self, '_v_last_read', None) or
            filelist != getattr(self, '_v_last_filelist', None)):
            self._v_last_read = mtime
            self._v_last_filelist = filelist

            return 1
        return 0


class PatchedFSFile(FSFile.FSFile):
    """ Custom FS File
    """
    manage_options = ({'label':'Properties', 'action':'manage_main'},)

    manage_main = DirectoryView.DirectoryViewSurrogate.manage_propertiesForm


def registerDirectory(filepath, prj=PROJECTNAME):
    """ Register file-system directory
    """
    return DirectoryView._dirreg.registerDirectoryByKey(filepath, prj)


DirectoryView.registerFileExtension('pdf', PatchedFSFile)
DirectoryView.registerFileExtension('epub', PatchedFSFile)
DirectoryView.registerFileExtension('lock', PatchedFSFile)

__all__ = [
    createDirectoryView.__name__,
    registerDirectory.__name__,
]
