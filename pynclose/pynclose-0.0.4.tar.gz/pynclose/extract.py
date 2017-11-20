"""Routine to extract contexts iteratively.

"""


def from_csv_file(fname:str) -> iter:
    """Yield ({object}, {attribute}), two frozensets implementing extent of
    intent for each concept found in given file.

    """
    with open(fname) as fd:
        while True:
            try:
                attrs = frozenset(map(str.strip, next(fd).split(',')))
                objts = frozenset(map(str.strip, next(fd).split(',')))
            except StopIteration:
                break  # no more concepts
            yield objts, attrs
