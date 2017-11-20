"""Routines to export an iterable of concepts to another format.

"""

import inclose
from . import extract


def to_asp(concepts:(frozenset, frozenset), first_index:int=0) -> iter:
    """Yield atoms representing given concepts"""
    for idx, (exts, ints) in enumerate(concepts, start=first_index):
        yield from ('ext({},"{}").'.format(idx, ext) for ext in exts)
        yield from ('int({},"{}").'.format(idx, int) for int in ints)


def to_asp_file(fname:str, concepts:(frozenset, frozenset), first_index:int=0,
                atom_sep:str='\n') -> iter:
    with open(fname, 'w') as ofd:
        ofd.write(atom_sep.join(to_asp(concepts, first_index=first_index)))


def asp_from_context(context:str, min_ext:int=1, min_int:int=1,
                     first_index:int=0, atom_sep:str='\n') -> iter:
    """Yield atoms representing concepts of given context"""
    csv_file = inclose.run_search(context, min_ext, min_int)
    yield from to_asp(extract.from_csv_file(csv_file))
