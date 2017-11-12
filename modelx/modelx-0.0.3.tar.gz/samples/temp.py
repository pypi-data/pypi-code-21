from modelx import *

def create_testmodel():

    # base<------------derived
    #  |                  |
    # subspace          subspace
    #  |     |            |    |
    # fibo  nestedsub    fibo  nestedsub
    #        |                  |
    #       fibo               fibo

    model, base = new_model(), new_space('base')
    subspace = base.new_space('subspace')
    nestedsub = subspace.new_space('nestedsub')
    derived = model.new_space('derived', bases=base)

    def fibo(x):
        if x == 0 or x == 1:
            return x
        else:
            return fibo(x - 1) + fibo(x - 2)

    subspace.new_cells(func=fibo)
    nestedsub.new_cells(func=fibo)

    return model


