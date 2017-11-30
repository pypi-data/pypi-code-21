from __future__ import division 
from uncertainties.umath import log as ulog

def fc_gc_dFdc_from_c(c):
    one_plus_c = 1+c
    two_plus_c = 2+c
    c_squared = c*c
    try:
        log_one_plus_c = ulog(one_plus_c)
    except TypeError:
        from numpy import log as nplog
        log_one_plus_c = nplog(one_plus_c)
    one_plus_c__times__log_opc = one_plus_c * log_one_plus_c
    one_plus_c__times__logsquare = one_plus_c__times__log_opc * log_one_plus_c
    fc = one_plus_c__times__logsquare - 2 * c * log_one_plus_c
    fc = fc + one_plus_c * c_squared / one_plus_c**2
    fc = fc / c / (0.5*(one_plus_c- 1/one_plus_c) - log_one_plus_c)

    dFdc = 2 * (one_plus_c__times__log_opc - c) 
    dFdc = dFdc * (c*(4+5*c+c_squared) * log_one_plus_c -c_squared *(2+3*c) - 2 * one_plus_c__times__logsquare)
    dFdc = -1 * dFdc /(c_squared * (c *two_plus_c-2*one_plus_c__times__log_opc)**2)
    return fc, dFdc
