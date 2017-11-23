from dataclay.api import get_objects_locations

__authors__ = ['Daniel Gasull <daniel.gasull@bsc.es>',
               'Alex Barcelo <alex.barcelo@bsc.es']
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class DataClayLocalIterator(object):
    """Trivial implementation of local iterators."""
    def __init__(self, local_chunks):
        self._started = False
        self._chunks_to_iterate = local_chunks
        self._current_chunk = 0
        self._chunk_iteration = iter(local_chunks[0][1])

    def next(self):
        """
        Not doing a itertools.chain because Python iterators are not easily made persistent
        :return:
        """
        # Maybe we finished long ago
        if self._current_chunk >= len(self._chunks_to_iterate):
            raise StopIteration

        try:
            # Maybe we can safely do a next
            return self._chunk_iteration.next()
        except StopIteration:
            # no, we can't: we finished the chunk
            self._current_chunk += 1
            if self._current_chunk >= len(self._chunks_to_iterate):
                # Finished iteration
                raise StopIteration
            else:
                self._chunk_iteration = iter(
                    self._chunks_to_iterate[self._current_chunk][1])
                return self._chunk_iteration.next()


class DataClayArray(object):
    """
    @dclayProperty sizes anything
    @dclayProperty chunks list<>
    @dclayProperty local_iterators dict<>
    """
    def __init__(self, max_chunk_size, default_value, sizes):
        """
        @dclayMethodParameter max_chunk_size int
        @dclayMethodParameter default_value anything
        @dclayMethodParameter sizes anything
        @dclayMethodReturn None
        """
        self.chunks = list()
        self.local_iterators = dict()

    def __getitem__(self, item):
        """
        @dclayMethodReturn
        """
        pass

    def __setitem__(self, key, value):
        # do things
        # do more things
        pass

    def get_local_iterators(self):
        """Get the Local Iterators for this array instance.
        :return: An element for each DataService
        """
        locations = get_objects_locations(self.chunks)

        # Process them and do something
        return None
