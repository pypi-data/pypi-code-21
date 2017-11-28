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

import warnings
import numpy as np

import TransportMaps as TM

__all__ = ['Distribution',
           'ProductDistribution',
           'ConditionalDistribution',
           'FactorizedDistribution']

class Distribution(TM.TMO):
    r""" Abstract distribution :math:`\nu_\pi`.

    Args:
      dim (int): input dimension of the distribution
    """
    def __init__(self, dim):
        super(Distribution, self).__init__()
        self._dim = dim

    @property
    def dim(self):
        return self._dim

    @dim.setter
    def dim(self, dim):
        self._dim = dim

    def rvs(self, m, *args, **kwargs):
        r""" [Abstract] Generate :math:`m` samples from the distribution.

        Args:
          m (int): number of samples to generate

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- :math:`m`
             :math:`d`-dimensional samples

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    def quadrature(self, qtype, qparams, *args, **kwargs):
        r""" [Abstract] Generate quadrature points and weights.

        Args:
          qtype (int): quadrature type number. The different types are defined in
            the associated sub-classes.
          qparams (object): inputs necessary to the generation of the selected
            quadrature

        Return:
          (:class:`tuple` (:class:`ndarray<numpy.ndarray>` [:math:`m,d`],
            :class:`ndarray<numpy.ndarray>` [:math:`m`])) -- list of quadrature
            points and weights

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    def pdf(self, x, params=None, idxs_slice=slice(None,None,None)):
        r""" Evaluate :math:`\pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`\pi`
            at the ``x`` points.

        Raises:
          NotImplementedError: the method calls :fun:`log_pdf`
        """
        return np.exp( self.log_pdf(x, params, idxs_slice) )

    def log_pdf(self, x, params=None, idxs_slice=slice(None,None,None)):
        r""" [Abstract] Evaluate :math:`\log \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`\log\pi`
            at the ``x`` points.

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    def grad_x_log_pdf(self, x, params=None, idxs_slice=slice(None,None,None)):
        r""" [Abstract] Evaluate :math:`\nabla_{\bf x} \log \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- values of
            :math:`\nabla_x\log\pi` at the ``x`` points.

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    def tuple_grad_x_log_pdf(self, x, params=None, idxs_slice=slice(None,None,None)):
        r""" [Abstract] Compute the tuple :math:`\left(\log \pi({\bf x}), \nabla_{\bf x} \log \pi({\bf x})\right)`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`tuple`) -- containing
            :math:`\left(\log \pi({\bf x}), \nabla_{\bf x} \log \pi({\bf x})\right)`

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        return (self.log_pdf(x, params, idxs_slice),
                self.grad_x_log_pdf(x, params, idxs_slice))

    def hess_x_log_pdf(self, x, params=None, idxs_slice=slice(None,None,None)):
        r""" [Abstract] Evaluate :math:`\nabla^2_{\bf x} \log \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) -- values of
            :math:`\nabla^2_x\log\pi` at the ``x`` points.

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    def mean_log_pdf(self):
        r""" [Abstract] Evaluate :math:`\mathbb{E}_{\pi}[\log \pi]`

        Returns:
          (float) -- :math:`\mathbb{E}_{\pi}[\log \pi]`

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

class ProductDistribution(Distribution):
    r""" Abstract distribution :math:`\nu(A_1\times\cdots\times A_n) = \nu_1(A_1)\cdots\nu_n(A_n)`
    """
    def get_component(self, avars):
        r""" [Abstract] return the measure :math:`\nu_{a_1}\times\cdots\times\nu_{a_k}`

        Args:
          avars (list): list of coordinates to extract from :math:`\nu`
        """
        raise NotImplementedError("To be implemented in subclasses")

class ConditionalDistribution(Distribution):
    r""" Abstract distribution :math:`\pi_{{\bf X}\vert{\bf Y}}`.

    Args:
      dim (int): input dimension of the distribution
      dim_y (int): dimension of the conditioning variables
    """
    def __init__(self, dim, dim_y):
        super(ConditionalDistribution, self).__init__(dim)
        self._dim_y = dim_y

    @property
    def dim_y(self):
        return self._dim_y

    @dim_y.setter
    def dim_y(self, dim_y):
        self._dim_y = dim_y
    
        
    def rvs(self, m, y, *args, **kwargs):
        r""" [Abstract] Generate :math:`m` samples from the distribution.

        Args:
          m (int): number of samples to generate
          y (:class:`ndarray<numpy.ndarray>` [:math:`d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- :math:`m`
             :math:`d`-dimensional samples

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    def quadrature(self, qtype, qparams, y, *args, **kwargs):
        r""" [Abstract] Generate quadrature points and weights.

        Args:
          qtype (int): quadrature type number. The different types are defined in
            the associated sub-classes.
          qparams (object): inputs necessary to the generation of the selected
            quadrature
          y (:class:`ndarray<numpy.ndarray>` [:math:`d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`

        Return:
          (:class:`tuple` (:class:`ndarray<numpy.ndarray>` [:math:`m,d`],
            :class:`ndarray<numpy.ndarray>` [:math:`m`])) -- list of quadrature
            points and weights

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    def pdf(self, x, y, params=None, idxs_slice=slice(None,None,None)):
        r""" Evaluate :math:`\pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`\pi`
            at the ``x`` points.

        Raises:
          NotImplementedError: the method calls :fun:`log_pdf`
        """
        return np.exp( self.log_pdf(x, y, params, idxs_slice) )

    def log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None)):
        r""" [Abstract] Evaluate :math:`\log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- values of :math:`\log\pi`
            at the ``x`` points.

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    def grad_x_log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None)):
        r""" [Abstract] Evaluate :math:`\nabla_{\bf x,y} \log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- values of
            :math:`\nabla_x\log\pi` at the ``x`` points.

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    def tuple_grad_x_log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None)):
        r""" Evaluate :math:`\left(\log \pi({\bf x}\vert{\bf y}), \nabla_{\bf x,y} \log \pi({\bf x}\vert{\bf y})\right)`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`tuple`) -- containing
            :math:`\left(\log \pi({\bf x}\vert{\bf y}), \nabla_{\bf x,y} \log \pi({\bf x}\vert{\bf y})\right)`

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        return (self.log_pdf(x, y, params, idxs_slice),
                self.grad_x_log_pdf(x, y, params, idxs_slice))

    def hess_x_log_pdf(self, x, y, params=None, idxs_slice=slice(None,None,None)):
        r""" [Abstract] Evaluate :math:`\nabla^2_{\bf x,y} \log \pi({\bf x}\vert{\bf y})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          y (:class:`ndarray<numpy.ndarray>` [:math:`m,d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) -- values of
            :math:`\nabla^2_x\log\pi` at the ``x`` points.

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

    def mean_log_pdf(self, y):
        r""" [Abstract] Evaluate :math:`\mathbb{E}_{\pi}[\log \pi]`

        Args:
          y (:class:`ndarray<numpy.ndarray>` [:math:`d_y`]): conditioning values
            :math:`{\bf Y}={\bf y}`
        
        Returns:
          (float) -- :math:`\mathbb{E}_{\pi}[\log \pi]`

        Raises:
          NotImplementedError: the method needs to be defined in the sub-classes
        """
        raise NotImplementedError("The method is not implemented for this distribution")

        
class FactorizedDistribution(Distribution):
    r""" Distribution :math:`\nu_\pi` defiened by its conditional factors.

    The density of the distribution :math:`\nu_\pi` is defined by

    .. math::

       \pi({\bf x}) = \prod_{({\bf i},{\bf k}) \in \mathcal{I}} \pi({\bf x}_{\bf i},{\bf x}_{\bf k})`

    Args:
      factors (:class:`list` of :class:`tuple`): each tuple contains a factor
        (:class:`ConditionalDistribution` and/or :class:`Distribution`), and two lists
        containing the list of marginal variables and conditioning variables

    Example
    -------
    Let :math:`\pi(x_0,x_1,x_2) = \pi_1(x_2|x_1,x_0) \pi_2(x_0|x_1) \pi_3(x_1)`.

    >>> factors = [(p1, [2], [1,0] ),
    >>>            (p2, [0], [1]  ),
    >>>            (p3, [1], []    )]
    >>> pi = FactorizedDistribution(factors)
    
    """
    def __init__(self, factors):
        input_dim = []
        self.factors = []
        for i, (pi, xidxs, yidxs) in enumerate(factors):
            if issubclass(type(pi), ConditionalDistribution):
                is_cond = True
            elif issubclass(type(pi), Distribution):
                is_cond = False
            else:
                raise TypeError("The %d-th factor is nor " % i + \
                                "Distribution or ConditionalDistribution")
            # pi has right number of inputs
            if len(set(xidxs)) != pi.dim:
                raise TypeError("The dimension of the %d-th " % i + \
                                "distribution does not match the input variables.")
            if is_cond and len(set(yidxs)) != pi.dim_y:
                raise TypeError("The conditioning dimension of the %d-th " % i + \
                                "distribution does not match the input variables.")
            if not is_cond and len(yidxs) != 0:
                raise TypeError("The conditioning dimension of the %d-th " % i + \
                                "distribution (Distribution) must be zero.")
            self.factors.append( (is_cond, pi, xidxs, yidxs) )
            input_dim.extend( xidxs )
        # Check total dimension and that all the marginals are available
        if len(input_dim) != len(set(input_dim)) or \
           (len(input_dim) != 0 and len(input_dim) != max(input_dim)+1):
            raise TypeError("Some marginals are not defined or multiply defined")
        super(FactorizedDistribution, self).__init__(len(input_dim))

    def append(self, factor):
        r""" Add a new factor to the distribution

        Args:
          factor (:class:`tuple`): tuple containing a factor
            (:class:`ConditionalDistribution` and/or :class:`Distribution`), and two
            tuples with the list of marginal variables and conditioning variables

        Example
        -------
        Let :math:`\pi(x_0,x_1,x_2) = \pi_1(x_2|x_1,x_0) \pi_2(x_0|x_1) \pi_3(x_1)` and let's
        add the factor :math:`\pi_4(x_3|x_0,x_1,x_2)`, obtaining:

        .. math::

           \pi(x_0,x_1,x_2,x_3) = \pi_4(x_3|x_0,x_1,x_2)\pi_1(x_2|x_1,x_0) \pi_2(x_0|x_1) \pi_3(x_1)

        >>> factor = (pi4, [3], [0,1,2])
        >>> pi.append(factor)
        
        """
        pi, xidxs, yidxs = factor
        if issubclass(type(pi), ConditionalDistribution):
            is_cond = True
        elif issubclass(type(pi), Distribution):
            is_cond = False
        else:
            raise TypeError("The factor is nor " + \
                            "Distribution or ConditionalDistribution")
        # pi has right number of inputs
        if len(xidxs) != pi.dim:
            raise TypeError("The dimension of the " + \
                            "distribution does not match the input variables.")
        if is_cond and len(yidxs) != pi.dim_y:
            raise TypeError("The conditioning dimension of the " + \
                            "distribution does not match the input variables.")
        if not is_cond and len(yidxs) != 0:
            raise TypeError("The conditioning dimension of the " + \
                            "distribution (Distribution) must be zero.")
        # Check xidxs contains new coordinates and that all the marginals are available
        if min(xidxs) < self.dim or len(xidxs) != len(set(xidxs)) or \
           self.dim + len(xidxs) != max(xidxs)+1:
            raise TypeError("Some marginals are not defined or multiply defined")
        self.factors.append( (is_cond, pi, xidxs, yidxs) )
        self.dim += len(xidxs)
        
    def log_pdf(self, x, params=None, idxs_slice=slice(None,None,None)):
        r""" [Abstract] Evaluate :math:`\log \pi({\bf x})`

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
        if x.shape[1] != self.dim:
            raise ValueError("The dimension of the input does not match the dimension " + \
                             "of the distribution")
        out = np.zeros(x.shape[0])
        for is_cond, pi, xidxs, yidxs in self.factors:
            if is_cond:
                out += pi.log_pdf(x[:,xidxs], x[:,yidxs],
                                  params=params, idxs_slice=idxs_slice)
            else:
                out += pi.log_pdf(x[:,xidxs], params=params, idxs_slice=idxs_slice)
        return out

    def grad_x_log_pdf(self, x, params=None, idxs_slice=slice(None,None,None)):
        r""" Evaluate :math:`\nabla_{\bf x} \log \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) -- values of
            :math:`\nabla_x\log\pi` at the ``x`` points.
        """
        if x.shape[1] != self.dim:
            raise ValueError("The dimension of the input does not match the dimension " + \
                             "of the distribution")
        out = np.zeros(x.shape)
        for is_cond, pi, xidxs, yidxs in self.factors:
            if is_cond:
                gx = pi.grad_x_log_pdf(x[:,xidxs], x[:,yidxs],
                                       params=params, idxs_slice=idxs_slice)
                out[:,yidxs] += gx[:,pi.dim:]
            else:
                gx = pi.grad_x_log_pdf(x[:,xidxs], params=params, idxs_slice=idxs_slice)
            out[:,xidxs] += gx[:,:pi.dim]
        return out

    def hess_x_log_pdf(self, x, params=None, idxs_slice=slice(None,None,None)):
        r""" Evaluate :math:`\nabla^2_{\bf x} \log \pi({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points
          params (dict): parameters
          idxs_slice (slice): if precomputed values are present, this parameter
            indicates at which of the points to evaluate. The number of indices
            represented by ``idxs_slice`` must match ``x.shape[0]``.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) -- values of
            :math:`\nabla^2_x\log\pi` at the ``x`` points.
        """
        if x.shape[1] != self.dim:
            raise ValueError("The dimension of the input does not match the dimension " + \
                             "of the distribution")
        m = x.shape[0]
        out = np.zeros( (m, self.dim, self.dim) )
        for is_cond, pi, xidxs, yidxs in self.factors:
            if is_cond:
                hx = pi.hess_x_log_pdf(x[:,xidxs], x[:,yidxs],
                                       params=params, idxs_slice=idxs_slice)
                out[np.ix_(range(m),xidxs,yidxs)] += hx[:,:pi.dim,pi.dim:]
                out[np.ix_(range(m),yidxs,xidxs)] += hx[:,pi.dim:,:pi.dim]
                out[np.ix_(range(m),yidxs,yidxs)] += hx[:,pi.dim:,pi.dim:]
            else:
                hx = pi.hess_x_log_pdf(x[:,xidxs], params=params, idxs_slice=idxs_slice)
            out[np.ix_(range(m),xidxs,xidxs)] += hx[:,:pi.dim,:pi.dim]
        return out
