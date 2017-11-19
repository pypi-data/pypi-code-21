import numbers
import math

def const(k):
    '''
    Returns a constant reaction rate coefficient, k.
    The returned k is the same value as the input,
    but has been checked for non-numeric types.

    INPUT
    k: must be numeric.

    RETURN
    k: numeric.

    EXAMPLE
    >>> const(5)
    5
    '''
    assert(isinstance(k, numbers.Number)), "Please specify a numeric reaction rate coefficient!"
    if k < 0:
        raise ValueError("Reaction rate must be positive.")
    return k

def arrh(A, E, T = 1200):
    '''
    Returns the Arrhenius reaction rate coefficient, k_arr.

    INPUTS
    ======
    A: positive numeric
       Arrhenius prefactor
       constant
    E: numeric
       activation energy
       same units as R*T (see R below)
    T: positive, nonzero numeric
       temperature in degrees Kelvin
       default value is 100

    CONSTANT
    ========
    R: ideal gas constant.
       value always 8.341
       units of (kg m^2) / (mol K s^2))

    RETURNS
    =======
    k_arr: numeric

    NOTES
    =====
    PRE:
        - A, E, T have numeric type
        - three inputs
        - default temperature is 100
    POST:
        - A and E are not changed by this function;
          T is changed if it is 0.
        - raises errors if T or A are negative
        - coerces T to 1E-6 if it is 0
        - returns a number

    EXAMPLE
    =======
    >>> arrh(100, 10, 1)
    30.152660796667536

    >>> arrh(A=10**7, E=10**3, T=10**2)
    3015266.079666753
    '''
    R = 8.341

    vars = [A, E, T]
    for variable in vars:
        assert (isinstance(variable, numbers.Number)), "Please provide numeric variables."
    assert (T >= 0), "T must be positive."
    assert (A > 0), "A must be positive."

    # Force T to not be 0
    try:
        1/T
    except ZeroDivisionError:
        print("Temperature cannot be absolute zero. Coercing T to 1E-6.")
        T = 1*10**-6

    # Return the solution to the equation
    return A*math.exp(-E/(R*T))

def mod_arrh(A, b, E, T = 1200):
    '''
    Returns modified Arrhenius reaction rate coefficient, k_mod-arr.

    INPUTS
    ======
    A: positive numeric
       Arrhenius prefactor
       constant
    b: real numeric
       modified Arrhenius parameter
       constant
    E: numeric
       activation energy
       same units as R*T (see R below)
    T: positive, nonzero numeric
       temperature in degrees Kelvin
       default value is 100

    CONSTANT
    ========
    R: ideal gas constant.
       value always 8.341
       units of (kg m^2) / (mol K s^2))

    RETURNS
    =======
    k_arr: numeric

    NOTES
    =====
    PRE:
        - A, b, E, T have numeric type
        - four inputs
        - default temperature is 100
    POST:
        - A, b, and E are not changed by this function;
          T is changed if it is 0.
        - raises errors if T or A are negative
        - raises error if b is nonreal
        - coerces T to 1E-6 if it is 0
        - returns a number

    EXAMPLE
    =======
    >>> mod_arrh(100, .5, 10, 5)
    175.93414330670856

    >>> mod_arrh(A=10**7, b=0.5, E=10**3, T=10**2)
    30152660.79666753
    '''
    R = 8.341

    vars = [A, b, E, T]
    for variable in vars:
        assert (isinstance(variable, numbers.Number)), "Please provide numeric variables."
    assert (T >= 0), "T must be positive."
    assert (A > 0), "A must be positive."
    if isinstance(b, complex):
        raise ValueError("b must be a real number.")

    # Force T to not be 0
    try:
        1/T
    except ZeroDivisionError:
        print("Temperature cannot be absolute zero. Coercing T to 1E-6.")
        T = 1*10**-6

    # Return the solution to the equation
    return A*T**b*math.exp(-(E/(R*T)))
