#
# This file is part of TransportMaps.
#
# TransportMaps is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TransportMaps is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with TransportMaps.  If not, see <http://www.gnu.org/licenses/>.
#
# Transport Maps Library
# Copyright (C) 2015-2017 Massachusetts Institute of Technology
# Uncertainty Quantification group
# Department of Aeronautics and Astronautics
#
# Author: Transport Map Team
# Website: transportmaps.mit.edu
# Support: transportmaps.mit.edu/qa/
#

import warnings
import scipy.linalg as scialg
from scipy.optimize import OptimizeResult
from scipy.optimize.linesearch import line_search_wolfe1, line_search_wolfe2, LineSearchWarning
import numpy as np

__all__ = ['minimize_newtonlu','minimize_newtoncglu']

_epsilon = np.sqrt(np.finfo(float).eps)

# standard status messages of optimizers
_status_message = {'success': 'Optimization terminated successfully.',
                   'maxfev': 'Maximum number of function evaluations has '
                              'been exceeded.',
                   'maxiter': 'Maximum number of iterations has been '
                              'exceeded.',
                   'pr_loss': 'Desired error not necessarily achieved due '
                              'to precision loss.'}

class _LineSearchError(RuntimeError):
    pass

def _line_search_wolfe12(f, fprime, xk, pk, gfk, old_fval, old_old_fval,
                         **kwargs):
    """
    Same as line_search_wolfe1, but fall back to line_search_wolfe2 if
    suitable step length is not found, and raise an exception if a
    suitable step length is not found.
    Raises
    ------
    _LineSearchError
        If no suitable step size is found
    """
    ret = line_search_wolfe1(f, fprime, xk, pk, gfk,
                             old_fval, old_old_fval,
                             **kwargs)

    if ret[0] is None:
        # line search failed: try different one.
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', LineSearchWarning)
            ret = line_search_wolfe2(f, fprime, xk, pk, gfk,
                                     old_fval, old_old_fval)

    if ret[0] is None:
        raise _LineSearchError()

    return ret

def minimize_newtonlu(fun, x0, args=(), jac=None, hess=None, hessp=None,
                       callback=None, xtol=1e-5, eps=_epsilon, maxiter=None,
                       disp=False, return_all=False,
                       **unknown_options):
    """ Minimization of scalar function of one or more variables using the Newton-LU algorithm.

    .. note:: the `jac` parameter (Jacobian) is required.

    Args:
      disp (bool): Set to True to print convergence messages.
      xtol (float): Average relative error in solution `xopt` acceptable for
        convergence.
      maxiter (int): Maximum number of iterations to perform.
      eps (float or ndarray): If `jac` is approximated, use this value
        for the step size.
    """
    if jac is None:
        raise ValueError('Jacobian is required for Newton-LU method')
    f = fun
    fprime = jac
    fhess_p = hessp
    fhess = hess
    avextol = xtol
    epsilon = eps
    retall = return_all

    x0 = np.asarray(x0).flatten()
    fcalls, f = wrap_function(f, args)
    gcalls, fprime = wrap_function(fprime, args)
    hcalls = 0
    if maxiter is None:
        maxiter = len(x0)*200

    xtol = len(x0) * avextol
    update = [2 * xtol]
    xk = x0
    if retall:
        allvecs = [xk]
    k = 0
    old_fval = f(x0)
    old_old_fval = None
    float64eps = np.finfo(np.float64).eps
    warnflag = 0

    while (np.add.reduce(np.abs(update)) > xtol) and (k < maxiter):
        # Compute a search direction pk by applying the CG method to
        #  del2 f(xk) p = - grad f(xk) starting from 0.
        b = -fprime(xk)

        if fhess is not None:             # you want to compute hessian once.
            A = fhess(*(xk,) + args)
            hcalls = hcalls + 1
            #Now we need to check if the Hessian is positive definite.
            #If not, we will first try to modify it a certain number of times to make it positive definite.
            #After this number of trials we will revert to the steepest descent search direction
            Lchol, success, counterIt = makeHessianPositive_Cholesky( A )
            if success == True: #Newton direction
               b_temp = scialg.solve_triangular(Lchol, b, trans=0, lower=True)
               pk = scialg.solve_triangular(Lchol, b_temp, trans='T', lower=True) # search direction is solution to system.
            else: #Steepest descent
               pk = b

        gfk = -b    # gradient at xk

        try:
            alphak, fc, gc, old_fval, old_old_fval, gfkp1 = \
                     _line_search_wolfe12(f, fprime, xk, pk, gfk,
                                          old_fval, old_old_fval)
        except _LineSearchError:
            # Line search failed to find a better solution.
            warnflag = 2
            break

        update = alphak * pk
        xk = xk + update        # upcast if necessary
        if callback is not None:
            callback(xk)
        if retall:
            allvecs.append(xk)
        k += 1

    fval = old_fval
    if warnflag == 2:
        msg = _status_message['pr_loss']
        if disp:
            print("Warning: " + msg)
            print("         Current function value: %f" % fval)
            print("         Iterations: %d" % k)
            print("         Function evaluations: %d" % fcalls[0])
            print("         Gradient evaluations: %d" % gcalls[0])
            print("         Hessian evaluations: %d" % hcalls)
    elif k >= maxiter:
        warnflag = 1
        msg = _status_message['maxiter']
        if disp:
            print("Warning: " + msg)
            print("         Current function value: %f" % fval)
            print("         Iterations: %d" % k)
            print("         Function evaluations: %d" % fcalls[0])
            print("         Gradient evaluations: %d" % gcalls[0])
            print("         Hessian evaluations: %d" % hcalls)
    else:
        msg = _status_message['success']
        if disp:
            print(msg)
            print("         Current function value: %f" % fval)
            print("         Iterations: %d" % k)
            print("         Function evaluations: %d" % fcalls[0])
            print("         Gradient evaluations: %d" % gcalls[0])
            print("         Hessian evaluations: %d" % hcalls)

    result = OptimizeResult(fun=fval, jac=gfk, nfev=fcalls[0], njev=gcalls[0],
                            nhev=hcalls, status=warnflag,
                            success=(warnflag == 0), message=msg, x=xk,
                            nit=k)
    if retall:
        result['allvecs'] = allvecs
    return result


def minimize_newtoncglu(fun, x0, args=(), jac=None, hess=None, hessp=None,
                       callback=None, xtol=1e-5, eps=_epsilon, maxiter=None,
                       disp=False, return_all=False,
                       **unknown_options):
    """ Minimization of scalar function of one or more variables using the Newton-LU algorithm.

    .. note:: the `jac` parameter (Jacobian) is required.

    Args:
      disp (bool): Set to True to print convergence messages.
      xtol (float): Average relative error in solution `xopt` acceptable for
        convergence.
      maxiter (int): Maximum number of iterations to perform.
      eps (float or ndarray): If `jac` is approximated, use this value
        for the step size.
    """
    if jac is None:
        raise ValueError('Jacobian is required for Newton-LU method')
    f = fun
    fprime = jac
    fhess_p = hessp
    fhess = hess
    avextol = xtol
    epsilon = eps
    retall = return_all

    x0 = np.asarray(x0).flatten()
    fcalls, f = wrap_function(f, args)
    gcalls, fprime = wrap_function(fprime, args)
    hcalls = 0
    if maxiter is None:
        maxiter = len(x0)*200

    xtol = len(x0) * avextol
    update = [2 * xtol]
    xk = x0
    if retall:
        allvecs = [xk]
    k = 0
    old_fval = f(x0)
    old_old_fval = None
    float64eps = np.finfo(np.float64).eps
    warnflag = 0

    #### CG-ITERATION #####

    while (np.add.reduce(np.abs(update)) > xtol) and (k < maxiter):
        # Compute a search direction pk by applying the CG method to
        #  del2 f(xk) p = - grad f(xk) starting from 0.
        b = -fprime(xk)

        #Options iterative solver?
        maggrad = np.add.reduce(np.abs(b))
        eta = np.min([0.5, np.sqrt(maggrad)])
        termcond = eta * maggrad
        xsupi = np.zeros(len(x0), dtype=x0.dtype)
        ri = -b
        psupi = -ri
        i = 0
        dri0 = np.dot(ri, ri)

        if fhess is not None:             # you want to compute hessian once.
            A = fhess(*(xk,) + args)
            hcalls = hcalls + 1

        while np.add.reduce(np.abs(ri)) > termcond:
            if fhess is None:
                if fhess_p is None:
                    Ap = approx_fhess_p(xk, psupi, fprime, epsilon)
                else:
                    Ap = fhess_p(xk, psupi, *args)
                    hcalls = hcalls + 1
            else:
                Ap = np.dot(A, psupi)
            # check curvature
            Ap = np.asarray(Ap).squeeze()  # get rid of matrices...
            curv = np.dot(psupi, Ap)
            if 0 <= curv <= 3 * float64eps:
                break
            elif curv < 0:
                if (i > 0):
                    break
                else:
                    # fall back to steepest descent direction
                    xsupi = dri0 / (-curv) * b
                    break
            alphai = dri0 / curv
            xsupi = xsupi + alphai * psupi
            ri = ri + alphai * Ap
            dri1 = np.dot(ri, ri)
            betai = dri1 / dri0
            psupi = -ri + betai * psupi
            i = i + 1
            dri0 = dri1          # update np.dot(ri,ri) for next time.

        pk = xsupi  # search direction is solution to system.
        gfk = -b    # gradient at xk

        try:
            alphak, fc, gc, old_fval, old_old_fval, gfkp1 = \
                     _line_search_wolfe12(f, fprime, xk, pk, gfk,
                                          old_fval, old_old_fval)
        except _LineSearchError:
            # Line search failed to find a better solution.
            warnflag = 2
            break

        update = alphak * pk
        xk = xk + update        # upcast if necessary
        if callback is not None:
            callback(xk)
        if retall:
            allvecs.append(xk)
        k += 1

    #### EXACT LU-ITERATION #####
    update = [2 * xtol]
    while (np.add.reduce(np.abs(update)) > xtol) and (k < maxiter):
        # Compute a search direction pk by applying the CG method to
        #  del2 f(xk) p = - grad f(xk) starting from 0.
        b = -fprime(xk)

        if fhess is not None:             # you want to compute hessian once.
            A = fhess(*(xk,) + args)
            hcalls = hcalls + 1
            #Now we need to check if the Hessian is positive definite.
            #If not, we will first try to modify it a certain number of times to make it positive definite.
            #After this number of trials we will revert to the steepest descent search direction
            Lchol, success, counterIt = makeHessianPositive_Cholesky( A )
            if success == True: #Newton direction
               b_temp = scialg.solve_triangular(Lchol, b, trans=0, lower=True)
               pk = scialg.solve_triangular(Lchol, b_temp, trans='T', lower=True) # search direction is solution to system.
            else: #Steepest descent
               pk = b

        gfk = -b    # gradient at xk

        try:
            alphak, fc, gc, old_fval, old_old_fval, gfkp1 = \
                     _line_search_wolfe12(f, fprime, xk, pk, gfk,
                                          old_fval, old_old_fval)
        except _LineSearchError:
            # Line search failed to find a better solution.
            warnflag = 2
            break

        update = alphak * pk
        xk = xk + update        # upcast if necessary
        if callback is not None:
            callback(xk)
        if retall:
            allvecs.append(xk)
        k += 1


    fval = old_fval
    if warnflag == 2:
        msg = _status_message['pr_loss']
        if disp:
            print("Warning: " + msg)
            print("         Current function value: %f" % fval)
            print("         Iterations: %d" % k)
            print("         Function evaluations: %d" % fcalls[0])
            print("         Gradient evaluations: %d" % gcalls[0])
            print("         Hessian evaluations: %d" % hcalls)
    elif k >= maxiter:
        warnflag = 1
        msg = _status_message['maxiter']
        if disp:
            print("Warning: " + msg)
            print("         Current function value: %f" % fval)
            print("         Iterations: %d" % k)
            print("         Function evaluations: %d" % fcalls[0])
            print("         Gradient evaluations: %d" % gcalls[0])
            print("         Hessian evaluations: %d" % hcalls)
    else:
        msg = _status_message['success']
        if disp:
            print(msg)
            print("         Current function value: %f" % fval)
            print("         Iterations: %d" % k)
            print("         Function evaluations: %d" % fcalls[0])
            print("         Gradient evaluations: %d" % gcalls[0])
            print("         Hessian evaluations: %d" % hcalls)

    result = OptimizeResult(fun=fval, jac=gfk, nfev=fcalls[0], njev=gcalls[0],
                            nhev=hcalls, status=warnflag,
                            success=(warnflag == 0), message=msg, x=xk,
                            nit=k)
    if retall:
        result['allvecs'] = allvecs
    return result




##################### Auxiliary functions #############################################

def wrap_function(function, args):
    ncalls = [0]
    if function is None:
        return ncalls, None

    def function_wrapper(*wrapper_args):
        ncalls[0] += 1
        return function(*(wrapper_args + args))

    return ncalls, function_wrapper


def makeHessianPositive_Cholesky( hess, beta = 1e-3 , maxIt = 10, prodFactor = 2 ):
  # From "Numerical Optimization" Nocedal & Wright pg.51

  if isSymMatrix( hess )==False:
     hess = closestSymMatrix( hess ) # Force symmetry
  diagHess = np.diag(hess)
  dim = len(diagHess)
  hess_temp = np.copy(hess)

  #Decide initial shift
  if np.min(diagHess) > 0:
     tau = 0
  else:
     tau = - np.min(diagHess) + beta

  counterIt = 0
  flag = False

  while  (flag == False and counterIt<maxIt):
    hess_temp[:,:] = hess  # Assign original hessian
    diag_view = np.diagonal(hess_temp)
    diag_view.setflags(write=True)
    diag_view += tau  # hess + tau*Id


    try:
      Lchol = np.linalg.cholesky(hess_temp)
      flag = True
    except LinAlgError:
      pass

    tau = max( prodFactor*tau, beta )
    counterIt += 1 # Update counter

    if flag == True:
      success = True
    else:
      success = False
      Lchol=0

  return Lchol, success, counterIt-1

def closestSymMatrix( A ):
  # Override the square matrix A with the closest symmetric matrix in the Frobenius norm(A+A^T) /2
  return (A+ np.transpose(A))/2


def isSymMatrix( A ):
  return (A.transpose() == A).all()


