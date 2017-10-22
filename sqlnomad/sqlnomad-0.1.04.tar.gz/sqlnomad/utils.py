# coding=utf-8
from typing import Sequence, Union, Optional


def rebracket(s) -> str:
    """Remove brackets within a string, and then surround the string with new brackets

    This is used to deal with field aliases that may or may not have brackets,
    and allows calling code to assume that regardless of its initial state the
    field will have brackets surrounding it.
    """
    new_str = strip_chars(s, "[]")
    return f"[{new_str}]"


def strip_chars(s: Optional[str], chars: Union[str, Sequence[str]]) -> str:
    """Strip specified characters from a string

    Example
    -------
    >>> strip_chars("[test]", "[]")
    'test'
    >>> strip_chars(None, "[]")
    ''
    """
    if s:
        clean = s.strip()
        for c in chars:
            clean = clean.replace(c, "")
        return clean
        # return s.replace("[", "").replace("]", "").strip()
    return ""


def standardize_string(original: str) -> str:
    """Remove special characters and standardize spaces in a string

    Example
    -------
    >>> standardize_string(f"SELECT first_name\\n   FROM (   SELECT * FROM customers)\\n")
    'SELECT first_name FROM (SELECT * FROM customers)'
    """
    new = strip_chars(original, "\n\r\t")
    new = " ".join(new.split())
    new = new.replace("{ ", "{")
    new = new.replace(" }", "}")
    new = new.replace("( ", "(")
    new = new.replace(" )", ")")
    return new


if __name__ == '__main__':
    import doctest

    doctest.testmod()
