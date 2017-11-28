import sys

def uprint(*args, **kwargs):
    """
    print(value, ..., sep=' ', file=sys.stdout, flush=False)

    Prints the values to a stream, or to sys.stdout by default.
    Optional keyword arguments:
    file:  a file-like object (stream); defaults to the current sys.stdout.
    sep:   string inserted between values, default a space.
    flush: whether to forcibly flush the stream.

    end is always end=""
    """
    print("\r", end="")
    # Clear to the end of line
    sys.stdout.write("\033[K")
    kwargs["end"] = ""
    print(*args, **kwargs)
    sys.stdout.flush()
