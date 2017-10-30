
# [[file:~/Research/CFEDemands/Demands/demands.org::*Marshallian%20demand%20interface][marshallian]]

# Tangled on Mon Oct 30 16:39:41 2017
from . import frischian
from ._core import lambdavalue
from ._utils import check_args, derivative
from numpy import array

def demands(y,p,alpha,beta,phi,NegativeDemands=True):

    n,alpha,beta,phi = check_args(p,alpha,beta,phi)

    lbda=lambdavalue(y,p,alpha,beta,phi,NegativeDemands=NegativeDemands)

    return frischian.demands(lbda,p,alpha,beta,phi,NegativeDemands=NegativeDemands)


def indirect_utility(y,p,alpha,beta,phi,NegativeDemands=True):
    """
    Returns utils associated with income y and prices p.
    """

    n,alpha,beta,phi = check_args(p,alpha,beta,phi)

    lbda=lambdavalue(y,p,alpha,beta,phi,NegativeDemands=NegativeDemands)

    return frischian.V(lbda,p,alpha,beta,phi,NegativeDemands=NegativeDemands)

V = indirect_utility

def expenditures(y,p,alpha,beta,phi,NegativeDemands=True):

    n,alpha,beta,phi = check_args(p,alpha,beta,phi)
    
    x=demands(y,p,alpha,beta,phi,NegativeDemands=NegativeDemands)

    px=array([p[i]*x[i] for i in range(n)])

    try:
        assert abs(sum(px) - y) < 0.001
    except AssertionError: # Call to all debugging
        lambdavalue(y,p,alpha,beta,phi,NegativeDemands=NegativeDemands)        
    
    return px

def budgetshares(y,p,alpha,beta,phi,NegativeDemands=True):
    
    n,alpha,beta,phi = check_args(p,alpha,beta,phi)
    
    x=expenditures(y,p,alpha,beta,phi,NegativeDemands=NegativeDemands)

    w=array([x[i]/y for i in range(n)])

    assert abs(sum(w)-1)<0.001
    
    return w

def share_income_elasticity(y,p,alpha,beta,phi,NegativeDemands=True):
    """
    Expenditure-share elasticity with respect to total expenditures.
    """

    n,alpha,beta,phi = check_args(p,alpha,beta,phi)

    def w(xbar):
        return budgetshares(xbar,p,alpha,beta,phi,NegativeDemands=NegativeDemands)

    dw=derivative(w)

    return [dw(y)[i]*(y/w(y)[i]) for i in range(n)]

def income_elasticity(y,p,alpha,beta,phi,NegativeDemands=True):

    return array(share_income_elasticity(y,p,alpha,beta,phi,NegativeDemands=NegativeDemands))+1.0

# marshallian ends here
