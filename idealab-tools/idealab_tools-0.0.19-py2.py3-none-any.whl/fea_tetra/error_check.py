# -*- coding: utf-8 -*-
"""
copyright 2016-2017 Dan Aukes
"""

from idealab_tools.data_exchange import dat
import os

#differences = 
#b_filename = os.path.join(directory,'b.dat')
#B_filename = os.path.join(directory,'B_big.dat')
#W_filename = os.path.join(directory,'W.dat')
#M_filename = os.path.join(directory,'M.dat')
#u_filename = os.path.join(directory,'u.dat')
#x_filename = os.path.join(directory,'x.dat')
#A_filename = os.path.join(directory,'A.dat')
#
#b_matlab = dat.read(b_filename,float)
#B_matlab = dat.read(B_filename,float)
#W_matlab = dat.read(W_filename,float)
#M_matlab = dat.read(M_filename,float)
#u_matlab = dat.read(u_filename,float)
#x_matlab = dat.read(x_filename,float)
#A_matlab = dat.read(A_filename,float)
#
#b_error = (b-b_matlab).nonzero()
#B_error = (B-B_matlab).nonzero()
#W_error = (W-W_matlab).nonzero()
#M_error = (M-M_matlab).nonzero()
#u_error = (u-u_matlab).nonzero()
#x_error = (x-x_matlab).nonzero()
#A_error = (A_alt-A_matlab).nonzero()

def compare_matrices(A,filename,directory=None, format = float):
    directory = directory or ''
    full_path = os.path.normpath(os.path.abspath(os.path.join(directory,filename)))
    B=dat.read(full_path,format = format)
    return num_errors(A,B)

def num_errors(a,b,tol=1e-3):
    error = (a-b) > (abs(a).max()*tol)
    num_errors = len(error.nonzero()[0])
    return num_errors