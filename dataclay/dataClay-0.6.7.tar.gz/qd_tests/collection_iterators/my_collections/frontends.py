__authors__ = ['Daniel Gasull <daniel.gasull@bsc.es>',
               'Alex Barcelo <alex.barcelo@bsc.es']
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class DataClayChunk(object):
    """A Chunk is the elemental thingy holding data (in the dataClay collections).

    @dclayProperty revision int
    @dclayProperty container_wrapper list<>
    @dclayProperty prev_chunk DataClayChunk
    @dclayProperty next_chunk DataClayChunk
    @dclayProperty max_num_elements int
    """
    def __init__(self, element_type, max_chunk_size):
        """Initialization of chunk
        @dclayMethodParameter element_type int
        @dclayMethodParameter max_chunk_size int
        @dclayMethodReturn None
        """
        self.max_num_elements = max_chunk_size
        self.revision = 0
        self.prev_chunk = None
        self.next_chunk = None
        self.container_wrapper = [None] * max_chunk_size

    def set_element(self, index, elem):
        """
        @dclayMethodParameter index index
        @dclayMethodParameter elem anything
        @dclayMethodReturn None
        """
        self.container_wrapper[index] = elem

    def get_element(self, index):
        """
        @dclayMethodParameter index int
        @dclayMethodReturn anything
        @dclayMethodReadOnly
        """
        return self.container_wrapper[index]

    def get_chunk(self):
        """
        @dclayMethodReturn list<>
        @dclayMethodReadOnly
        """
        return self.container_wrapper

    def update_revision(self):
        """
        @dclayMethodReturn None
        """
        self.revision += 1

    def get_revision(self):
        """
        @dclayMethodReturn int
        @dclayMethodReadOnly
        """
        return self.revision

    def get_cur_num_elements(self):
        """
        @dclayMethodReturn int
        @dclayMethodReadOnly
        """
        return self.max_num_elements

    def get_max_num_elements(self):
        """
        @dclayMethodReturn int
        @dclayMethodReadOnly
        """
        return self.max_num_elements
