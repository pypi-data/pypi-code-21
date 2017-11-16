#!/usr/bin/env python
#     DStat Interface - An interface for the open hardware DStat potentiostat
#     Copyright (C) 2014  Michael D. M. Dryden - 
#     Wheeler Microfluidics Laboratory <http://microfluidics.utoronto.ca>
#         
#     
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#     
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#     
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Creates data plot.
"""
try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
except ImportError:
    print "ERR: GTK not available"
    sys.exit(1)
    
from matplotlib.figure import Figure

from matplotlib.backends.backend_gtk3agg \
    import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.backends.backend_gtk3 \
    import NavigationToolbar2GTK3 as NavigationToolbar
try:
    import seaborn as sns
except ImportError:
    pass
    
from numpy import sin, linspace, pi, mean, trapz
from scipy import fft, arange

def plotSpectrum(y,Fs):
    """
    Plots a Single-Sided Amplitude Spectrum of y(t)
    """    
    y = y-mean(y)
    n = len(y) # length of the signal
    k = arange(n)
    T = n/Fs
    frq = k/T # two sides frequency range
    frq = frq[range(n/2)] # one side frequency range
    Y = fft(y)/n # fft computing and normalization
    Y = abs(Y[range(n/2)])
    
    return (frq, Y)

def integrateSpectrum(x, y, target, bandwidth):
    """
    Returns integral of range of bandwidth centered on target (both in Hz).
    """
    j = 0
    k = len(x)
    
    for i in range(len(x)):
        if x[i] >= target-bandwidth/2:
            j = i
            break
            
    for i in range(j,len(x)):
        if x[i] >= target+bandwidth/2:
            k = i
            break
        
    return trapz(y=y[j:k], x=x[j:k])
    
def findBounds(y):
    start_index = 0;
    stop_index = len(y)-1;
    
    for i in range(len(y)):
        if (y[i] <= mean(y) and y[i+1] > mean(y)):
            start_index = i
            break
    
    for i in range(len(y)):
        if (y[-(i+1)] <= mean(y) and y[-i] > mean(y)):
            stop_index = len(y)-1-i  # len(y) is last index + 1
            break
    
    return (start_index, stop_index)

