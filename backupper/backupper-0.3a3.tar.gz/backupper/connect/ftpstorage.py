import os
from ftplib import FTP

from .utils import *

_all_ = ["FTPStorage"]

class FTPStorage(AbstractStorageContext):
    """
        FTP storage system.

        A handy wrapper for ftplib.FTP methods.
    """

    CONNEXION_TYPE = "ftp"

    def __init__(self, host, user="anonymous", passwd=""):
        if not host:
            raise ValueError("__init__: please provide a host.")
        self.host = host
        self.user = user
        self.passwd = passwd
        self._connection = None

    def connect(self):
        if not self._connection is None:
            raise AlreadyConnectedError("connect: you're already connected to {}.".format(self._connection.host)) # We use self._connection.host because the user could modify the host after the connection was opened

        try:
            self._connection = FTP(host=self.host)
            self._connection.login(user=self.user, passwd=self.passwd)
        except Exception as e:
            if not self._connection is None:
                self._connection.close()
            raise UnableToConnectError("connect: FTP module returned an error ({}).".format(e))

    def disconnect(self):
        if self._connection is None:
            raise NotConnectedError("disconnect: you're not connected to {}.".format(self.host))

        try:
            self._connection.quit()
        except:
            self._connection.close()
        finally:
            self._connection = None

    def upload(self, src, dest="."):
        if self._connection is None:
            raise NotConnectedError("upload: you're not connected to {}.".format(self.host))

        dest_filename = ""

        try:
            dest_files = self.listdir(dest)

            if not self.isdir(dest):
                raise UnpermittedOperationError("upload: {} is a file.".format(dest))

            if os.path.basename(src) in dest_files:
                raise UnpermittedOperationError("upload: {} already exists.".format(src))

            dest_filename = os.path.basename(src)
        except NotFoundError as e:
            try:
                dest, dest_filename = os.path.split(dest)

                self.listdir(dest)

                if not self.isdir(dest):
                    raise UnpermittedOperationError("upload: {} is a file.".format(os.path.normpath(dest)))
            except NotFoundError:
                raise NotFoundError("upload: {} doesn't exist.".format(os.path.normpath(os.path.dirname(dest))))

        if not os.path.exists(src):
            raise NotFoundError("upload: {} doesn't exist.".format(src))

        try:
            if os.path.isdir(src):
                full_dest = os.path.join(dest, dest_filename)
                self._connection.mkd(full_dest)
                self._recursive_upload(src, full_dest)
            else:
                with open(src, "rb") as f:
                    self._connection.storbinary('STOR {}'.format(os.path.join(dest, dest_filename)), f)
        except Exception as e:
            raise StorageError("upload: FTP module returned an error ({}).".format(e))

    def _recursive_upload(self, current_file, dest):
        """
            Internal recursive upload subroutine.

            When uploading a directory, recursively creates its structure.

            :param current_file: The directory to upload.
            :type current_file: str
            :param dest: Destination.
            :type dest: str
        """
        files = os.listdir(current_file)
        for f in files:
            subfile = os.path.join(current_file, f)
            next_dest = os.path.join(dest, f)
            if os.path.isdir(subfile):
                self._connection.mkd(next_dest)
                self._recursive_upload(subfile, next_dest)
            else:
                with open(subfile, 'rb') as fp:
                    self._connection.storbinary('STOR {}'.format(next_dest), fp)

    def download(self, src, dest="."):
        #TODO Implement me
        raise NotImplementedError("download: Method not implemented yet.")

        if self._connection is None:
            raise NotConnectedError("download: you're not connected to {}.".format(self.host))

        try:
            pass
        except Exception as e:
            raise StorageError("download: FTP module returned an error ({}).".format(e))

    def listdir(self, path="."):
        if self._connection is None:
            raise NotConnectedError("listdir: you're not connected to {}.".format(self.host))

        last_path = self.getcwd()
        abs_path = os.path.normpath(os.path.join(last_path, path))

        try:
            if not self.isdir(path):
                return [os.path.basename(path)]
            self.chdir(abs_path)
            result = [os.path.basename(f) for f in self._connection.nlst("-a") if not os.path.basename(f) in [".", "..", ""]]
            self.chdir(last_path)
            return result
        except NotFoundError as e:
            self.chdir(last_path)
            raise NotFoundError("listdir: FTP module returned an error ({}).".format(e))
        except Exception as e:
            self.chdir(last_path)
            raise StorageError("listdir: FTP module returned an error ({}).".format(e))

    def isdir(self, path):
        """
            Tests if the path is an existing directory.

            :param path: File to test.
            :type path: str
            :return: True if the path is a directory.
            :rtype: bool
        """

        if self._connection is None:
            raise NotConnectedError("isdir: you're not connected to {}.".format(self.host))

        basename, filename = os.path.split(os.path.normpath(os.path.join(self.getcwd(), path)))
        files = {}

        # Case where our canonical path is the root
        if filename == "":
            return True

        try:
            list_log = []
            old_cwd = self._connection.pwd()
            self._connection.cwd(basename)
            self._connection.dir("-a", list_log.append)
            self._connection.cwd(old_cwd)
            files = {' '.join(line.split()[8:]): line[0] for line in list_log}
        except Exception as e:
            raise StorageError("isdir: FTP module returned an error ({}).".format(e))

        if not filename in files:
            raise NotFoundError("isdir: {} doesn't exist.".format(path))

        return files[filename] == "d"

    def remove(self, path):
        if self._connection is None:
            raise NotConnectedError("remove: you're not connected to {}.".format(self.host))

        try:
            if self.isdir(path):
                # TODO We should recursively delete the contents of path before removing the directory, otherwise we get an error
                raise NotImplementedError("remove: Directory deletion isn't implemented yet.")
                self._connection.rmd(path)
            else:
                self._connection.delete(path)
        except Exception as e:
            raise StorageError("remove: FTP module returned an error ({}).".format(e))

    def _recursive_remove(self, current_file):
        """
            TODO IMPLEMENT ME
        """

    def mkdir(self, path):
        if self._connection is None:
            raise NotConnectedError("mkdir: you're not connected to {}.".format(self.host))

        try:
            self._connection.mkd(path)
        except Exception as e:
            raise StorageError("mkdir: FTP module returned an error ({}).".format(e))

    def rename(self, path, new_path):
        if self._connection is None:
            raise NotConnectedError("rename: you're not connected to {}.".format(self.host))

        try:
            self._connection.rename(path, new_path)
        except Exception as e:
            raise StorageError("rename: FTP module returned an error ({}).".format(e))

    def chdir(self, path="/"):
        if self._connection is None:
            raise NotConnectedError("chdir: you're not connected to {}.".format(self.host))

        try:
            self._connection.cwd(path)
        except Exception as e:
            raise NotFoundError("chdir: FTP module returned an error ({}).".format(e))

    def getcwd(self):
        if self._connection is None:
            raise NotConnectedError("getcwd: you're not connected to {}.".format(self.host))

        try:
            return self._connection.pwd()
        except Exception as e:
            raise StorageError("getcwd: FTP module returned an error ({}).".format(e))
