""" Monkey patches
"""
import os
from Products.CMFCore import DirectoryView
from eea.downloads.content.DirectoryView import PatchedDirectoryInformation

def registerDirectoryByKey(self, filepath, reg_key, subdirs=1,
                               ignore=DirectoryView.ignore):
    """ Custom behaviour for eea.downloads keys
    """
    if 'eea.downloads' not in reg_key:
        return self._old_registerDirectoryByKey(
            filepath, reg_key, subdirs, ignore)
    #
    # Custom behaviour for eea.downloads
    #
    info = PatchedDirectoryInformation(filepath, reg_key, ignore)
    self._directories[reg_key] = info
    if subdirs:
        for entry in info.getSubdirs():
            entry_filepath = os.path.join(filepath, entry)
            entry_reg_key = '/'.join((reg_key, entry))
            self.registerDirectoryByKey(entry_filepath, entry_reg_key,
                                        subdirs, ignore)
