from __future__ import division 
from math import pi
from EPIC.utils.numbers import G

def rho_critical(Hz):
    return 3*Hz**2/(8*pi*G)    # h^2 Msun Mpc^-3

def z_of_a(A):
    return 1/A - 1

