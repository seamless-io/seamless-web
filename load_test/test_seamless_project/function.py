import decimal

import scipy

PI_DIGITS = 10000


def pi():
    """
    Compute Pi to the current precision.

    Examples
    --------
    >>> print(pi())
    3.141592653589793238462643383

    Notes
    -----
    Taken from https://docs.python.org/3/library/decimal.html#recipes
    """
    decimal.getcontext().prec = PI_DIGITS
    decimal.getcontext().prec += 2  # extra digits for intermediate steps
    three = decimal.Decimal(3)      # substitute "three=3.0" for regular floats
    lasts, t, s, n, na, d, da = 0, three, 3, 1, 0, 0, 24
    while s != lasts:
        lasts = s
        n, na = n + na, na + 8
        d, da = d + da, da + 32
        t = (t * n) / d
        s += t
    decimal.getcontext().prec -= 2
    return +s


if __name__ == '__main__':
    print(f'SciPy version: {scipy.__version__}')
    print('Executing...')
    print(pi())
    print('Finished')
