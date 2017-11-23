"""
    Provides an abstraction layer to open a connection to various storage systems.
"""

from abc import ABC, abstractmethod

__all__ = ["StorageError", "AlreadyConnectedError", "NotConnectedError", "UnableToConnectError", "NotFoundError", "UnpermittedOperationError", "AbstractStorageContext"]

class StorageError(Exception):
    """
        Generic storage error (all errors defined below inherit from this exception).
    """

class AlreadyConnectedError(StorageError):
    """
        Raised if you try to open a connection while it's already established.
    """

class NotConnectedError(StorageError):
    """
        Raised if you try to perform an operation while the connection hasn't been established.
    """

class UnableToConnectError(StorageError):
    """
        Raised if the connection wasn't successfully established.
    """

class NotFoundError(StorageError):
    """
        Raised if a file or directory doesn't exist in the storage.
    """

class UnpermittedOperationError(StorageError):
    """
        Raised if trying to perform an unpermitted operation (chdir to a file for instance).
    """

class AbstractStorageContext(ABC):
    """
        Abstract connection model.

        This class provides a common context for a connection to a distant storage. Implementation is left to child classes.
    """

    CONNEXION_TYPE = "unknown"
    """Type of storage (may be FTP, SFTP, S3, etc.). A subclass should always redefine this class attribute."""

    def __init__(self):
        pass

    @abstractmethod
    def connect(self):
        """
            Opens a connection with the storage.
        """

    @abstractmethod
    def disconnect(self):
        """
            Closes the connection with the storage.
        """

    @abstractmethod
    def upload(self, src, dest="."):
        """
            Uploads a file to the storage.

            :param src: Local path of the file or directory to upload.
            :type src: str
            :param dest: Distant destination path.
            :type dest: str
        """

    @abstractmethod
    def download(self, src, dest="."):
        """
            Retrieves a file from the storage.

            :param src: Distant path of the file or directory to retrieve.
            :type src: str
            :param dest: Local destination path.
            :type dest: str
        """

    @abstractmethod
    def listdir(self, path="."):
        """
            Lists the contents of the storage.

            :param path: resource to list.
            :type path: str
            :return: a list of contents.
            :rtype: list
        """

    @abstractmethod
    def remove(self, path):
        """
            Removes a file or directory from the storage.

            :param path: Resource to remove.
            :type path: str
        """

    @abstractmethod
    def mkdir(self, path):
        """
            Creates a directory on the storage.

            :param path: Directory to create.
            :type path: str
        """

    @abstractmethod
    def rename(self, path, new_path):
        """
            Moves a directory or file in the storage. It can be used to rename a resource.

            :param path: Resource to rename.
            :type path: str
            :param new_path: New name of the resource.
            :type new_path: str
        """

    @abstractmethod
    def chdir(self, path="/"):
        """
            Changes the storage working directory.

            :param path: New distant working directory.
            :type path: str
        """

    @abstractmethod
    def getcwd(self):
        """
            Returns the storage working directory.

            :return: Current distant working directory.
            :rtype: str
        """

    @classmethod
    def storage_methods(cls):
        """
            Retrieves a dictionary of storage methods indexed by their CONNEXION_TYPE class attribute.

            If you call this method from the base abstract class AbstractStorageMethod, you will get direct inherited classes. If a given storage method has other inherited classes (who knows?), you could retrieve them by calling this method from the storage method class.

            :return: CONNEXION_TYPE: corresponding_class storage methods.
            :rtype: dict
        """
        return {f.CONNEXION_TYPE: f for f in cls.__subclasses__()}
