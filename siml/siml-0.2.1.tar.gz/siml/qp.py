__all__ = []
options = {}

def fP(x, y, alpha = 1.0, beta = 0.0):
    base.symv(P, x, y, alpha = alpha, beta = beta)

def fG(x, y, trans = 'N', alpha = 1.0, beta = 0.0):
    misc.sgemv(G, x, y, dims, trans = trans, alpha = alpha, beta = beta)
    

def fA(x, y, trans = 'N', alpha = 1.0, beta = 0.0):
    base.gemv(A, x, y, trans = trans, alpha = alpha, beta = beta)

def res(ux, uy, uz, us, vx, vy, vz, vs, W, lmbda):

    # Evaluates residual in Newton equations:
    # 
    #      [ vx ]    [ vx ]   [ 0     ]   [ P  A'  G' ]   [ ux        ]
    #      [ vy ] := [ vy ] - [ 0     ] - [ A  0   0  ] * [ uy        ]
    #      [ vz ]    [ vz ]   [ W'*us ]   [ G  0   0  ]   [ W^{-1}*uz ]
    #
    #      vs := vs - lmbda o (uz + us).

    # vx := vx - P*ux - A'*uy - G'*W^{-1}*uz
    fP(ux, vx, alpha = -1.0, beta = 1.0)
    fA(uy, vx, alpha = -1.0, beta = 1.0, trans = 'T') 
    blas.copy(uz, wz3)
    misc.scale(wz3, W, inverse = 'I')
    fG(wz3, vx, alpha = -1.0, beta = 1.0, trans = 'T') 

    # vy := vy - A*ux
    fA(ux, vy, alpha = -1.0, beta = 1.0)

    # vz := vz - G*ux - W'*us
    fG(ux, vz, alpha = -1.0, beta = 1.0)
    blas.copy(us, ws3)
    misc.scale(ws3, W, trans = 'T')
    blas.axpy(ws3, vz, alpha = -1.0)

    # vs := vs - lmbda o (uz + us)
    blas.copy(us, ws3)
    blas.axpy(uz, ws3)
    misc.sprod(ws3, lmbda, dims, diag = 'D')
    blas.axpy(ws3, vs, alpha = -1.0)



# kktsolver(W) returns a routine for solving 
#
#     [ P   A'  G'*W^{-1} ] [ ux ]   [ bx ]
#     [ A   0   0         ] [ uy ] = [ by ].
#     [ G   0   -W'       ] [ uz ]   [ bz ]

 factor = misc.kkt_chol2(G, dims, A)
 def kktsolver(W):
     return factor(W, P)

def f4(x, y, z, s):
    if refinement or DEBUG: 
        xcopy(x, wx)        
        ycopy(y, wy)        
        blas.copy(z, wz)        
        blas.copy(s, ws)        
    f4_no_ir(x, y, z, s)        
    for i in range(refinement):
        xcopy(wx, wx2)        
        ycopy(wy, wy2)        
        blas.copy(wz, wz2)        
        blas.copy(ws, ws2)        
        res(x, y, z, s, wx2, wy2, wz2, ws2, W, lmbda) 
        f4_no_ir(wx2, wy2, wz2, ws2)
        xaxpy(wx2, x)
        yaxpy(wy2, y)
        blas.axpy(wz2, z)
        blas.axpy(ws2, s)
    if DEBUG:
        res(x, y, z, s, wx, wy, wz, ws, W, lmbda)
        print("KKT residuals:")
        print("    'x': %e" %math.sqrt(xdot(wx, wx)))
        print("    'y': %e" %math.sqrt(ydot(wy, wy)))
        print("    'z': %e" %misc.snrm2(wz, dims))
        print("    's': %e" %misc.snrm2(ws, dims))
    

# f4_no_ir(x, y, z, s) solves
# 
#     [ 0     ]   [ P  A'  G' ]   [ ux        ]   [ bx ]
#     [ 0     ] + [ A  0   0  ] * [ uy        ] = [ by ]
#     [ W'*us ]   [ G  0   0  ]   [ W^{-1}*uz ]   [ bz ]
#
#     lmbda o (uz + us) = bs.
#
# On entry, x, y, z, s contain bx, by, bz, bs.
# On exit, they contain ux, uy, uz, us.

def f4_no_ir(x, y, z, s):

    # Solve 
    #
    #     [ P A' G'   ] [ ux        ]    [ bx                    ]
    #     [ A 0  0    ] [ uy        ] =  [ by                    ]
    #     [ G 0 -W'*W ] [ W^{-1}*uz ]    [ bz - W'*(lmbda o\ bs) ]
    #
    #     us = lmbda o\ bs - uz.
    #
    # On entry, x, y, z, s  contains bx, by, bz, bs. 
    # On exit they contain x, y, z, s.
    
    # s := lmbda o\ s 
    #    = lmbda o\ bs
    misc.sinv(s, lmbda, dims)

    # z := z - W'*s 
    #    = bz - W'*(lambda o\ bs)
    blas.copy(s, ws3)
    misc.scale(ws3, W, trans = 'T')
    blas.axpy(ws3, z, alpha = -1.0)

    # Solve for ux, uy, uz
    f3(x, y, z)

    # s := s - z 
    #    = lambda o\ bs - uz.
    blas.axpy(z, s, alpha = -1.0)


# f4(x, y, z, s) solves the same system as f4_no_ir, but applies
# iterative refinement.
    
    
    
    
    coneqp(P, q, G, h, None, A,  b, initvals, kktsolver = None, options = options)
def coneqp(P, q, G = None, h = None, dims = None, A = None, b = None,
    initvals = None, kktsolver = None, xnewcopy = None, xdot = None,
    xaxpy = None, xscal = None, ynewcopy = None, ydot = None, yaxpy = None,
    yscal = None, **kwargs):

    import math
    from cvxopt import base, blas, misc
    from cvxopt.base import matrix, spmatrix

    STEP = 0.99
    EXPON = 3

    options = kwargs.get('options',globals()['options'])  
    DEBUG = options.get('debug',False)
    KKTREG = options.get('kktreg',None)
    correction = options.get('use_correction', True)
    MAXITERS = options.get('maxiters',100)
    ABSTOL = options.get('abstol',1e-7)
    RELTOL = options.get('reltol',1e-6)
    FEASTOL = options.get('feastol',1e-7)
    show_progress = options.get('show_progress',True)

    kktsolver = 'chol2'            
    defaultsolvers = ('ldl', 'ldl2', 'chol', 'chol2')

    # Argument error checking depends on level of customization.
    customkkt = not True
    matrixP = True
    matrixG = True
    matrixA = True
    customx = False 
    customy = False

    dims = {'l': h.size[0], 'q': [], 's': []}
    
    #cdim = dims['l'] + sum(dims['q']) + sum([ k**2 for k in dims['s'] ])
    cdim = dims['l']
    
    # Data for kth 'q' constraint are found in rows indq[k]:indq[k+1] of G.
    indq = [ dims['l'] ]  
    #for k in dims['q']:  indq = indq + [ indq[-1] + k ] 
    indq = indq + [ indq[-1] + k ] 

    # Data for kth 's' constraint are found in rows inds[k]:inds[k+1] of G.
    inds = [ indq[-1] ]
    for k in dims['s']:  inds = inds + [ inds[-1] + k**2 ] 
   
    #ws3, wz3 = matrix(0.0, (cdim,1 )), matrix(0.0, (cdim,1 ))
    ws3, wz3 = np.zeros(shape=(cdim,1)), np.zeros(shape=(cdim,1))
    
    #xnewcopy = matrix 
    #xdot = blas.dot
    #xaxpy = blas.axpy 
    #xscal = blas.scal 
    
    y = np.copy(x)
    # def xcopy(x, y): 
        # y = xscal(0.0, y) 
        # y = xaxpy(x, y)
    #ynewcopy = matrix 
    #ydot = blas.dot 
    #yaxpy = blas.axpy 
    #yscal = blas.scal
    y = np.copy(x)
    # def ycopy(x, y): 
        # yscal(0.0, y) 
        # yaxpy(x, y)

    #resx0 = max(1.0, math.sqrt(xdot(q,q)))
    #resy0 = max(1.0, math.sqrt(ydot(b,b)))
    #resz0 = max(1.0, misc.snrm2(h, dims))
    resx0 = np.max([1.0, math.sqrt(np.dot(q,q))])
    resy0 = np.max([1.0, math.sqrt(np.dot(b,b))])
    resz0 = np.max([1.0, math.sqrt(np.dot(np.transpose(q)*q))])
    
    
    # if cdim == 0: 

        # # Solve
        # #
        # #     [ P  A' ] [ x ]   [ -q ]
        # #     [       ] [   ] = [    ].
        # #     [ A  0  ] [ y ]   [  b ]

        # try: f3 = kktsolver({'d': matrix(0.0, (0,1)), 'di': 
            # matrix(0.0, (0,1)), 'beta': [], 'v': [], 'r': [], 'rti': []})
        # except ArithmeticError: 
            # raise ValueError("Rank(A) < p or Rank([P; A; G]) < n")
        # x = xnewcopy(q)  
        # xscal(-1.0, x)
        # y = ynewcopy(b)
        # f3(x, y, matrix(0.0, (0,1)))

        # # dres = || P*x + q + A'*y || / resx0 
        # rx = xnewcopy(q)
        # fP(x, rx, beta = 1.0)
        # pcost = 0.5 * (xdot(x, rx) + xdot(x, q))
        # fA(y, rx, beta = 1.0, trans = 'T')
        # dres = math.sqrt(xdot(rx, rx)) / resx0

        # # pres = || A*x - b || / resy0
        # ry = ynewcopy(b)
        # fA(x, ry, alpha = 1.0, beta = -1.0)
        # pres = math.sqrt(ydot(ry, ry)) / resy0 

        # if pcost == 0.0: relgap = None
        # else: relgap = 0.0

        # return { 'status': 'optimal', 'x': x,  'y': y, 'z': 
            # matrix(0.0, (0,1)), 's': matrix(0.0, (0,1)), 
            # 'gap': 0.0, 'relgap': 0.0, 
            # 'primal objective': pcost,
            # 'dual objective': pcost,
            # 'primal slack': 0.0, 'dual slack': 0.0,
            # 'primal infeasibility': pres, 'dual infeasibility': dres,
            # 'iterations': 0 } 


    #x, y = xnewcopy(q), ynewcopy(b)
    x,y = np.copy(q), np.copy(b)
    s, z = matrix(0.0, (cdim, 1)), matrix(0.0, (cdim, 1))
    

    # Factor
    #
    #     [ P   A'  G' ] 
    #     [ A   0   0  ].
    #     [ G   0  -I  ]
    
    W = {}
    W['d'] = matrix(1.0, (dims['l'], 1)) 
    W['di'] = matrix(1.0, (dims['l'], 1)) 
    W['v'] = [ matrix(0.0, (m,1)) for m in dims['q'] ]
    W['beta'] = len(dims['q']) * [ 1.0 ] 
    for v in W['v']: v[0] = 1.0
    W['r'] = [ matrix(0.0, (m,m)) for m in dims['s'] ]
    W['rti'] = [ matrix(0.0, (m,m)) for m in dims['s'] ]
    for r in W['r']: r[::r.size[0]+1 ] = 1.0
    for rti in W['rti']: rti[::rti.size[0]+1 ] = 1.0

    try: f = kktsolver(W)
    except ArithmeticError:  
        raise ValueError("Rank(A) < p or Rank([P; A; G]) < n")

         
    x = -np.copy(q)
    #xcopy(q, x)
    #xscal(-1.0, x)
    y = np.copy(b)
    #ycopy(b, y)  
    blas.copy(h, z)
    try: f(x, y, z) 
    except ArithmeticError:  
        raise ValueError("Rank(A) < p or Rank([P; G; A]) < n")
    blas.copy(z, s)  
    blas.scal(-1.0, s)  

    nrms = misc.snrm2(s, dims)
    ts = misc.max_step(s, dims)
    if ts >= -1e-8 * max(nrms, 1.0):  
        a = 1.0 + ts  
        s[:dims['l']] += a
        s[indq[:-1]] += a
        ind = dims['l'] + sum(dims['q'])
        for m in dims['s']:
            s[ind : ind+m*m : m+1] += a
            ind += m**2

    nrmz = misc.snrm2(z, dims)
    tz = misc.max_step(z, dims)
    if tz >= -1e-8 * max(nrmz, 1.0):
        a = 1.0 + tz  
        z[:dims['l']] += a
        z[indq[:-1]] += a
        ind = dims['l'] + sum(dims['q'])
        for m in dims['s']:
            z[ind : ind+m*m : m+1] += a
            ind += m**2


    rx, ry, rz = xnewcopy(q), ynewcopy(b), matrix(0.0, (cdim, 1)) 
    dx, dy = xnewcopy(x), ynewcopy(y)   
    dz, ds = matrix(0.0, (cdim, 1)), matrix(0.0, (cdim, 1))
    lmbda = matrix(0.0, (dims['l'] + sum(dims['q']) + sum(dims['s']), 1))
    lmbdasq = matrix(0.0, (dims['l'] + sum(dims['q']) + sum(dims['s']), 1))
    sigs = matrix(0.0, (sum(dims['s']), 1))
    sigz = matrix(0.0, (sum(dims['s']), 1))


    gap = misc.sdot(s, z, dims) 

    for iters in range(MAXITERS + 1):

        # f0 = (1/2)*x'*P*x + q'*x + r and  rx = P*x + q + A'*y + G'*z.
        rx = np.copy(q)
        #xcopy(q, rx)
        fP(x, rx, beta = 1.0)
        f0 = 0.5 * (xdot(x, rx) + xdot(x, q))
        fA(y, rx, beta = 1.0, trans = 'T')
        fG(z, rx, beta = 1.0, trans = 'T')
        resx = math.sqrt(xdot(rx, rx))
           
        # ry = A*x - b      
        ry = np.copy(b)
        #ycopy(b, ry)
        fA(x, ry, alpha = 1.0, beta = -1.0)
        resy = math.sqrt(ydot(ry, ry))

        # rz = s + G*x - h
        blas.copy(s, rz)
        blas.axpy(h, rz, alpha = -1.0)
        fG(x, rz, beta = 1.0)
        resz = misc.snrm2(rz, dims)


        # Statistics for stopping criteria.

        # pcost = (1/2)*x'*P*x + q'*x 
        # dcost = (1/2)*x'*P*x + q'*x + y'*(A*x-b) + z'*(G*x-h)
        #       = (1/2)*x'*P*x + q'*x + y'*(A*x-b) + z'*(G*x-h+s) - z'*s
        #       = (1/2)*x'*P*x + q'*x + y'*ry + z'*rz - gap
        pcost = f0
        dcost = f0 + ydot(y, ry) + misc.sdot(z, rz, dims) - gap
        if pcost < 0.0:
            relgap = gap / -pcost
        elif dcost > 0.0:
            relgap = gap / dcost 
        else:
            relgap = None
        pres = max(resy/resy0, resz/resz0)
        dres = resx/resx0 


        if ( pres <= FEASTOL and dres <= FEASTOL and ( gap <= ABSTOL or 
            (relgap is not None and relgap <= RELTOL) )) or \
            iters == MAXITERS:
            ind = dims['l'] + sum(dims['q'])
            for m in dims['s']:
                misc.symm(s, m, ind)
                misc.symm(z, m, ind)
                ind += m**2
            ts = misc.max_step(s, dims)
            tz = misc.max_step(z, dims)
            if iters == MAXITERS:
                if show_progress:
                    print("Terminated (maximum number of iterations "\
                        "reached).")
                status = 'unknown'
            else:
                if show_progress:
                    print("Optimal solution found.")
                status = 'optimal'
            return { 'x': x,  'y': y,  's': s,  'z': z,  'status': status,
                    'gap': gap,  'relative gap': relgap, 
                    'primal objective': pcost,  'dual objective': dcost,
                    'primal infeasibility': pres,
                    'dual infeasibility': dres, 'primal slack': -ts,
                    'dual slack': -tz , 'iterations': iters }
                    

        # Compute initial scaling W and scaled iterates:  
        #
        #     W * z = W^{-T} * s = lambda.
        # 
        # lmbdasq = lambda o lambda.
        
        if iters == 0:  W = misc.compute_scaling(s, z, lmbda, dims)
        misc.ssqr(lmbdasq, lmbda, dims)


        # f3(x, y, z) solves
        #
        #    [ P   A'  G'    ] [ ux        ]   [ bx ]
        #    [ A   0   0     ] [ uy        ] = [ by ].
        #    [ G   0   -W'*W ] [ W^{-1}*uz ]   [ bz ]
        #
        # On entry, x, y, z containg bx, by, bz.
        # On exit, they contain ux, uy, uz.

        f3 = kktsolver(W)

        if iters == 0:
            if refinement or DEBUG:
                wx, wy = xnewcopy(q), ynewcopy(b) 
                wz, ws = matrix(0.0, (cdim,1)), matrix(0.0, (cdim,1)) 
            if refinement:
                wx2, wy2 = xnewcopy(q), ynewcopy(b) 
                wz2, ws2 = matrix(0.0, (cdim,1)), matrix(0.0, (cdim,1)) 

        mu = gap / (dims['l'] + len(dims['q']) + sum(dims['s']))
        sigma, eta = 0.0, 0.0

        for i in [0, 1]:

            # Solve
            #
            #     [ 0     ]   [ P  A' G' ]   [ dx        ]
            #     [ 0     ] + [ A  0  0  ] * [ dy        ] = -(1 - eta) * r
            #     [ W'*ds ]   [ G  0  0  ]   [ W^{-1}*dz ]
            #
            #     lmbda o (dz + ds) = -lmbda o lmbda + sigma*mu*e (i=0)
            #     lmbda o (dz + ds) = -lmbda o lmbda - dsa o dza 
            #                         + sigma*mu*e (i=1) where dsa, dza
            #                         are the solution for i=0. 
 
            # ds = -lmbdasq + sigma * mu * e  (if i is 0)
            #    = -lmbdasq - dsa o dza + sigma * mu * e  (if i is 1), 
            #     where ds, dz are solution for i is 0.
            blas.scal(0.0, ds)
            if correction and i == 1:  
                blas.axpy(ws3, ds, alpha = -1.0)
            blas.axpy(lmbdasq, ds, n = dims['l'] + sum(dims['q']), 
                alpha = -1.0)
            ds[:dims['l']] += sigma*mu
            ind = dims['l']
            for m in dims['q']:
                ds[ind] += sigma*mu
                ind += m
            ind2 = ind
            for m in dims['s']:
                blas.axpy(lmbdasq, ds, n = m, offsetx = ind2, offsety =  
                    ind, incy = m + 1, alpha = -1.0)
                ds[ind : ind + m*m : m+1] += sigma*mu
                ind += m*m
                ind2 += m

       
            # (dx, dy, dz) := -(1 - eta) * (rx, ry, rz)
            xscal(0.0, dx);  xaxpy(rx, dx, alpha = -1.0 + eta)
            yscal(0.0, dy);  yaxpy(ry, dy, alpha = -1.0 + eta)
            blas.scal(0.0, dz) 
            blas.axpy(rz, dz, alpha = -1.0 + eta)
            
            f4(dx, dy, dz, ds)
            dsdz = misc.sdot(ds, dz, dims)

            # Save ds o dz for Mehrotra correction
            if correction and i == 0:
                blas.copy(ds, ws3)
                misc.sprod(ws3, dz, dims)


            # Maximum steps to boundary.  
            # 
            # If i is 1, also compute eigenvalue decomposition of the 
            # 's' blocks in ds,dz.  The eigenvectors Qs, Qz are stored in 
            # dsk, dzk.  The eigenvalues are stored in sigs, sigz.

            misc.scale2(lmbda, ds, dims)
            misc.scale2(lmbda, dz, dims)
            if i == 0: 
                ts = misc.max_step(ds, dims)
                tz = misc.max_step(dz, dims)
            else:
                ts = misc.max_step(ds, dims, sigma = sigs)
                tz = misc.max_step(dz, dims, sigma = sigz)
            t = max([ 0.0, ts, tz ])
            if t == 0:
                step = 1.0
            else:
                if i == 0:
                    step = min(1.0, 1.0 / t)
                else:
                    step = min(1.0, STEP / t)
            if i == 0: 
                sigma = min(1.0, max(0.0, 
                    1.0 - step + dsdz/gap * step**2))**EXPON
                eta = 0.0


        xaxpy(dx, x, alpha = step)
        yaxpy(dy, y, alpha = step)


        # We will now replace the 'l' and 'q' blocks of ds and dz with 
        # the updated iterates in the current scaling.
        # We also replace the 's' blocks of ds and dz with the factors 
        # Ls, Lz in a factorization Ls*Ls', Lz*Lz' of the updated variables
        # in the current scaling.

        # ds := e + step*ds for nonlinear, 'l' and 'q' blocks.
        # dz := e + step*dz for nonlinear, 'l' and 'q' blocks.
        blas.scal(step, ds, n = dims['l'] + sum(dims['q']))
        blas.scal(step, dz, n = dims['l'] + sum(dims['q']))
        ind = dims['l']
        ds[:ind] += 1.0
        dz[:ind] += 1.0
        for m in dims['q']:
            ds[ind] += 1.0
            dz[ind] += 1.0
            ind += m

        # ds := H(lambda)^{-1/2} * ds and dz := H(lambda)^{-1/2} * dz.
        #
        # This replaced the 'l' and 'q' components of ds and dz with the
        # updated iterates in the current scaling.
        # The 's' components of ds and dz are replaced with
        #
        #     diag(lmbda_k)^{1/2} * Qs * diag(lmbda_k)^{1/2}
        #     diag(lmbda_k)^{1/2} * Qz * diag(lmbda_k)^{1/2}
        # 
        misc.scale2(lmbda, ds, dims, inverse = 'I')
        misc.scale2(lmbda, dz, dims, inverse = 'I')

        # sigs := ( e + step*sigs ) ./ lambda for 's' blocks.
        # sigz := ( e + step*sigz ) ./ lmabda for 's' blocks.
        blas.scal(step, sigs)
        blas.scal(step, sigz)
        sigs += 1.0
        sigz += 1.0
        blas.tbsv(lmbda, sigs, n = sum(dims['s']), k = 0, ldA = 1, offsetA
            = dims['l'] + sum(dims['q']))
        blas.tbsv(lmbda, sigz, n = sum(dims['s']), k = 0, ldA = 1, offsetA
            = dims['l'] + sum(dims['q']))

        # dsk := Ls = dsk * sqrt(sigs).
        # dzk := Lz = dzk * sqrt(sigz).
        ind2, ind3 = dims['l'] + sum(dims['q']), 0
        for k in range(len(dims['s'])):
            m = dims['s'][k]
            for i in range(m):
                blas.scal(math.sqrt(sigs[ind3+i]), ds, offset = ind2 + m*i,
                    n = m)
                blas.scal(math.sqrt(sigz[ind3+i]), dz, offset = ind2 + m*i,
                    n = m)
            ind2 += m*m
            ind3 += m


        # Update lambda and scaling.
        misc.update_scaling(W, lmbda, ds, dz)


        # Unscale s, z (unscaled variables are used only to compute 
        # feasibility residuals).

        blas.copy(lmbda, s, n = dims['l'] + sum(dims['q']))
        ind = dims['l'] + sum(dims['q'])
        ind2 = ind
        for m in dims['s']:
            blas.scal(0.0, s, offset = ind2)
            blas.copy(lmbda, s, offsetx = ind, offsety = ind2, n = m, 
                incy = m+1)
            ind += m
            ind2 += m*m
        misc.scale(s, W, trans = 'T')

        blas.copy(lmbda, z, n = dims['l'] + sum(dims['q']))
        ind = dims['l'] + sum(dims['q'])
        ind2 = ind
        for m in dims['s']:
            blas.scal(0.0, z, offset = ind2)
            blas.copy(lmbda, z, offsetx = ind, offsety = ind2, n = m, 
                incy = m+1)
            ind += m
            ind2 += m*m
        misc.scale(z, W, inverse = 'I')

        gap = blas.dot(lmbda, lmbda) 


