import numpy as np

def weighting(turns, misses, attendences, npeople, nmeetings, meetings_since_turn, punishment, at_delta, floor, attack):
    delta = misses - turns
    opportunities = attendences + misses
    boost = np.log((punishment - 1) * floor) / at_delta
    w = boost * (delta / opportunities)
    w = floor + np.exp(w.fillna(0)) - 1
    w *= attack / npeople * np.log(meetings_since_turn+1) + 1
    return w


def probs(weights, minimum=None, minimum_factor=None, maximum=None, max_difference=None):
    p = weights / weights.sum()

    if (maximum is not None) and (minimum is not None):
        minimum_factor = minimum * len(p)
    elif max_difference is not None:
        minimum_factor = 1 - max_difference
    if minimum_factor is not None:
        minimum = minimum_factor * 1. / len(p)
    else:
        raise ValueError("Specify minimum and maximum, or max_difference or minimum_factor")
    if minimum >= (1. / len(p)):
        return (p / p) * (1. / len(p))
    filt = p < minimum
    if filt.sum() > 0:
        print('{} are adjusted up to the minimum {:.2%}'.format(', '.join(p[filt].index.values), minimum))
    p[filt] = minimum  # set those below min to min
    adjust = 1 - p.sum()  # amount over 1
    rest = p[~filt] / p[~filt].sum()  # fraction of probabilty of unminimised ones
    p[~filt] += rest * adjust  # add the appropriate adjustment on the unminimised ones
    if (p < minimum).any():
        p = probs(p, minimum_factor=minimum_factor)
    return p


def algorithm(df):
    df['weight'] = weighting(df.turns, df.misses, df.attendences, len(df), df.turns.sum(), df.meetings_since_turn, 10000, 1, 1, 10)
    df['weight'] = probs(df['weight'], maximum=1, minimum=0.01)
    return df


def simulate(df, n):
    # df.loc['jon', 'attendences'] += 1
    # df.loc['jon', 'turns'] += 1
    np.random.seed(0)
    chosen = []
    for i in range(n):
        df = algorithm(df)
        chosen.append(df.sample(n=1, weights='weight').index[0])
        df.loc[chosen[-1], 'turns'] += 1
        df.loc[:, 'attendences'] += 1
    return algorithm(df)
