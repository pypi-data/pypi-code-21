
# [[file:~/Research/CFEDemands/Demands/demands.org::*Frischian%20demand%20interface][frischian]]

# Tangled on Mon Oct 30 16:39:41 2017
from ._utils import check_args
from numpy import log

def demands(lbda,p,alpha,beta,phi,NegativeDemands=True):
    """
    Given marginal utility of income lbda and prices, 
    returns a list of $n$ quantities demanded, conditional on 
    preference parameters (alpha,beta,phi).
    """
    n,alpha,beta,phi = check_args(p,alpha,beta,phi)

    x=[((alpha[i]/(p[i]*lbda))**beta[i] - phi[i]) for i in range(n)]

    if not NegativeDemands:
        x=[max(x[i],0.) for i in range(n)]        

    return x

def indirect_utility(lbda,p,alpha,beta,phi,NegativeDemands=True):
    """
    Returns value of Frisch Indirect Utility function
    evaluated at (lbda,p) given preference parameters (alpha,beta,phi).
    """
    n,alpha,beta,phi = check_args(p,alpha,beta,phi)

    x=demands(lbda,p,alpha,beta,phi,NegativeDemands=NegativeDemands)

    U=0
    for i in range(n):
        if beta[i]==1:
            U += alpha[i]*log(x[i]+phi[i])
        else:
            U += alpha[i]*((x[i]+phi[i])**(1-1./beta[i])-1)*beta[i]/(beta[i]-1)

    return U

V = indirect_utility

# frischian ends here
