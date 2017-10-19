import numpy

from procgraph import simple_block

# Taken from the numpy cookbook


@simple_block
def smooth1d(x, window_len=11, window='hanning'):
    """
    Smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    ``window`` must be one of  'flat', 'hanning', 'hamming', 'bartlett', 
    'blackman'.
    A flat window will produce a moving average smoothing.

    
    :param x: the input signal 
    :param window_len: the dimension of the smoothing window;  an odd integer
    :param window: the type of window from 
    :return: smoothed: the smoothed signal
        
    example: ::

        t=linspace(-2,2,0.1)
        x=sin(t)+randn(len(t))*0.1
        y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, 
    numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an 
          array instead of a string   
    """

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")

    if window_len < 3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError(
                        "Window %r is not one of 'flat', 'hanning', 'hamming',"
                         "'bartlett', 'blackman'." % window)

    s = numpy.r_[2 * x[0] - x[window_len:1:-1],
                 x,
                 2 * x[-1] - x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w = numpy.ones(window_len, 'd')
    else:
        w = eval('numpy.' + window + '(window_len)')

    y = numpy.convolve(w / w.sum(), s, mode='same')
    return y[window_len - 1:-window_len + 1]


