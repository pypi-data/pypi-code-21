###############################################################################
# (c) Copyright 2016 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''

Module that allows to retrieve information about and extract a .rpm file
e.g::

    pm = PackageManager(/path/to/myfile.rpm, relocateMap)

relocateMap being a map between the prefix as mentioned in the
RPM and the final location::

    { "/opt/LHCbSoft":"/opt/siteroot/lhcb" }

Then it is possible to extract information like::

 pm.getGroup()
 pm.getProvides()
 pm.getRequires()
 [...]

:author: Ben Couturier
'''
import logging
import os
import stat
import lbinstall.rpmfile as rpmfile
import hashlib
from lbinstall.Model import Provides, Requires, Package
import shutil
import tempfile
#
# Missing features:
# - handle hard links
# - handle modification times


#
# Various utilities to decode RPM
#############################################################
def flagToString(flags):
    ''' Convert numerical flags to strings

    :param flags: the numerical value of the flag
    :returns: the string value of the flag'''
    if flags is None or (type(flags) == str and len(flags) == 0):
        return None

    flags = flags & 0xf
    if flags == 0:
        return None
    elif flags == 2:
        return 'LT'
    elif flags == 4:
        return 'GT'
    elif flags == 8:
        return 'EQ'
    elif flags == 10:
        return 'LE'
    elif flags == 12:
        return 'GE'
    return flags


def relocate(filename, prefixmap):
    ''' Relocate the filename according to the map

    :param filename: the file path that needs to be relocated
    :param prefixmap: the relocation map

    :returns: the relocated file path'''
    if filename.startswith("./"):
        filename = filename.replace("./", "/")
    for k in prefixmap.keys():
        if filename.startswith(k):
            return filename.replace(k, prefixmap[k])
    return filename


#
# The package manager itself
#############################################################
class PackageManager(object):
    '''
    Class allowing to open a RPM file and extract information
    and files from it.

    :param filename: the name of the rpm
    :param sitroot: the installation area root directory
    :param relocatemap: the relocation map
    :param no_rpm_task: flag to avoid opening a rpm headers
    :param tmp_dir: custom temparary directory
    '''

    def __init__(self, filename, siteroot, relocatemap=None,
                 no_rpm_tasks=False, tmp_dir=None):
        '''
        Initialization for the package manager
        '''

        self.PGPHASHALGO = {
            1: hashlib.md5,
            2: None,  # unimplemented
            3: None,  # unimplemented
            5: None,  # unimplemented
            6: None,  # unimplemented
            7: None,  # unimplemented
            8: hashlib.sha256,
            9: hashlib.sha384,
            10: hashlib.sha512
        }

        self.log = logging.getLogger(__name__)
        self._filename = filename
        if not no_rpm_tasks:
            with rpmfile.open(self._filename) as f:
                self._headers = f.headers
        self.siteroot = siteroot
        if relocatemap is None:
            # Just remove the "./" prefix in this case
            relocatemap = {"./": "/"}
        self._relocatemap = relocatemap
        self._topdir = None
        self._filenames = None
        if tmp_dir:
            self._tmp_dir = tmp_dir
        else:
            self._tmp_dir = "%s/tmp" % siteroot
        if filename:
            self.package_tmp_folder = tempfile.mkdtemp(
                prefix=self.getName(), dir=self._tmp_dir)
        self.files_to_rollback = {
            'dirs': [],
            'links': [],
            'files': [],
        }

    def setrelocatemap(self, m):
        """
        Sets the relocation map

        :param m: the map that needs to be set
        """
        self._relocatemap = m

    def getGroup(self):
        """
        Gets the group of the package

        :return: the group of the package from the header
        """
        return self._headers["group"]

    def _getProvides(self):
        # The flags don't seem to come a a list when only one is specified
        # making sure it's the case before calling zip
        flags = self._headers["provideflags"]

        if not isinstance(flags, (list, tuple)):
            flags = [flags]

        l = [self._headers["providename"],
             self._headers["provideversion"],
             list(map(flagToString, flags))]
        return list(zip(*l))

    def getProvides(self):
        """
        Gets the list of providers

        :return: the list of providers
        """
        l = self._getProvides()
        provs = []
        for n, v, f in l:
            provs.append(Provides(n, v, None, None, f, None))
        return provs

    def _getRequires(self):
        l = [self._headers["requirename"],
             self._headers["requireversion"],
             list(map(flagToString, self._headers["requireflags"]))]
        return list(zip(*l))

    def getRequires(self):
        """
        Gets the list of requires

        :return: the list of requires
        """
        l = self._getRequires()
        reqs = []
        for n, v, f in l:
            reqs.append(Requires(n, v, None, None, f, None))
        return reqs

    def getPackage(self):
        ''' Returns the Package metadata in
        lbinstall.DependencyManager format

        :returns the package object
        '''
        p = Package(self.getName(),
                    self.getVersion(),
                    self.getRelease(),
                    None, None, self.getGroup(),
                    self.getArch(),
                    self.getTopDir(),
                    self.getProvides(),
                    self.getRequires(),
                    self.relocate(self.getTopDir()))
        return p

    def getPrefixes(self):
        """
        Returns the prefixes from the header

        :return: the list of prefixes from the header
        """
        return [str(x) for x in self._headers["prefixes"]]

    def getInstallPrefix(self):
        """ Return the proper relocation
        prefix in case several are specified

        :returns: the relocated prefix"""
        topDir = self.getTopDir()
        prefixes = [p for p in self.getPrefixes() if p in topDir]
        if len(prefixes) == 0:
            return None
        else:
            return relocate(prefixes[0], self._relocatemap)

    def getName(self):
        """
        Gets the package name from the header

        :return: the package name
        """
        return self._headers["name"]

    def getVersion(self):
        """
        Gets the package version from the header

        :return: the package version
        """
        return self._headers["version"]

    def getRelease(self):
        """
        Gets the package release from the header

        :return: the packae release"""
        return self._headers["release"]

    def getFullName(self):
        """
        Gets the package full name

        :return: the package full name
        """
        return "%s-%s-%s" % (self.getName(), self.getVersion(),
                             self.getRelease())

    def getMD5Checksum(self):
        """
        Gets the package checksum from the header

        :return: the package checksum"""
        return self._headers["md5"]

    def getSize(self):
        """
        Gets the package size from the header

        :return: the package size"""
        return self._headers["size"]

    def getArch(self):
        """
        Gets the package architecture from the header

        :return: the package architecture"""
        return self._headers["arch"]

    def getRPMVersion(self):
        """
        Gets the package rpm version from the header

        :return: the package rpm version"""
        return self._headers["rpmversion"]

    def getTopDir(self):
        """
        Gets the package top directory

        :return: the package top directory"""
        if self._topdir is None:
            with rpmfile.open(self._filename) as rpm:
                self._topdir = os.path.commonprefix([m.name
                                                     for m
                                                     in rpm.getmembers()])
        return self._topdir

    def create_folder_tree_with_permission(self, target, filename):
        """
        Creates the tree for a give target and adds the right permissions

        :param target: the destination folder path
        :param filename: the filename that needs to be moved
        """
        if not os.path.exists(os.path.dirname(target)):
            # We need to go step by step in the tree to keep the same
            # permissions. If os.amkedirs(target) is used, we cannot
            # recreate the permissions of partens folders

            # Get the relative folder path starting from siteroot
            tmp_folders = os.path.dirname(filename).replace(self.siteroot,
                                                            "")
            # Get the path tree from the relative path
            tmp_folders = tmp_folders.split('/')
            # Keep track of original visited folders
            tmp_path_origin = self.siteroot
            # Keep track of the dest visited folders
            tmp_path_dest = self.package_tmp_folder
            for folder in tmp_folders:
                if folder == "":
                    continue
                # Add the new subfolder to visited original path
                tmp_path_origin = "%s/%s" % (tmp_path_origin, folder)
                # Add the new subfolder to visited dest path
                tmp_path_dest = "%s/%s" % (tmp_path_dest, folder)
                # Do nothing if the path exists
                if os.path.exists(tmp_path_dest):
                    continue
                # If not, create the dest subfolder and keep the original
                # permissions
                s = os.stat(tmp_path_origin)
                mode = s[stat.ST_MODE]
                os.makedirs(tmp_path_dest)
                os.chmod(tmp_path_dest, mode)

    def backupFile(self, filename, type_f, overwrite):
        """
        Backups a given filename if overwrite option is active

        :param filename: the filename that needs to be backup
        :param type_f: the type of the filename (directory, link, file)
        :param overwrite: Flag to overwrite the existing files
        """
        # If the given filename path does not exists, do nothing
        if not os.path.exists(filename):
            return
        # If the overwrite flag is not True, do nothing
        if not overwrite:
            return
        # Get the relative name of the filename starting from siteroot
        name = filename.replace(self.siteroot, '')
        # Check if the tmp backup folder has been correctly created.
        # If not, create it.
        if not os.path.exists(self.package_tmp_folder):
            self.log.debug("Creating backup folder %s" %
                           self.package_tmp_folder)
            os.makedirs(self.package_tmp_folder)
        # The target filename is formed by the relative name and the tmp
        # backup folder
        target = "%s%s" % (self.package_tmp_folder, name)
        self.log.debug("Backup up %s to %s" % (filename, target))
        # Take special action based on the type of the filename
        if type_f == "dir":
            # Create the backup filename with the correct permissions
            s = os.stat(filename)
            mode = s[stat.ST_MODE]
            os.makedirs(target)
            os.chmod(target, mode)
        elif type_f == "link":
            # Read the destination of the link. Does not matter if the
            # path is relative and since it will be restored in the right
            # position
            linkto = os.readlink(filename)
            # Create the backup folder tree
            self.create_folder_tree_with_permission(target, filename)
            os.symlink(linkto, target)
        else:
            # Create the backup folder tree
            self.create_folder_tree_with_permission(target, filename)
            # Copy the file. copy2 will copy the correct permissions
            shutil.copy2(filename, target)

    def restoreFiles(self):
        """
        Restores all the backup files in case of failure and roll-back
        """
        # Walk through the backup folder tree
        for root, dirs, files in os.walk(self.package_tmp_folder,
                                         topdown=True):
            # At each level, first we deal with folders
            for name in dirs:
                # We need both the original name, from the backup
                full_name_origin = os.path.join(root, name)
                # and the destination folder name
                full_name_dest = full_name_origin.replace(
                    self.package_tmp_folder, self.siteroot)
                # if the folder exists, do nothing
                if not os.path.exists(full_name_dest):
                    # Create a directory with the same permissions as
                    # the one in the backup
                    self.log.debug("Restoring dir from backup %s" % (
                        full_name_dest))
                    os.makedirs(full_name_dest)
                    s = os.stat(full_name_origin)
                    mode = s[stat.ST_MODE]
                    os.chmod(full_name_dest, mode)
                else:
                    self.log.debug("No need to restore dir from backup %s" % (
                        full_name_dest))
            for name in files:
                # We need both the original name, from the backup
                full_name_origin = os.path.join(root, name)
                # and the destination folder name
                full_name_dest = full_name_origin.replace(
                    self.package_tmp_folder, self.siteroot)
                # if the file is a link
                if os.path.islink(full_name_origin):
                    if not os.path.exists(full_name_dest):
                        # Read the destination of the link. It will be
                        # restored in the right position
                        self.log.debug("Restoring link from backup %s" % (
                            full_name_dest))
                        linkto = os.readlink(full_name_origin)
                        os.symlink(linkto, full_name_dest)
                    else:
                        self.log.debug(
                            "No need to restore link from backup %s" % (
                                full_name_dest))
                else:
                    if not os.path.exists(full_name_dest):
                        self.log.debug("Restoring file from backup %s" % (
                            full_name_dest))
                        shutil.copy2(full_name_origin, full_name_dest)
                    else:
                        self.log.debug(
                            "No need to restore file from backup %s" % (
                                full_name_dest))

    def removeBackupFiles(self):
        """ Removes the backup files if the extract call succeed
        or if it failed, after the backup was restored
        """
        # Simply removed the temporary backup folder for this extraction
        shutil.rmtree(self.package_tmp_folder)

    def extract(self, prefixmap=None, overwrite=False):
        ''' Extract the files using the relocation specified
        in the prefix maps

        :param prefixmap: the relocation map
        :param overwrite: Flag to overwrite the existing files

        '''
        if prefixmap is None:
            prefixmap = self._relocatemap

        with rpmfile.open(self._filename) as rpm:
            for m in rpm.getmembers():
                if prefixmap is None:
                    # Just fix the "./" in that case
                    target = m.name.replace("./", "/")
                else:
                    target = relocate(m.name, prefixmap)
                # Create directories as needed
                attrs = m._attrs
                if not os.path.exists(target) or overwrite:
                    # Only overwite if requested
                    if attrs["isDir"]:
                        # Forgot about overwrite for directories,
                        # We may have different packages in the same
                        # directories
                        if overwrite and os.path.exists(target):
                            continue
                        self.backupFile(target, 'dir', overwrite)
                        try:
                            self.log.debug("Creating dir %s" % target)
                            os.makedirs(target)
                            os.chmod(target, attrs["mode"])
                            self.files_to_rollback['dirs'].append(target)
                        except Exception as e:
                            self.removeFiles()
                            self.removeBackupFiles()
                            raise e
                    elif attrs["isLink"]:
                        fin = rpm.extractfile(m.name)
                        lnktgt = fin.read()
                        if not os.path.exists(os.path.dirname(target)):
                            os.makedirs(os.path.dirname(target))
                        self.log.debug("We have a link %s to: %s"
                                       % (target, lnktgt))
                        self.backupFile(target, 'link', overwrite)
                        try:
                            os.symlink(lnktgt, target)
                            self.files_to_rollback['links'].append(target)
                        except:
                            if overwrite:
                                try:
                                    os.unlink(target)
                                    os.symlink(lnktgt, target)
                                    self.files_to_rollback['links'].append(
                                        target)
                                except Exception as e:
                                    self.removeFiles()
                                    self.removeBackupFiles()
                                    raise e
                            else:
                                self.removeFiles()
                                self.removeBackupFiles()
                                raise Exception("File %s already exists.If you"
                                                " want to overwrite please use"
                                                " --overwrite flag" % target)
                        # os.lchmod(target, attrs["mode"])
                    else:
                        self.backupFile(target, 'file', overwrite)
                        if not os.path.exists(os.path.dirname(target)):
                            if not os.path.exists(target):
                                os.makedirs(os.path.dirname(target))
                        self.log.debug("Relocating %s to %s"
                                       % (m.name, target))
                        fin = rpm.extractfile(m.name)
                        with open(target, "w+b") as fout:
                            fout.write(fin.read())
                        os.chmod(target, attrs["mode"])
                        self.files_to_rollback['files'].append(target)
                elif not os.path.exists(target) and not overwrite:
                    self.removeFiles()
                    self.removeBackupFiles()
                    raise Exception("File %s already exists. If you want to"
                                    " overwrite please use --overwrite flag" %
                                    target)
        self.removeBackupFiles()

    def getCpioFileSizes(self):
        '''
        Get the file sies from the CPIO archive instead of headers

        :returns: the file sizes
        '''
        filesizes = []
        with rpmfile.open(self._filename) as rpm:
            for m in rpm.getmembers():
                filesizes.append(m.size)
        return filesizes

    def relocate(self, path):
        ''' Useful util if the PM is initialized with the
        proper relocation map

        :param path: the initial path
        :returns: the reolcated path
        '''
        return relocate(path, self._relocatemap)

    def checkFileSizesOnDisk(self):
        '''
        Compare the filesizes on disk with the RPM metadata
        '''
        mdata = self.getFileMetadata()
        for (fname, isdir, md5, s) in mdata:
            # print("\nFname:%s " % fname)
            # print(md5)
            if isdir:
                continue
            name = self.relocate(fname)
            # print("Full name: %s\n Link: %s" % (name, os.path.islink(name)))
            # lstat as we do not want to check symlinks
            statres = os.lstat(name)

            if s != statres[stat.ST_SIZE]:
                raise Exception("%s: Mismatch in filesize vs metadata:"
                                " %s vs %s" % (name, statres[stat.ST_SIZE], s))
            if not os.path.islink(name):
                check_sum = self.check_sum(name, int(self._headers.get(
                    'fieldsdigetsalgo', '1')))
                # print(check_sum)
                if check_sum and md5 and md5 != check_sum:
                    raise Exception("%s: Mismatch in checksum vs metadata:"
                                    " %s vs %s" % (name, check_sum, md5))
            self.log.debug("File %s metadata:%s real:%s"
                           % (name, s,  statres[stat.ST_SIZE]))

    def removeFiles(self):
        ''' Cleanup the files already installed '''

        self.log.error("Error installing files, rolling back")
        # First removing the files
        for name in self.files_to_rollback['files']:
            try:
                os.unlink(name)
                self.log.warning("Removed %s" % name)
            except:
                self.log.warning("Could not remove %s" % name)
        # Second removing the Links
        for name in self.files_to_rollback['links']:
            try:
                os.unlink(name)
                self.log.warning("Removed %s" % name)
            except:
                self.log.warning("Could not remove %s" % name)
        # Last remove the dirs
        for name in self.files_to_rollback['dirs']:
            try:
                os.rmdir(name)
                self.log.warning("Removed %s" % name)
            except:
                self.log.warning("Could not remove %s" % name)
        # Restore the backup
        self.restoreFiles()

    def getFileNames(self):
        """
        Gets the rpm payload filenames
        :return: list of filenames
        """
        if self._filenames is None:
            ret = []
            with rpmfile.open(self._filename) as rpm:
                for m in rpm.getmembers():
                    ret.append((m.name, m.isdir))
            self._filenames = ret
        return self._filenames

    def getFileMetadata(self):
        '''
        Return a list with the needed info about the files in the RPM,
        i.e. a tuple with (filename, bool(isdir), filemd5, filesize

        :returns: list of tuples ( filename, is directory, checksum and size)
        '''
        tmp = list(zip(*self.getFileNames()))
        try:
            tmp.append(self._headers['filemd5s'])
        except:
            tmp.append([])
        tmp.append(self.getCpioFileSizes())
        return list(zip(*tmp))

    def getRelocatedFileMetadata(self):

        ''' Return a list with the needed infor about the files in the RPM,
        i.e. a tuple with (filename, bool(isdir), filemd5, filesize

        :returns: list of tuples ( filename, is directory, checksum and size)
        '''

        tmp = []
        for (name, ftype, md5, size) in self.getFileMetadata():
            fname = self.relocate(name).replace(self.siteroot, '')
            tmp.append((fname, ftype, md5, size))
        return tmp

    def getPostInstallScript(self):
        '''
        returns a string with the content of the post install script

        :returns: the postinstall script
        '''
        return self._headers.get("postin")

    def check_sum(self, fname, encription_algorithm):
        """
        Computes a file check sum

        :param fname: the file that needs checksum computation
        :param encription_algorithm: the type of algorithm used
        :return: the value of the checksum
        """
        if self.PGPHASHALGO.get(encription_algorithm, None):
            check_sum_hash = self.PGPHASHALGO[encription_algorithm]()
        else:
            return None

        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                check_sum_hash.update(chunk)
        return check_sum_hash.hexdigest()
