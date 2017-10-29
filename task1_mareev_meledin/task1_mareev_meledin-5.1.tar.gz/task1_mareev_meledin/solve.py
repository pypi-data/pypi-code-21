import numpy as np
from scipy.optimize import linprog


def nash_equilibrium(in_matrix):
    a = np.matrix(in_matrix)
    n = len(a)  
    m = len(a.T) 
    row_min = np.min(a, 1)    
    col_max = np.max(a.T, 1)  
    
    for i in range(0, n):
        for j in range(0, m):
            if (a[i, j] == row_min[i] and a[i, j] == col_max[j]):
                p = np.zeros(n) 
                q = np.zeros(m) 
                p[i] = 1
                q[j] = 1
                return {'f': a[i, j], 'p': p.tolist(), 'q': q.tolist()}

    sub = min(0, np.min(a))
    a -= sub    

    c = np.ones(n)  
    a_ub = np.vstack((-a.T, -np.identity(n))) 
    b_ub = np.hstack((np.full(m, -1), np.zeros(n))) 
    res = linprog(c, a_ub, b_ub)     
    f = 1 / res.fun + sub       
    p = res.x * 1/res.fun
   

    c = np.full(m, -1)
    a_ub = np.vstack((a, -np.identity(m)))
    b_ub = np.hstack((np.ones(n), np.zeros(m)))
    res = linprog(c, a_ub, b_ub)
    q = res.x * -1/res.fun 
    
    return {'f': f, 'p': p.tolist(), 'q': q.tolist()}
