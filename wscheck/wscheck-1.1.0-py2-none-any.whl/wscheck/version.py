__version__ = (1, 1, 0)


class Version:
    def __init__(self):
        version_string_array = [str(v) for v in __version__]
        self.__version = '.'.join(version_string_array[:3])
        self.__release = '-'.join([self.__version] + version_string_array[3:])

    @property
    def version_array(self):
        """
        :rtype: tuple
        """
        return __version__

    @property
    def version(self):
        """
        :rtype: str
        """
        return self.__version

    @property
    def release(self):
        """
        :rtype: str
        """
        return self.__release
