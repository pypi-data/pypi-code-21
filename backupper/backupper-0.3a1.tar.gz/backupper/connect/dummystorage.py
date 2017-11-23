import os

from .utils import *

_all_ = ["DummyStorage"]

class DummyStorage(AbstractStorageContext):
    """
        Dummy storage system.

        Just a demo implementation of backupper.connect.AbstractStorageContext. It will only store a non-persistent tree.
    """

    CONNEXION_TYPE = "dummy"

    def __init__(self):
        self._tree = {}
        """Dummy file structure"""

        self._cwd = "/"
        """Dummy current working directory"""

        self._connected = False
        """True if connected"""

    def connect(self):
        # Does nothing else but toggling a boolean
        if not self._connected:
            self._connected = True
        else:
            raise AlreadyConnectedError("connect: Already connected.")

    def disconnect(self):
        # Does nothing else but toggling a boolean
        if self._connected:
            self._connected = False
            self._cwd = "/"
        else:
            raise NotConnectedError("disconnect: Not connected.")

    def upload(self, src, dest="."):
        if self._connected:
            # Try to retrieve the source
            if not os.path.exists(src):
                raise NotFoundError("upload: {} doesn't exist.".format(src))
            src = os.path.abspath(src)

            # Try to access the destination
            dest_tree = {}
            dest_filename = ""
            # dest exists?
            try:
                # If so,
                dest_tree = self._walk(dest)
                # ...Is it a file? If yes, we raise an exception because we can't copy a tree in a file.
                if not isinstance(dest_tree, dict):
                    raise UnpermittedOperationError("upload: {} is a file.".format(dest))
                # ...Otherwise dest/basename(src) exists?
                if os.path.basename(src) in dest_tree:
                    # If so we raise an error
                    raise UnpermittedOperationError("upload: {} already exists.".format(src))
                else:
                    # Otherwise that's ok
                    dest_filename = os.path.basename(src)
            except NotFoundError:
                # Otherwise, dirname(dest) exists?
                try:
                    # If so...
                    dest_tree = self._walk(os.path.dirname(dest))
                    # ...Is it a file? If yes, we raise an exception because we can't copy a tree in a file.
                    if not isinstance(dest_tree, dict):
                        raise UnpermittedOperationError("upload: {} is a file.".format(os.path.normpath(os.path.dirname(dest))))
                    # ...Otherwise that's ok
                    dest_filename = os.path.basename(dest)
                except NotFoundError:
                    # Otherwise, it's an error
                    raise NotFoundError("upload: {} doesn't exist.".format(os.path.normpath(os.path.dirname(dest))))

            # We create the according root node
            if os.path.isdir(src):
                dest_tree[dest_filename] = {}
                self._recursive_upload(src, dest_tree[dest_filename])
            else:
                with open(src, "rb") as f:
                    dest_tree[dest_filename] = f.read()
        else:
            raise NotConnectedError("upload: Not connected.")

    def _recursive_upload(self, current_file, dest_tree):
        """
            Internal recursive upload subroutine.

            When uploading a directory, recursively creates its structure.

            :param current_file: The directory to upload.
            :type current_file: str
            :param dest_tree: Tree for the destination.
            :type dest_tree: dict
        """
        for item in [os.path.join(current_file, f) for f in os.listdir(current_file)]:
            dest_filename = os.path.basename(item)
            if os.path.isdir(item):
                dest_tree[dest_filename] = {}
                self._recursive_upload(item, dest_tree[dest_filename])
            else:
                with open(item, "rb") as f:
                    dest_tree[dest_filename] = f.read()

    def download(self, src, dest="."):
        if self._connected:
            # Try to retrieve the source
            try:
                file_to_download = self._walk(src)
                canonical_dest = os.path.abspath(dest)

                # If the destination is an existing directory, and if we're going to download a directory, we append the destination filename to the canonical destination
                if os.path.isdir(canonical_dest) and isinstance(file_to_download, dict):
                    canonical_dest = os.path.join(canonical_dest, os.path.basename(src))
                    dest = os.path.join(dest, os.path.basename(src))

                # If the destination is an existing file, we raise an exception (otherwise we would override it)
                if os.path.isfile(canonical_dest):
                    raise UnpermittedOperationError("download: {} already exists.".format(dest))

                # We package the file to download in a super dict, otherwise we create the base file
                if not isinstance(file_to_download, dict):
                    file_to_download = {os.path.basename(src): file_to_download}
                else:
                    try:
                        os.mkdir(canonical_dest)
                    except FileExistsError:
                        pass

                self._recursive_download(file_to_download, canonical_dest)
            except NotFoundError:
                raise NotFoundError("download: {} doesn't exist.".format(src))

        else:
            raise NotConnectedError("download: Not connected.")

    def _recursive_download(self, source_tree, canonical_dest):
        """
            Internal recursive download subroutine.

            When downloading a directory, recursively creates its structure.

            :param source_tree: The tree to download.
            :type source_tree: dict
            :param canonical_dest: Absolute path for the destination.
            :type canonical_dest: str
        """

        for item in source_tree:
            if isinstance(source_tree[item], dict):
                next_canonical_dest = os.path.join(canonical_dest, item)
                os.mkdir(next_canonical_dest)
                self._recursive_download(source_tree[item], next_canonical_dest)
            else:
                opening_mode = "x"
                if not isinstance(source_tree[item], str):
                    opening_mode+= "b"
                with open(os.path.join(canonical_dest, item), opening_mode) as f:
                    f.write(source_tree[item])

    def listdir(self, path="."):
        if self._connected:
            # Try to walk to the target directory
            try:
                result = self._walk(path)

                # If the target was a file we raise an exception
                if isinstance(result, dict):
                    return list(result.keys())
                else:
                    raise UnpermittedOperationError("listdir: {} isn't a directory.".format(path))
            except NotFoundError:
                raise NotFoundError("listdir: {} doesn't exist".format(path))
        else:
            raise NotConnectedError("listdir: Not connected.")


    def remove(self, path):
        if self._connected:
            basefile, to_remove = os.path.split(os.path.normpath(os.path.join(self._cwd, path)))

            # Try to walk to the base directory
            try:
                base = self._walk(basefile)

                # If the target resource doesn't exist we raise an exception
                if not to_remove in base:
                    raise NotFoundError("remove: {} doesn't exist.".format(path))

                del base[to_remove]
            except NotFoundError:
                raise NotFoundError("remove: {} doesn't exist".format(basefile))
        else:
            raise NotConnectedError("remove: Not connected.")

    def mkdir(self, path):
        if self._connected:
            basefile, new_dir = os.path.split(os.path.normpath(os.path.join(self._cwd, path)))

            # Try to walk to the base directory
            try:
                base = self._walk(basefile)

                # If the basefile is a regular file we raise an exception
                if not isinstance(base, dict):
                    raise UnpermittedOperationError("mkdir: {} is a file.".format(basefile))

                # If the target directory already exists we raise an exception
                if new_dir in base:
                    raise UnpermittedOperationError("mkdir: {} already exists.".format(path))

                # A dict is mutable so self._walk returns a reference we can directly modify
                base[new_dir] = {}
            except NotFoundError:
                raise NotFoundError("mkdir: {} doesn't exist.".format(basefile))
        else:
            raise NotConnectedError("mkdir: Not connected.")

    def rename(self, path, new_path):
        if self._connected:
            canonical_path = os.path.normpath(os.path.join(self._cwd, path))
            basefile, old_file = os.path.split(canonical_path)

            # Try to walk to the old base directory
            base = {}
            try:
                base = self._walk(basefile)
            except NotFoundError:
                raise NotFoundError("rename: {} doesn't exist.".format(basefile))

            # If the old file doesn't exist, we raise an exception
            if not old_file in base:
                raise NotFoundError("rename: {} doesn't exist.".format(path))

            # Try to walk to the new base directory
            new_canonical_path = os.path.normpath(os.path.join(self._cwd, new_path))
            new_basefile, new_name = os.path.split(new_canonical_path)
            try:
                new_base = self._walk(new_basefile)

                # If the new basefile is a regular file we raise an exception
                if not isinstance(new_base, dict):
                    raise UnpermittedOperationError("rename: {} is a file.".format(new_basefile))

                # If the destination is in the source, we raise an exception (you can't copy a directory in itself)
                if os.path.basename(os.path.commonpath([canonical_path, new_canonical_path])) == os.path.basename(canonical_path):
                    raise UnpermittedOperationError("rename: can't rename {} into itself.".format(path))

                # If the new file name already exists, we raise an exception
                if new_name in new_base:
                    raise UnpermittedOperationError("rename: {} already exists.".format(new_path))


                new_base[new_name] = base.pop(old_file)
            except NotFoundError:
                raise NotFoundError("rename:  {} doesn't exist.".format(new_basefile))
        else:
            raise NotConnectedError("rename: Not connected.")

    def chdir(self, path="/"):
        if self._connected:
            # Try to walk to the target directory
            try:
                # If the target is a file, we raise an exception
                if not isinstance(self._walk(path), dict):
                    raise UnpermittedOperationError("chdir: {} isn't a directory.".format(path))
            except NotFoundError:
                raise NotFoundError("chdir: {} doesn't exist.".format(path))

            # Set the new path
            new_path = os.path.normpath(os.path.join(self._cwd, path))
            self._cwd = new_path
        else:
            raise NotConnectedError("chdir: Not connected.")

    def getcwd(self):
        if self._connected:
            return self._cwd
        else:
            raise NotConnectedError("getcwd: Not connected.")

    def _walk(self, path):
        """
            Walks into the tree and returns the reached level.

            :param path: Absolute or relative path.
            :type path: str
            :return: The last level reached (a dictionary if it's a directory, a string if it's a file).
            :rtype: dict or str

            :raises: backupper.connect.utils.NotFoundError
        """

        # Absolute path
        canonical_path = os.path.normpath(os.path.join(self._cwd, path))

        splitted_path = []

        # Split the path from the end to the beginning (splitted_path is reversed)
        while canonical_path != "/":
            canonical_path, tail = os.path.split(canonical_path)
            splitted_path.append(tail)

        subtree = self._tree

        # Try to go to the target level
        for element in reversed(splitted_path):
            # If the element isn't in the subtree, we raise an exception
            if element in subtree:
                subtree = subtree[element]
            else:
                raise NotFoundError("_walk: {} doesn't exist.".format(path))

        return subtree
