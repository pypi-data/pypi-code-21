import scipy as sp


def fast_random_choice(weights):
    """
    This is at least for small arrays much faster
    than numpy.random.choice.
    """
    cs = 0
    u = sp.random.rand()
    for k in range(weights.size):
        cs += weights[k]
        if u <= cs:
            return k
    raise Exception("Random choice error {}".format(weights))
