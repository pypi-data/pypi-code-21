from __future__ import division 
from math import pi, log

# constants of nature
speedoflight = 299792458. # in m/s
G = 4.3021135e-9 # in units of Mpc Msun**-1 (km/s)**2
mH = 1.67262178e-27 # in units of kg 

# common numbers
log2pi = log(2*pi)
ln10 = log(10)

# units conversion
keV = 1.602176565e-22 # in units of kg (km/s)**2
kg = 1/keV # in units of keV (km/s)**-2
mumH = mH * kg * 0.63
GmumH = G * mumH

# statistics
CL68 = 0.682689492137086
CL95 = 0.954499736103642
CL997 = 0.997300203936740
CL999 = 0.999936657516334

#dict_sigmaCL = lambda n: 1 - 2 * scipy_stats_standard_normal.cdf(-n)
dict_sigmaCL = dict(zip(range(1, 5), [CL68, CL95, CL997, CL999]))
