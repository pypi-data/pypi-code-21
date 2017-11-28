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

import numpy as np
import numpy.linalg as npla
import scipy.stats as stats
import scipy.signal as signal

__all__ = ['ess']

def ess(samps, quantile=0.99, do_xcorr=False,
        plotting=False, plot_lag=50, fig=None):
    r""" Compute the Effective Sample Size (ESS) of a sample

    The minimum ESS over all the dimension is returned.
    Cross-correlation can be optionally used as well in the determination of
    the ESS.
    Plotting of the correlation decay can be shown.

    The ESS is computed as :math:`\lfloor m/\kappa \rfloor`, where

    .. math::

       \kappa = 1 + \sum_{c_i>b_i} c_i \;,

    :math:`c_i` is the auto-correlation at lag :math:`i` and
    :math:`b_i` is the ``quantile``-confidence interval for the
    :math:`i`-th value of auto-correlation
    (i.e. only significant auto-correlation values are summed up).

    Args:
      samps (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]):
        :math:`d`-dimensional sample on which to compute the ESS
      quantile (float): condifence interval quantile
      do_xcorr (bool): whether to compute and use the auto-correlation function
      plotting (bool): whether to plot auto/cross-correlation decays
      plot_lag (int): how many lags to plot
      fig (figure): handle to a figure

    Returns:
      (:class:`int`) -- minimum ESS across the :math:`d` dimensions
    """
    nsamps = samps.shape[0]
    dim = samps.shape[1]
    xcorr = []
    abs_xcorr = []
    for d1 in range(dim):
        if do_xcorr:
            for d2 in range(d1+1):
                s1 = samps[:,d1] - np.mean(samps[:,d1])
                s2 = samps[:,d2] - np.mean(samps[:,d2])
                s1 /= npla.norm(s1)
                s2 /= npla.norm(s2)
                # c = np.correlate(s1, s2, mode='full')[nsamps-1:]
                c = signal.correlate(s1, s2, mode='full')[nsamps-1:]
                xcorr.append(c)
                abs_xcorr.append( np.abs(xcorr[-1]) )
        else:
            s = samps[:,d1] - np.mean(samps[:,d1])
            s /= npla.norm(s)
            # c = np.correlate(s, s, mode='full')[nsamps-1:]
            c = signal.correlate(s, s, mode='full')[nsamps-1:]
            xcorr.append(c)
            abs_xcorr.append( np.abs(xcorr[-1]) )
    # Confidence interval
    var = 1. / np.arange(nsamps, 0, -1)
    alpha = 1. - (1. - quantile)/2.
    confint = stats.norm.ppf(alpha) * np.sqrt(var)
    # ESS
    ess = []
    min_ess = nsamps
    for axc in abs_xcorr:
        sig_corr = axc[axc >= confint]
        kappa = 1. + 2. * np.sum(sig_corr[1:])
        ess.append( int(floor( float(nsamps) / kappa ) ) )
        if ess[-1] < min_ess:
            min_ess = ess[-1]
    if plotting:
        import matplotlib.pyplot as plt
        if fig is None:
            fig = plt.figure()
        ax_list = []
        if do_xcorr:
            for d1 in range(dim):
                for d2 in range(dim):
                    if d2 <= d1:
                        ax_list.append( fig.add_subplot(dim,dim,d1*dim+d2+1) )
        else:
            for d1 in range(dim):
                ax_list.append( fig.add_subplot(1,dim,d1+1) )
        for ax, c in zip(ax_list, xcorr):
            ax.vlines(range(plot_lag+1), np.zeros(plot_lag+1), c[:plot_lag+1])
            ax.plot(confint[:plot_lag+1], '--r')
            ax.plot(-confint[:plot_lag+1], '--r')
            ax.tick_params(
                axis='x',          # changes apply to the x-axis
                which='both',      # both major and minor ticks are affected
                bottom='off',      # ticks along the bottom edge are off
                top='off',         # ticks along the top edge are off
                labelbottom='off') # labels along the bottom edge are off
            ax.tick_params(
                axis='y',          # changes apply to the x-axis
                which='both',      # both major and minor ticks are affected
                left='off',        # ticks along the bottom edge are off
                right='off',       # ticks along the top edge are off
                labelleft='off')   # labels along the bottom edge are off
        plt.tight_layout()
    return min_ess