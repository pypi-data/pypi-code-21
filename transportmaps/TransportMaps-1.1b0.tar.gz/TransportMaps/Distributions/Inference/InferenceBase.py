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
# Authors: Transport Map Team
# Website: transportmaps.mit.edu
# Support: transportmaps.mit.edu/qa/
#

from TransportMaps.Distributions import Distribution

__all__ = ['BayesPosteriorDistribution']

class BayesPosteriorDistribution(Distribution):
    r""" Given a log-likelihood and a prior, assemble the posterior density

    Given the log-likelihood :math:`\log\pi({\bf y}\vert{\bf x})` and the
    prior density :math:`\pi({\bf x})`, assemble the Bayes' posterior density

    .. math::

      \pi({\bf x}\vert {\bf y}) \propto \pi({\bf y}\vert{\bf x}) \pi({\bf x})

    Args:
      logL (:class:`LogLikelihood<TransportMaps.Functionals.LogLikelihood>`):
        log-likelihood :math:`\log\pi({\bf y}\vert{\bf x})`
      prior (:class:`Distribution<TransportMaps.Distributions.Distribution>`):
        prior density :math:`\pi({\bf x})`
    """
    def __init__(self, logL, prior):
        super(BayesPosteriorDistribution, self).__init__(prior.dim)
        self.prior = prior
        self.logL = logL

    @property
    def observations(self):
        return self.logL.y

    def log_pdf(self, x, params=None, idxs_slice=slice(None,None,None)):
        r""" Evaluate :math:`\log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`\log\pi`
            at the ``x`` points.
        """
        return self.logL.evaluate(x, params, idxs_slice) \
            + self.prior.log_pdf(x, params, idxs_slice)

    def grad_x_log_pdf(self, x, params=None, idxs_slice=slice(None,None,None)):
        r""" Evaluate :math:`\nabla_{\bf x} \log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- values of
            :math:`\nabla_{\bf x}\log\pi` at the ``x`` points.
        """
        return self.logL.grad_x(x, params, idxs_slice) \
            + self.prior.grad_x_log_pdf(x, params, idxs_slice)

    def tuple_grad_x_log_pdf(self, x, params=None, idxs_slice=slice(None,None,None)):
        r""" Evaluate :math:`\left(\log \pi({\bf x}\vert{\bf y}), \nabla_{\bf x} \log \pi({\bf x}\vert{\bf y})\right)`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`tuple`) --
            :math:`\left(\log \pi({\bf x}\vert{\bf y}), \nabla_{\bf x} \log \pi({\bf x}\vert{\bf y})\right)`
        """
        ll, gxll = self.logL.tuple_grad_x(x, params, idxs_slice)
        lpr, gxlpr = self.prior.tuple_grad_x_log_pdf(x, params, idxs_slice)
        ev = ll + lpr
        gx = gxll + gxlpr
        return (ev, gx)

    def hess_x_log_pdf(self, x, params=None, idxs_slice=slice(None,None,None)):
        r""" Evaluate :math:`\nabla^2_{\bf x} \log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) -- values of
            :math:`\nabla^2_{\bf x}\log\pi` at the ``x`` points.
        """
        return self.logL.hess_x(x, params, idxs_slice) \
            + self.prior.hess_x_log_pdf(x, params, idxs_slice)

            