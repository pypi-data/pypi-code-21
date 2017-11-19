from numpy import sum, power, abs


def mse(expected, real):
    return sum(power((expected - real), 2))


def mae(expected, real):
    return sum(abs(expected - real))


def get_loss(name):
    """Returns loss function by the name."""

    try:
        return globals()[name]
    except:
        raise ValueError('Invalid metric function.')