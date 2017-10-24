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
Installer for the for LHCb Software.
All it needs is the name of a local directory to use to setup the install area
and the yum repository configuration.

:author: Stefan-Gabriel Chitic
'''

from lbinstall.PackageManager import PackageManager
import tarfile
import tempfile
import logging


class RpmTarTool(object):
    def __init__(self, tarFile, rpmFile):
        # Create a lbinstall package manager to deal with the rpm
        self.packageManager = PackageManager(rpmFile, None,
                                             tmp_dir=tempfile.gettempdir())
        self.rpmFile = rpmFile
        self.tarFile = tarFile
        # Open the tar file
        self.tarManager = tarfile.open(tarFile, 'r')
        self.log = logging.getLogger(__name__)

    def _getRpmFileListMetaInfo(self):
        to_return = {}
        # The root folders might be different in the tar file and in the rpm
        # so get the longest folder prefixes.
        root_folders = []
        # Futhuremore, the rpm has an install prefix that needs to be removed.
        prefix = self.packageManager.getInstallPrefix()
        for file in self.packageManager.getFileMetadata():
            start_string = file[0].index(prefix) + len(prefix)
            # Remove the install prefix from the filename
            filename_after_relocation = file[0][start_string:]
            # Update the longest common folder prefix
            tmp_root_folders = filename_after_relocation.split('/')
            index_root = 0
            if len(root_folders) == 0:
                root_folders = tmp_root_folders
            for folder in root_folders:
                if folder == tmp_root_folders[index_root]:
                    index_root += 1
                else:
                    break
            root_folders = root_folders[:index_root]
            # Update the rpm meta info dictionary
            to_return[filename_after_relocation] = {
                'is_dir': file[1],
                'checksum': file[2],
                'size': file[3]
            }
        self.rpm_root_folder = '/'.join(root_folders)
        return to_return

    def _getTarileListMetaInfo(self, ):
        members = self.tarManager.getmembers()
        to_return = {}
        # The root folders might be different in the tar file and in the rpm
        # so get the longest folder prefixes.
        root_folders = []
        for member in members:
            # Update the longest common folder prefix
            tmp_root_folders = member.name.split('/')
            index_root = 0
            if len(root_folders) == 0:
                root_folders = tmp_root_folders
            for folder in root_folders:
                if folder == tmp_root_folders[index_root]:
                    index_root += 1
                else:
                    break
            root_folders = root_folders[:index_root]
            to_return[member.name] = {
                'is_dir': member.type == tarfile.DIRTYPE,
                'checksum': member.chksum,
                'size': member.size
            }
        self.tar_root_folder = '/'.join(root_folders)
        return to_return

    def compare(self):
        rpm_meta_info = self._getRpmFileListMetaInfo()
        tar_meta_info = self._getTarileListMetaInfo()
        missing_files = {
            'tar': [],
            'rpm': []
        }
        size_mismatch = []
        dir_prop_mismatch = []
        check_sum_mismatch = []
        for file in rpm_meta_info.keys():
            # In order to compare the filenames in the rpm with those in tar,
            # we need to switch the longest common path from the rpm with the
            # one in the tar file
            file_without_root_folder = file.replace(self.rpm_root_folder,
                                                    self.tar_root_folder)
            if not tar_meta_info.get(file_without_root_folder, None):
                missing_files['tar'].append(file)
                continue
            rpm_file = rpm_meta_info[file]
            tar_file = tar_meta_info[file_without_root_folder]
            # Compare the size
            if rpm_file['size'] != tar_file['size']:
                size_mismatch.append(
                    {'file': file,
                     'tar_size': tar_file['size'],
                     'rpm_size': rpm_file['size']
                     }
                )
            # Compare the folder structure
            if rpm_file['is_dir'] != tar_file['is_dir']:
                dir_prop_mismatch.append(
                    {'file': file,
                     'tar_is_dir': tar_file['is_dir'],
                     'tar_is_dir': rpm_file['is_dir']
                     }
                )
            # Compare the checksum
            if rpm_file['checksum'] != tar_file['checksum']:
                check_sum_mismatch.append(
                    {'file': file,
                     'tar_checksum': tar_file['checksum'],
                     'rpm_checksum': rpm_file['checksum']
                     }
                )
        for file in tar_meta_info.keys():
            # In order to compare the filenames in the tar with those in rpm,
            # we need to switch the longest common path from the tar with the
            # one in the rpm file
            file_without_root_folder = file.replace(self.tar_root_folder,
                                                    self.rpm_root_folder)
            if not rpm_meta_info.get(file_without_root_folder, None):
                missing_files['rpm'].append(file_without_root_folder)
                continue
        self.missing_files = missing_files
        self.size_mismatch = size_mismatch
        self.dir_prop_mismatch = dir_prop_mismatch
        self.check_sum_mismatch = check_sum_mismatch
        self.display()

    def display(self):
        # Display the missing files
        if len(self.missing_files['tar']) or len(self.missing_files['rpm']):
            self.log.error("Missing files")
            self.log.error('==============')
            if len(self.missing_files['tar']):
                self.log.error('\tIn tar file:')
                for file in self.missing_files['tar']:
                    self.log.error('\t\t%s' % file)
            if len(self.missing_files['rpm']):
                self.log.error('\tIn rpm file:')
                for file in self.missing_files['rpm']:
                    self.log.error('\t\t%s' % file)
        # Display the mismatched files size
        if len(self.size_mismatch):
            self.log.error("Mismatch size")
            self.log.error('======================')
            for file in self.size_mismatch:
                self.log.error(
                    '\t%s has %s bytes in rpm and %s bytes in tar file' % (
                        file['file'], file['rpm_size'], file['tar_size']))
        # Display the mismatched folder structure
        if len(self.dir_prop_mismatch):
            self.log.error("Mismatch directory")
            self.log.error('======================')
            for file in self.dir_prop_mismatch:
                self.log.error('\t%s - %s in rpm and %s in tar file' % (
                    file['file'], file['tar_is_dir'], file['tar_is_dir']))
        # Display the mismatched files checksum
        # Will not work without extracting due to the different hashing
        # algoritm
        """
        if len(self.check_sum_mismatch):
            self.log.error("Mismatch checksum")
            self.log.error('======================')
            for file in self.check_sum_mismatch:
                self.log.error('\t%s - %s in rpm and %s in tar file' % (
                    file['file'], file['rpm_checksum'], file['tar_checksum']))
        """
