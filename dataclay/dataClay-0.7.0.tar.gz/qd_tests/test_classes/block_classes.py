from dataclay.contrib.register.collections.structures import Block


class MaxBlock(Block):
    """Blocking abstraction layer for nice high-level blocking.

    @dclayProperty int max_value
    @dclayProperty int idx_max
    """
    def __init__(self):
        """
        @dclayMethodReturn None
        """
        self.max_value = 0
        self.idx_max = -1

        # copied from the parent --WIP
        self.first_chunk = None
        self.first_index = 0
        self.num_chunks = 1

        # The transient variables
        self._loaded_chunk = None
        self._finished_chunk = None
        self._chunks_done = None
        self._i_in_chunk = None
        self._current_index = None

    def eval_max(self):
        """
        @dclayMethodReturn int
        """
        import numpy as np
        self.max_value = None
        self.start_iteration()

        while self.has_next():
            idx, row = self.get_next()
            _temp = row.max()

            if _temp > self.max_value:
                self.max_value = _temp
                self.idx_max = idx

        return self.max_value

    def get_max(self):
        """
        @dclayMethodReturn int
        """
        return self.max_value

    def get_idx_max(self):
        """
        @dclayMethodReturn int
        """
        return self.idx_max
