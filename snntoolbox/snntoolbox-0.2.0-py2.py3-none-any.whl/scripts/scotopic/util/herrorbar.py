
import numpy as np
import scipy
import matcompat

# if available import pylab (from matlibplot)
try:
    import matplotlib.pylab as plt
except ImportError:
    pass

def herrorbar(x, y, l, u, symbol):

    # Local Variables: xl, xb, tee, hold_state, xr, esymbol, mark, ybot, next, ls, msg, symbol, yb, hh, npt, ytop, cax, h, m, l, n, u, y, x, col
    # Function calls: isempty, lower, zeros, abs, min, isstr, max, isequal, NaN, plot, ishold, nargin, length, ones, herrorbar, error, newplot, get, colstyle, nargout, size
    #%HERRORBAR Horizontal Error bar plot.
    #%   HERRORBAR(X,Y,L,R) plots the graph of vector X vs. vector Y with
    #%   horizontal error bars specified by the vectors L and R. L and R contain the
    #%   left and right error ranges for each point in X. Each error bar
    #%   is L(i) + R(i) long and is drawn a distance of L(i) to the right and R(i)
    #%   to the right the points in (X,Y). The vectors X,Y,L and R must all be
    #%   the same length. If X,Y,L and R are matrices then each column
    #%   produces a separate line.
    #%
    #%   HERRORBAR(X,Y,E) or HERRORBAR(Y,E) plots X with error bars [X-E X+E].
    #%   HERRORBAR(...,'LineSpec') uses the color and linestyle specified by
    #%   the string 'LineSpec'. See PLOT for possibilities.
    #%
    #%   H = HERRORBAR(...) returns a vector of line handles.
    #%
    #%   Example:
    #%      x = 1:10;
    #%      y = sin(x);
    #%      e = std(y)*ones(size(x));
    #%      herrorbar(x,y,e)
    #%   draws symmetric horizontal error bars of unit standard deviation.
    #%
    #%   This code is based on ERRORBAR provided in MATLAB.   
    #%
    #%   See also ERRORBAR
    #%   Jos van der Geest
    #%   email: jos@jasen.nl
    #%
    #%   File history:
    #%   August 2006 (Jos): I have taken back ownership. I like to thank Greg Aloe from
    #%   The MathWorks who originally introduced this piece of code to the
    #%   Matlab File Exchange. 
    #%   September 2003 (Greg Aloe): This code was originally provided by Jos
    #%   from the newsgroup comp.soft-sys.matlab:
    #%   http://newsreader.mathworks.com/WebX?50@118.fdnxaJz9btF^1@.eea3ff9
    #%   After unsuccessfully attempting to contact the orignal author, I
    #%   decided to take ownership so that others could benefit from finding it
    #%   on the MATLAB Central File Exchange.
    if matcompat.max(matcompat.size(x)) == 1.:
        npt = length(x)
        x = x.flatten(1)
        y = y.flatten(1)
        if nargin > 2.:
            if not isstr(l):
                l = l.flatten(1)
            
            
            if nargin > 3.:
                if not isstr(u):
                    u = u.flatten(1)
                
                
            
            
        
        
    else:
        [npt, n] = matcompat.size(x)
        
    
    if nargin == 3.:
        if not isstr(l):
            u = l
            symbol = '-'
        else:
            symbol = l
            l = y
            u = y
            y = x
            [m, n] = matcompat.size(y)
            x[:] = np.dot(np.arange(1., (npt)+1).conj().T, np.ones(1., n))
            
        
    
    
    if nargin == 4.:
        if isstr(u):
            symbol = u
            u = l
        else:
            symbol = '-'
            
        
    
    
    if nargin == 2.:
        l = y
        u = y
        y = x
        [m, n] = matcompat.size(y)
        x[:] = np.dot(np.arange(1., (npt)+1).conj().T, np.ones(1., n))
        symbol = '-'
    
    
    u = np.abs(u)
    l = np.abs(l)
    if np.logical_or(np.logical_or(np.logical_or(isstr(x), isstr(y)), isstr(u)), isstr(l)):
        matcompat.error('Arguments must be numeric.')
    
    
    if np.logical_or(np.logical_or(not isequal(matcompat.size(x), matcompat.size(y)), not isequal(matcompat.size(x), matcompat.size(l))), not isequal(matcompat.size(x), matcompat.size(u))):
        matcompat.error('The sizes of X, Y, L and U must be the same.')
    
    
    tee = (matcompat.max(y.flatten(1))-matcompat.max(y.flatten(1)))/10.
    #% make tee .02 x-distance for error bars
    #% changed from errorbar.m
    xl = x-l
    xr = x+u
    ytop = y+tee
    ybot = y-tee
    n = matcompat.size(y, 2.)
    #% end change
    #% Plot graph and bars
    hold_state = plt.ishold
    cax = newplot
    next = lower(plt.get(cax, 'NextPlot'))
    #% build up nan-separated vector for bars
    #% changed from errorbar.m
    xb = np.zeros((npt*9.), n)
    xb[0::9.,:] = xl
    xb[1::9.,:] = xl
    xb[2::9.,:] = NaN
    xb[3::9.,:] = xl
    xb[4::9.,:] = xr
    xb[5::9.,:] = NaN
    xb[6::9.,:] = xr
    xb[7::9.,:] = xr
    xb[8::9.,:] = NaN
    yb = np.zeros((npt*9.), n)
    yb[0::9.,:] = ytop
    yb[1::9.,:] = ybot
    yb[2::9.,:] = NaN
    yb[3::9.,:] = y
    yb[4::9.,:] = y
    yb[5::9.,:] = NaN
    yb[6::9.,:] = ytop
    yb[7::9.,:] = ybot
    yb[8::9.,:] = NaN
    #% end change
    [ls, col, mark, msg] = colstyle(symbol)
    if not isempty(msg):
        matcompat.error(msg)
    
    
    symbol = np.array(np.hstack((ls, mark, col)))
    #% Use marker only on data part
    esymbol = np.array(np.hstack(('-', col)))
    #% Make sure bars are solid
    h = plt.plot(xb, yb, esymbol)
    plt.hold(on)
    h = np.array(np.vstack((np.hstack((h)), np.hstack((plt.plot(x, y, symbol))))))
    if not hold_state:
        plt.hold(off)
    
    
    if nargout > 0.:
        hh = h
    
    
    return [hh]