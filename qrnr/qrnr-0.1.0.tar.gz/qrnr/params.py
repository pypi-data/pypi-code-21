"""methods to parse parameters
"""
from datetime import datetime

PARSERS = dict(
    date=lambda s: datetime.strptime(s, "%Y-%m-%d"),
    iso_ts=lambda s: datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ"),
    int=int,
    text=str,
    double=float,
)


def parse_parameters(pars):
    """
    Parameters
    ----------
    pars : str
      string that contains parameters. The format of parameters is:
        name1:type1=value1[;name2:type2=value2...]
      i.e., a semicolon ';' is an entry separator, an equal sign '=' is a key-value separator,
      and a colon ':' is a keyname-type separator.
      thus the following is interpreted as variable foo = 2 and bar = 2017-01-01 (as date)
        foo:int=2;bar:date=2017-01-01

    Returns
    -------
    a dict of parsed parameters

    >>> from datetime import datetime
    >>> parse_parameters('') == dict()
    True
    >>> ex1 = parse_parameters('foo:int=2;bar:date=2017-01-01')
    >>> ex1 == dict(foo=2, bar=datetime.strptime('2017-01-01', "%Y-%m-%d"))
    True
    >>> parse_parameters('bar:double=1.0') == dict(bar=1.0)
    True
    >>> parse_parameters('hoge:unknown=error')
    Traceback (most recent call last):
    ...
    RuntimeError: Unknown parameter type: unknown
    """
    if not pars:
        return dict()
    params = dict()
    for ktv in pars.split(';'):
        kt, v = ktv.split('=', 1)
        k, t = kt.split(':', 1)
        if t not in PARSERS:
            raise RuntimeError("Unknown parameter type: {}".format(t))
        params[k] = PARSERS[t](v)
    return params


if __name__ == '__main__':
    import doctest
    doctest.testmod()
