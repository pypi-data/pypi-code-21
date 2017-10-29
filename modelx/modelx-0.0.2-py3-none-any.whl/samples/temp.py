from modelx import *

model, space = new_model(), new_space()


@defcells
def bar():
    return 2 * n