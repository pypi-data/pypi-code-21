
# [[file:~/Research/CFEDemands/Demands/demands.org::*Hicksian%20demand%20interface][hicksian]]

# Tangled on Mon Oct 30 16:39:41 2017
from . import frischian
from ._utils import check_args
from ._core import lambdaforU
from numpy import array

def expenditurefunction(U,p,alpha,beta,phi,NegativeDemands=True):

    n,alpha,beta,phi = check_args(p,alpha,beta,phi)

    x=demands(U,p,alpha,beta,phi,NegativeDemands=NegativeDemands)

    return sum(array([p[i]*x[i] for i in range(n)]))

def demands(U,p,alpha,beta,phi,NegativeDemands=True):

    n,alpha,beta,phi = check_args(p,alpha,beta,phi)
    lbda=lambdaforU(U,p,alpha,beta,phi,NegativeDemands=NegativeDemands)

    return frischian.demands(lbda,p,alpha,beta,phi,NegativeDemands=NegativeDemands)

def budgetshares(U,p,alpha,beta,phi,NegativeDemands=True):

    n,alpha,beta,phi = check_args(p,alpha,beta,phi)
    
    h=demands(U,p,alpha,beta,phi,NegativeDemands=NegativeDemands)
    y=expenditurefunction(U,p,alpha,beta,phi,NegativeDemands=NegativeDemands)

    return array([p[i]*h[i]/y for i in range(n)])

# hicksian ends here
