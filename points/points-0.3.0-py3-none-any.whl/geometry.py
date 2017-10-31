"""Contains functions for using trigonometry equations."""

import math

def degree_angle(func):
    """A decorator which takes a function that returns an angle in radians and
    confers upon it the ability to return it in degrees."""

    def new_func(*args, degrees=False, **kwargs):
        angle = func(*args, **kwargs)
        if degrees:
            return math.degrees(angle)
        return angle
    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    return new_func
