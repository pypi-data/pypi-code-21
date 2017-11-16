"""
Python Profiler Util
"""
import cProfile
import pstats
import io


class Profiler:
    """
    Basic Profiler helper class
    """
    def __init__(self) -> None:
        self._pr = cProfile.Profile()
        self._sortby = 'cumulative'

    def start(self):
        """
        Start profiling
        :return:
        """
        self._pr.enable()

    def stop(self):
        """
        stop profiling, need to use with start
        :return:
        """
        self._pr.disable()

    def print(self):
        """
        Get profile result as string
        :return:
        """
        string_io = io.StringIO()
        pstats.Stats(self._pr, stream=string_io).sort_stats(self._sortby).print_stats()
        return string_io.getvalue()

    def dump(self, filename):
        """
        Dump profile to file
        :param filename:
        :return:
        """
        pstats.Stats(self._pr).sort_stats(self._sortby).dump_stats(filename)
