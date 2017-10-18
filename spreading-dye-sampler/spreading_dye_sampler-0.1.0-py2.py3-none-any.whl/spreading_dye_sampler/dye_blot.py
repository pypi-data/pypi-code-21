import numpy as np

class DyeBlot:
    def __init__(self, grid_dims, cell_dims):
        self._grid_dims = grid_dims
        """Width and height of the grid in a 2-element list."""
        self._cell_dims = cell_dims
        """Width and height of the cells in a 2-element list."""
        self._cells = []
        """A list of 2-tuples containing cell coordinates."""

    def num_cells(self):
        """Returns the number of cells in the blot."""
        return len(self._cells)

    def for_each_cell(self, function):
        """
        Calls function(x, y) for each cell in the blot.

        Args:
            function: A callable object.
        """
        for cell in self._cells:
            function(cell[0], cell[1])


def make_blot(grid_dims, cell_dims, req_num_cells, permitted=None, squeeze=False):
    """
    Create a DyeBlot on a given grid, perhaps enforcing a mask.

    If permitted is specified, only cells for which permitted has a
    truthy value will be selected. If squeeze is True, non-permitted
    cells will simply be removed from consideration when extending
    a blot; if it is False, blot construction will be stopped and
    None returned if a non-permitted cell is used.

    Args:
        grid_dims (List): A 2-element list with width and height \
            of the grid, in that order.

        cell_dims (List): A 2-element list with width and height \
            off the cells, in that order.

        req_num_cells (Int): The required size of the blot.

        permitted (np.ndarray): A 2D array of size corresponding to \
            grid_dims.

    Returns:
        (Union[DyeBlot, None]) The constructed DyeBlot, or None if \
            squeeze is False and a masked cell was used.
    """
    from numpy.random import random
    from numpy.random import choice

    grid_width = grid_dims[0]
    grid_height = grid_dims[1]
    cell_width = cell_dims[0]
    cell_height = cell_dims[1]

    blot = DyeBlot(grid_dims, cell_dims)
    if permitted is None:
        permitted = np.ones(grid_dims, dtype=bool)
    neighbours = {}     # dict of (x, y) -> shared_edge_length

    def _add_neighbour(neighbour, new_edge_length):
        if neighbour in blot._cells:
            return
        if neighbour in neighbours:
            neighbours[neighbour] += new_edge_length
        else:
            neighbours[neighbour] = new_edge_length

    def _add_cell(cell):
        blot._cells.append(cell)

        _add_neighbour((cell[0] - 1, cell[1]), cell_height)
        _add_neighbour((cell[0], cell[1] - 1), cell_width)
        _add_neighbour((cell[0] + 1, cell[1]), cell_height)
        _add_neighbour((cell[0], cell[1] + 1), cell_width)

    def _draw_neighbour():
        cells, lengths = zip(*neighbours.items())
        indices = np.arange(0, len(cells))
        probabilities = np.asarray(lengths) / sum(lengths)
        index = choice(indices, p=probabilities)
        return cells[index]

    def _is_permitted(neighbour):
        if neighbour[0] < 0: return False
        if neighbour[0] >= grid_width: return False
        if neighbour[1] < 0: return False
        if neighbour[1] >= grid_height: return False
        return permitted[neighbour]

    cx = int(np.floor(random() * grid_width))
    cy = int(np.floor(random() * grid_height))
    start = cx, cy

    if _is_permitted(start):
        _add_cell(start)
        while neighbours != {} and len(blot._cells) < req_num_cells:
            neighbour = _draw_neighbour()
            if _is_permitted(neighbour):
                _add_cell(neighbour)
            elif not squeeze:
                return None
            del(neighbours[neighbour])
    else:
        return None

    return blot

if __name__ == '__main__':
    blot = make_blot([1200, 1600], [30, 30], 10)
    print(blot)
