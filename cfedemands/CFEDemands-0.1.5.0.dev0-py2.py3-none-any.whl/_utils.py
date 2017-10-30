
# [[file:~/Research/CFEDemands/Demands/demands.org::*Utility%20and%20optimization%20routines][demand_utils]]

# Tangled on Mon Oct 30 16:39:41 2017
from scipy import optimize 
from numpy import array, ones, zeros, sum, log, Inf, dot, nan, all
import warnings

def check_args(p,alpha,beta,phi):
    """
    Perform sanity check on inputs.  Supply default values if these are missing.
    """

    # Make sure all args are of type array:
    p=array(p,dtype=float)

    try: 
        len(alpha) # If len() not defined, then must be a singleton
        alpha=array(alpha,dtype=float)
    except TypeError: alpha=array([alpha],dtype=float)

    try:
        len(beta) # If len() not defined, then must be a singleton
        beta = array(beta,dtype=float)
    except TypeError: beta = array([beta],dtype=float)

    try:
        len(phi) # If len() not defined, then must be a singleton
        phi=array(phi,dtype=float)
    except TypeError: phi=array([phi],dtype=float)

    n=len(p)

    if len(alpha)==1<n:
        alpha=ones(n)*alpha
    else:
        if not alpha.all():
            raise ValueError

    if len(beta)==1<n:
        beta = ones(n)*beta
    else:
        if not beta.all():
            raise ValueError
        if not all(beta>0):
            raise ValueError
    
    if len(phi)==1<n:
        phi=ones(n)*phi

    return (n,alpha,beta,phi)

def derivative(f,h=2e-5,LIMIT=False):
    """
    Computes the numerical derivative of a function with a single scalar argument.

    - h :: A precision parameter.  

    BUGS: Would be better to actually take a limit, instead of assuming that h 
    is infinitesimal.  
    """
    def df(x, h=h):
        return ( f(x+h/2) - f(x-h/2) )/h
    return df

# demand_utils ends here
