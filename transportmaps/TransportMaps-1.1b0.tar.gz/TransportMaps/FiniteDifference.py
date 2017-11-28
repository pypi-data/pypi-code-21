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

__all__ = ['check_der', 'check_grad_a', 'check_hess_a_from_grad_a',
           'check_action_hess_a_from_grad_a', 'check_grad_x',
           'check_hess_x_from_grad_x', 'grad_a_fd', 'grad_x_fd',
           'grad_x_fx',]

import numpy as np
import time

def check_der(f, dx_f, x, dx, params, title='', verbose=True):
    maxerr = np.max(np.abs(dx_fdapprox(f,x,dx,params) - dx_f(x,params)))
    if verbose:
        print("Check der %s - Max err: %e" % (title,maxerr))

def check_grad_a(f, grad_f, x, dx, params, end=True, title='', verbose=True):
    app_start = time.clock()
    app = grad_a_fd(f,x,dx,params,end)
    app_stop = time.clock()
    app_time = app_stop-app_start
    exa_start = time.clock()
    exa = grad_f(x,params)
    exa_stop = time.clock()
    exa_time = exa_stop - exa_start
    err = np.abs(app-exa).flatten()
    idxmer = np.argmax(err)
    maxerr = err[idxmer]
    if not np.allclose(exa, app, rtol=100*dx, atol=10*dx):
        print('Max err: %e. Abs: %e. rtol: %e. atol: %e' % (
            maxerr, exa.flatten()[idxmer], 100*dx, 10*dx))
    if verbose:
        print("Check grad %s - Max err: %e - FD time: %.4f - Analytic time: %.4f" % (
            title,maxerr,app_time,exa_time))
    return np.allclose(exa, app, rtol=100*dx, atol=10*dx)

def check_hess_a_from_grad_a(grad_f, hess_f, x, dx, params, title='', verbose=True):
    exa_start = time.clock()
    exa = hess_f(x,params)
    exa_stop = time.clock()
    exa_time = exa_stop - exa_start
    app_start = time.clock()
    app = grad_a_fd(grad_f, x, dx, params)
    app_stop = time.clock()
    app_time = app_stop-app_start
    err = np.abs(app-exa).flatten()
    maxerr = np.max(err)
    if verbose:
        print("Check hess %s - Max err: %e - FD time: %.4f - Analytic time: %.4f" % (
            title,maxerr, app_time,exa_time))
    return np.allclose(exa, app, rtol=100*dx, atol=10*dx)

def check_action_hess_a_from_grad_a(grad_f, action_hess_f, x, dx, v, params, title='', verbose=True):
    exa_start = time.clock()
    exa = action_hess_f(x, v, params)
    exa_stop = time.clock()
    exa_time = exa_stop - exa_start
    app_start = time.clock()
    app = grad_a_fd(grad_f, x, dx, params)
    app = np.dot(app, v)
    app_stop = time.clock()
    app_time = app_stop-app_start
    err = np.abs(app-exa).flatten()
    maxerr = np.max(err)
    if verbose:
        print("Check hess %s - Max err: %e - FD time: %.4f - Analytic time: %.4f" % (
            title,maxerr,app_time,exa_time))
    return np.allclose(exa, app, rtol=100*dx, atol=10*dx)
    
def check_grad_x(f, grad_f, x, dx, params, title='', verbose=True):
    app_start = time.clock()
    app = grad_x_fd(f,x,dx,params)
    app_stop = time.clock()
    app_time = app_stop-app_start
    exa_start = time.clock()
    exa = grad_f(x,params)
    exa_stop = time.clock()
    exa_time = exa_stop - exa_start
    err = np.abs(app-exa).flatten()
    maxerr = np.max(err)
    if verbose:
        print("Check grad %s - Max err: %e - FD time: %.4f - Analytic time: %.4f" % (
            title,maxerr,app_time,exa_time))
    return np.allclose(exa, app, rtol=100*dx, atol=10*dx)

def check_hess_x_from_grad_x(grad_f, hess_f, x, dx, params, title='', verbose=True):
    exa_start = time.clock()
    exa = hess_f(x,params)
    exa_stop = time.clock()
    exa_time = exa_stop - exa_start
    app_start = time.clock()
    app = grad_x_fd(grad_f, x, dx, params)
    app_stop = time.clock()
    app_time = app_stop-app_start
    err = np.abs(app-exa).flatten()
    maxerr = np.max(err)
    if verbose:
        print("Check hess %s - Max err: %e - FD time: %.4f - Analytic time: %.4f" % (title,maxerr,
                                                                                     app_time,exa_time))
    # return np.allclose(exa, app, rtol=100*dx, atol=10*dx)
    return np.allclose(exa, app, rtol=dx, atol=dx)

def grad_a_fd(f, x, dx, params, end=True):
    tmp = f(x, params)
    if isinstance(tmp, float): extradims = 0
    else: extradims = tmp.ndim
    if end:
        out = np.zeros(tmp.shape + (len(x),))
    else:
        out = np.zeros(tmp.shape[:1] + (len(x),) + tmp.shape[1:])
    idxbase = tuple( [slice(None)]* extradims )
    for i in range(len(x)):
        xc_minus = x.copy()
        xc_plus = x.copy()
        xc_minus[i] -= dx/2.
        xc_plus[i] += dx/2.
        fm = f(xc_minus, params)
        fp = f(xc_plus, params)
        if end:
            out[idxbase + (i,)] = (fp-fm)/dx
        else:
            idx = (idxbase[:1] + (i,) + idxbase[1:])
            out[idx] = (fp-fm)/dx
    return out

def grad_x_fd(f, x, dx, params=None):
    r""" Compute :math:`\nabla_{\bf x} f({\bf x})` of :math:`f:\mathbb{R}^d\rightarrow\mathbb{R}`
    """
    tmp = f(x, params)
    if isinstance(tmp, float): extradims = 0
    else: extradims = tmp.ndim
    nsamp = x.shape[0]
    dim = x.shape[1]
    out = np.zeros(tmp.shape + (dim,))
    idxbase = tuple( [slice(None)]* extradims )
    for i in range(dim):
        xcm = x.copy()
        xcp = x.copy()
        xcm[:,i] -= dx/2.
        xcp[:,i] += dx/2.
        fm = f(xcm, params)
        fp = f(xcp, params)
        out[idxbase + (i,)] = (fp-fm)/dx
    return out

def grad_x_fx(f, x, dx):
    r""" Compute :math:`\nabla_{\bf x} f_{\bf x}({\bf x})` of :math:`f_{\bf x}:\mathbb{R}^d\rightarrow\mathbb{R}^d`
    """
    nsamp = x.shape[0]
    dim = x.shape[1]
    out = np.zeros((nsamp,dim,dim))
    for i in range(dim):
        xcm = x.copy()
        xcp = x.copy()
        xcm[:,i] -= dx/2.
        xcp[:,i] += dx/2.
        fm = f(xcm)
        fp = f(xcp)
        out[:,:,i] = (fp-fm)/dx
    return out
