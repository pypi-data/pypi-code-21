from .version import Version


class FolderVersionCreator():
    """
    utility class that allows to create quickly `Version` object from  SQL file
    in a folder
    """

    def __init__(self, path_prefix):
        """
        Create an instant.

        :param path_prefix: the folder path. "/" should NOT be at the end.
        """
        if path_prefix[-1] == '/':
            raise Exception("please do not put / at the end of path prefix")

        self.path_prefix = path_prefix

    def create_version(self, version_code, version_file, version_comment,
                       before_migrate=None, after_migrate=None):
        return Version(
            version_code, version_comment,
            sql_file=f"{self.path_prefix}/{version_file}",
            before_migrate=before_migrate,
            after_migrate=after_migrate
        )
