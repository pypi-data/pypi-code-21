import pytest


def parametrize_with_names(arguments, named_values, **kwargs):
    """
    :type arguments: str
    :type named_values: dict
    :rtype: callable
    """
    names, values = zip(*sorted(named_values.items()))
    return pytest.mark.parametrize(arguments, values, ids=names, **kwargs)
