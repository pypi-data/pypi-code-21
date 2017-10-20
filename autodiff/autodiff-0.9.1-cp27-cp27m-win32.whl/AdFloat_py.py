import numpy as np
from scipy.special import erf as errorfunc


class AdFloat():

    __slots__ = ['dx', 'x']

    def __init__(self, x, dx=1):
        self.x = x
        self.dx = dx


    def __add__(self, b):
        """
        d/dx(a+b) = d/dx(a) + d/dx(b)
        """
        a = self
        if isinstance(b, AdFloat):
            return AdFloat(a.x+b.x, a.dx + b.dx)
        
        return AdFloat(a.x+b, a.dx)

    def __mul__(self, b):
        """
        d/dx(a*b) = d/dx(a)*b + d/dx(b)*a
        """
        a = self
        if isinstance(b, AdFloat):
            return AdFloat(a.x*b.x, a.dx*b.x + b.dx*b.x)

        return AdFloat(a.x*b, a.dx*b)



    def __sub__(self, b):
        """
        d/dx(a-b) = dx(a) - d/dx(b)
        """
        a = self
        if isinstance(b, AdFloat):
            return AdFloat(a.x-b.x, a.dx - b.dx)

        return AdFloat(a.x-b, a.dx)

    
    def __truediv__(self, b):
        """
        d/dx(a/b) = ( d/dx(a)*b- d/dx(b)*a ) / (b^2)
        """
        a = self
        if isinstance(b, AdFloat):
            return AdFloat(a.x/b.x, (a.dx*b.x - b.dx*a.x)/b.x**2)

        return AdFloat(a.x/b, a.dx/b)
    
    def __pow__(self, b):
        """
        d/dx(a**b) = b*a^(b-1)*d/dx(a) + ln(a)*a^b*d/dx(b)
        """
        a = self
        if isinstance(b, AdFloat):
            #Both a and b are variables
            if a.dx == 1 and b.dx == 1:
                #avoid log(0)
                if a.x==0:
                    return AdFloat(a.x**b.x, b.x*a.x**(b.x-1)*a.dx)

                return AdFloat(a.x**b.x, b.x*a.x**(b.x-1)*a.dx + np.log(a.x)*a.x**b.x*b.dx)
            
            # a is a variable, and b in a constant
            elif a.dx==1:
                
                return AdFloat(a.x**b.x, b.x*a.x**(b.x-1)*a.dx)
            
            # b is a variable, and a is a constant
            elif b.dx==1:
                #avoid log(0)
                if a.x==0:
                    return AdFloat(a.x**b.x, 0)
                return AdFloat(a.x**b.x, a.x**b.x*np.log(a.x)*b.dx)
            
            return AdFloat(a.x**b.x, b.x*a.x**(b.x-1)*a.dx)
        # a is a variable and b is a constant
        return AdFloat(a.x**b, b*a.x**(b-1)*a.dx)
    
    __radd__ = __add__
    __rmul__ = __mul__
    __rsub__ = __sub__
    __rtruediv__ = __truediv__
    __rpow__ = __pow__

def sqrt(a):
    if isinstance(a, AdFloat):
        return AdFloat(np.sqrt(a.x), a.dx/(2*np.sqrt(a.x)))
    return np.sqrt(a)
def sin(a):
    if isinstance(a, AdFloat):
        return AdFloat(np.sin(a.x), np.cos(a.x)*a.dx)
    return np.sin(a)
def cos(a):
    if isinstance(a, AdFloat):
        return AdFloat(np.cos(a.x), -np.sin(a.x)*a.dx)
    return np.cos(a)
def tan(a):
    if isinstance(a, AdFloat):
        return AdFloat(np.tan(a.x), a.dx/np.cos(a.x)**2)
    return np.tan(a)
def erf(a):
    if isinstance(a, AdFloat):
        return AdFloat(errorfunc(a.x), 2.0 / np.sqrt(np.pi) * np.exp(-(a.x ** 2.0)) * a.dx)
    return errorfunc(a)
def exp(a):
    if isinstance(a, AdFloat):
        return AdFloat(np.exp(a.x), np.exp(a.x)*a.dx)
    return np.exp(a)
def log(a):
    if isinstance(a, AdFloat):
        return AdFloat(np.log(a.x), a.dx/a.x)
    return np.log(a)
    
def partial(f, x, i):
    """
    Computes the partial derivative of f(x) with respect to x_i
    This is done by setting d/dx_j (x)=0 forall j ≠ i
    """
    result = f(*[AdFloat(x_j, j == i) for j, x_j in enumerate(x)])
    return result.dx


def jacobian(f, x, param):
    """
    Calculates the jacobian matrix for d/dx_i (f(x))
    """

    N = len(x)
    M = len(param)
    J = np.zeros((N, M))
    for i, x_i in enumerate(x):
        for j in range(M):
            parameters=[]
            for k, p_k in enumerate(param):
                    parameters.append(AdFloat(p_k, k == j))
            # parameters = [AdFloat(p_k, k == j) for k, p_k in enumerate(param)]
            val = f(AdFloat(x_i,0), parameters)
            J[i, j] = val.dx

    return J

