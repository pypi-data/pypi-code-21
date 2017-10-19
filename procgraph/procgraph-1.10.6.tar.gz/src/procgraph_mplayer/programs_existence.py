from contracts import contract
from system_cmd.which import find_executable

__all__ = ['check_programs_existence']


@contract(returns='dict(str:str)')
def check_programs_existence(programs):
    res = {}
    for p in programs:
        e = find_executable(p)
        if e is None:
            msg = 'Cannot find program %r.' % p
            raise ValueError(msg)
        else:
            res[p] = e

    return res
