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

import numpy as np
import scipy.stats as stats

from TransportMaps.Functionals.MonotonicFunctionApproximations import *

__all__ = ['MonotonicFrozenFunction', 'FrozenLinear',
           'FrozenExponential', 'FrozenGaussianToUniform']

class MonotonicFrozenFunction(MonotonicFunctionApproximation):
    r""" [Abstract] Frozen function. No optimization over the coefficients allowed.
    """
    def precomp_evaluate(self, x, *args, **kwargs):
        return {}

    def precomp_grad_x(self, x, *args, **kwargs):
        return {}

    def precomp_hess_x(self, x, *args, **kwargs):
        return {}

    def precomp_partial_xd(self, x, *args, **kwargs):
        return {}

    def precomp_grad_x_partial_xd(self, x, *args, **kwargs):
        return {}

    def precomp_hess_x_partial_xd(self, x, *args, **kwargs):
        return {}

    def precomp_partial2_xd(self, x, *args, **kwargs):
        return {}

class FrozenLinear(MonotonicFrozenFunction):
    r""" Frozen Linear map :math:`{\bf x} \rightarrow a_1 + a_2 {\bf x}_d`

    Args:
      dim (int): input dimension :math:`d`
      a1 (int): coefficient :math:`a_1`
      a2 (int): coefficient :math:`a_2`
    """

    def __init__(self, dim, a1, a2):
        self.dim = dim
        self.set_coeffs(a1, a2)

    @property
    def n_coeffs(self):
        r"""
        Returns: 2
        """
        return 2

    def set_coeffs(self, a1, a2):
        r""" Set coefficients :math:`a_1` and :math:`a_2`. """
        if a2 < 0.:
            raise ValueError("The map is not monotone")
        self.a1 = a1
        self.a2 = a2

    def evaluate(self, x, *args, **kwargs):
        r""" Evaluate :math:`f_{\bf a}({\bf x}) = a_1 + a_2 {\bf x}_d`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- function value at points `x`
        """
        return self.a1 + self.a2 * x[:,-1]

    def grad_x(self, x, *args, **kwargs):
        r""" Evaluate :math:`\nabla_{\bf x} f_{\bf a}({\bf x})`

        This is:

        .. math::

           \nabla_{\bf x} f_{\bf a}({\bf x}) = \begin{bmatrix}
           \partial_{{\bf x}_1} f_{\bf a}({\bf x}) \\ \partial_{{\bf x}_2} f_{\bf a}({\bf x}) \\
           \vdots \\ \partial_{{\bf x}_d} f_{\bf a}({\bf x})
           \end{bmatrix} = \begin{bmatrix} 0 \\ 0 \\ \vdots \\ a2 \end{bmatrix}

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
            :math:`\nabla_{\bf x}f_{\bf a}({\bf x};{\bf a})` at points `x`
        """
        out = np.zeros((x.shape[0],self.dim))
        out[:,-1] = self.a2
        return out

    def partial_xd(self, x, *args, **kwargs):
        r""" Evaluate :math:`\partial_{{\bf x}_d} f_{\bf a}({\bf x}) = b`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
            :math:`\partial_{{\bf x}_d}f_{\bf a}({\bf x})` at points `x`
        """
        return self.a2 * np.ones(x.shape[0])

    def grad_x_partial_xd(self, x, *args, **kwargs):
        r""" Evaluate :math:`\nabla_{\bf x}\partial_{{\bf x}_d} f_{\bf a}({\bf x}) = 0`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
            :math:`\nabla_{\bf x}\partial_{{\bf x}_d}f_{\bf a}({\bf x})` at points `x`
        """
        return np.zeros((x.shape[0],self.dim))

    def partial2_xd(self, x, *args, **kwargs):
        r""" Evaluate :math:`\partial^2_{{\bf x}_d} f_{\bf a}({\bf x}) = 0`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
            :math:`\partial^2_{{\bf x}_d}f_{\bf a}({\bf x};{\bf a})` at points `x`
        """
        return np.zeros(x.shape[0])

    def inverse(self, xkm1, y):
        r""" Compute :math:`f_{\bf a}^{-1}({\bf x}_{1:d-1})(y):={\bf x}_d` s.t. :math:`f_{\bf a}({\bf x}_{1:d-1},{\bf x}_d) - y = 0`.

        Due to the form of the approximation we have:

        .. math::

           f_{\bf a}^{-1}({\bf x}_{1:d-1})(y) = \frac{y-a_1}{a_2}

        Args:
          xkm1 (:class:`ndarray<numpy.ndarray>` [:math:`d-1`]): fixed coordinates
            :math:`{\bf x}_{1:d-1}`
          y (float): value :math:`y`

        Returns:
          (:class:`float<float>`) -- inverse value :math:`x`.
        """
        return (y - self.a1)/self.a2

class FrozenExponential(MonotonicFrozenFunction):
    r""" Frozen Exponential map :math:`f_{\bf a}:{\bf x} \mapsto \exp( {\bf x}_d )`

    Args:
      dim (int): input dimension :math:`d`
    """

    def __init__(self, dim):
        self.dim = dim
        self.set_coeffs()

    @property
    def n_coeffs(self):
        r"""
        Returns: 0
        """
        return 0

    def set_coeffs(self):
        r""" No coefficients to be set.
        """
        pass

    def evaluate(self, x, *args, **kwargs):
        r""" Evaluate :math:`f_{\bf a}({\bf x}) = \exp({\bf x}_d)`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- function value at points `x`
        """
        return np.exp(x[:,-1])

    def grad_x(self, x, *args, **kwargs):
        r""" Evaluate :math:`\nabla_{\bf x} f_{\bf a}({\bf x})`

        This is:

        .. math::

           \nabla_{\bf x} f_{\bf a}({\bf x}) = \begin{bmatrix}
           \partial_{{\bf x}_1} f_{\bf a}({\bf x}) \\ \partial_{{\bf x}_2} f_{\bf a}({\bf x}) \\
           \vdots \\ \partial_{{\bf x}_d} f_{\bf a}({\bf x})
           \end{bmatrix} = \begin{bmatrix} 0 \\ 0 \\ \vdots \\ \exp({\bf x}_d) \end{bmatrix}

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
            :math:`\nabla_{\bf x}f_{\bf a}({\bf x};{\bf a})` at points `x`
        """
        out = np.zeros((x.shape[0],self.dim))
        out[:,-1] = np.exp(x[:,-1])
        return out

    def hess_x(self, x, *args, **kwargs):
        r""" Evaluate :math:`\nabla^2_{\bf x} f_{\bf a}({\bf x})`

        This is:

        .. math::

           \nabla^2_{\bf x} f_{\bf a}({\bf x}) = \begin{bmatrix}
           \partial^2_{{\bf x}_1} f_{\bf a}({\bf x}) & \partial_{{\bf x}_1{\bf x}_2} f_{\bf a}({\bf x}) & \cdots & \partial_{{\bf x}_1{\bf x}_d} f_{\bf a}({\bf x}) \\
           \partial_{{\bf x}_2 {\bf x}_1} f_{\bf a}({\bf x}) & \partial^2_{{\bf x}_2} f_{\bf a}({\bf x}) & \cdots & \partial_{{\bf x}_2{\bf x}_d} f_{\bf a}({\bf x}) \\
           \vdots &  & \ddots & \\
           \partial_{{\bf x}_d{\bf x}_1} f_{\bf a}({\bf x}) & \partial_{{\bf x}_d{\bf x}_2} f_{\bf a}({\bf x}) & \cdots & \partial^2_{{\bf x}_d} f_{\bf a}({\bf x})
           \end{bmatrix} = \begin{bmatrix}
           0 & \cdots & 0 & 0 \\
           \vdots & \ddots & 0 & \vdots \\
           0 & \cdots & 0 & 0 \\
           0 & \cdots & 0 &  \exp({\bf x}_d) \end{bmatrix}

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
            :math:`\nabla^2_{\bf x}f_{\bf a}({\bf x})` at points `x`
        """
        out = np.zeros((x.shape[0],self.dim,self.dim))
        out[:,-1,-1] = np.exp(x[:,-1])
        return out

    def partial_xd(self, x, *args, **kwargs):
        r""" Evaluate :math:`\partial_{{\bf x}_d} f_{\bf a}({\bf x}) = \exp({\bf x}_d)`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
            :math:`\partial_{{\bf x}_d}f_{\bf a}({\bf x};{\bf a})` at points `x`
        """
        return self.fapprox(x)

    def grad_x_partial_xd(self, x, *args, **kwargs):
        r""" Evaluate :math:`\nabla_{\bf x}\partial_{{\bf x}_d} f_{\bf a}({\bf x})`

        This is:

        .. math::

           \nabla_{\bf x} \partial_{{\bf x}_d} f_{\bf a}({\bf x}) = \begin{bmatrix}
           \partial_{{\bf x}_1} f_{\bf a}({\bf x}) \\ \partial_{{\bf x}_2} f_{\bf a}({\bf x}) \\
           \vdots \\ \partial_{{\bf x}_d} f_{\bf a}({\bf x})
           \end{bmatrix} = \begin{bmatrix} 0 \\ 0 \\ \vdots \\ \exp({\bf x}_d) \end{bmatrix}


        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
            :math:`\nabla_{\bf x}\partial_{{\bf x}_d}f_{\bf a}({\bf x})` at points `x`
        """
        return self.dx_fapprox(x)

    def partial2_xd(self, x, *args, **kwargs):
        r""" Evaluate :math:`\partial^2_{{\bf x}_d} f_{\bf a}({\bf x}) = \exp({\bf x}_d)`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
            :math:`\partial^2_{{\bf x}_d}f_{\bf a}({\bf x})` at points `x`
        """
        return self.fapprox(x)

    def inverse(self, xkm1, y):
        r""" Compute :math:`f_{\bf a}^{-1}({\bf x}_{1:d-1})(y):={\bf x}_d` s.t. :math:`f_{\bf a}({\bf x}_{1:d-1},{\bf x}_d) - y = 0`.

        Due to the form of the approximation we have:

        .. math::

           f_{\bf a}^{-1}({\bf x}_{1:d-1})(y) = \log(y)

        Args:
          xkm1 (:class:`ndarray<numpy.ndarray>` [:math:`d-1`]): fixed coordinates
            :math:`{\bf x}_{1:d-1}`
          y (float): value :math:`y`

        Returns:
          (:class:`float<float>`) -- inverse value :math:`x`.
        """
        return np.log(y)

class FrozenGaussianToUniform(MonotonicFrozenFunction):
    r""" Frozen Gaussian To Uniform map.

    This is given by the Cumulative Distribution Function of a standard
    normal distribution along the last coordinate:

    .. math::

       f_{\bf a}({\bf x}) = \frac{1}{2} \left[ 1 + \text{erf}\left( \frac{x}{\sqrt{2}} \right)\right]

    Args:
      dim (int): input dimension :math:`d`
    """

    def __init__(self, dim):
        self.dim = dim
        self.set_coeffs()
        self.std = stats.norm()

    @property
    def n_coeffs(self):
        r"""
        Returns: 0
        """
        return 0

    def set_coeffs(self):
        r""" No coefficients to be set.
        """
        pass

    def evaluate(self, x, *args, **kwargs):
        r""" Evaluate :math:`f_{\bf a}({\bf x})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) -- function value at points `x`
        """
        return self.std.cdf(x[:,-1])

    def grad_x(self, x, *args, **kwargs):
        r""" Evaluate :math:`\nabla_{\bf x} f_{\bf a}({\bf x})`

        This is:

        .. math::

           \nabla_{\bf x} f_{\bf a}({\bf x}) = \begin{bmatrix}
           \partial_{{\bf x}_1} f_{\bf a}({\bf x}) \\ \partial_{{\bf x}_2} f_{\bf a}({\bf x}) \\
           \vdots \\ \partial_{{\bf x}_d} f_{\bf a}({\bf x})
           \end{bmatrix} = \begin{bmatrix} 0 \\ 0 \\ \vdots \\
           (2\pi)^{-1}\exp(-\frac{{\bf x}^2_d}{2})
           \end{bmatrix}

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
            :math:`\nabla_{\bf x}f_{\bf a}({\bf x})` at points `x`
        """
        out = np.zeros((x.shape[0],self.dim))
        out[:,-1] = np.exp(-x[:,-1]**2./2.) / np.sqrt(2.*np.pi)
        return out

    def partial_xd(self, x, *args, **kwargs):
        r""" Evaluate :math:`\partial_{{\bf x}_d} f_{\bf a}({\bf x}) = (2\pi)^{-1}\exp(-\frac{{\bf x}^2_d}{2})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
            :math:`\partial_{{\bf x}_d}f_{\bf a}({\bf x})` at points `x`
        """
        return np.exp(-x[:,-1]**2./2.) / np.sqrt(2.*np.pi)

    def hess_x(self, x, *args, **kwargs):
        r""" Evaluate :math:`\nabla^2_{\bf x} f_{\bf a}({\bf x})`

        This is:

        .. math::

           \nabla^2_{\bf x} f_{\bf a}({\bf x}) = \begin{bmatrix}
           \partial^2_{{\bf x}_1} f_{\bf a}({\bf x}) & \partial_{{\bf x}_1{\bf x}_2} f_{\bf a}({\bf x}) & \cdots & \partial_{{\bf x}_1{\bf x}_d} f_{\bf a}({\bf x}) \\
           \partial_{{\bf x}_2 {\bf x}_1} f_{\bf a}({\bf x}) & \partial^2_{{\bf x}_2} f_{\bf a}({\bf x}) & \cdots & \partial_{{\bf x}_2{\bf x}_d} f_{\bf a}({\bf x}) \\
           \vdots &  & \ddots & \\
           \partial_{{\bf x}_d{\bf x}_1} f_{\bf a}({\bf x}) & \partial_{{\bf x}_d{\bf x}_2} f_{\bf a}({\bf x}) & \cdots & \partial^2_{{\bf x}_d} f_{\bf a}({\bf x})
           \end{bmatrix} = \begin{bmatrix}
           0 & \cdots & 0 & 0 \\
           \vdots & \ddots & 0 & \vdots \\
           0 & \cdots & 0 & 0 \\
           0 & \cdots & 0 &  -{\bf x}_d (2\pi)^{-1} \exp(-\frac{{\bf x}^2_d}{2})
           \end{bmatrix}

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
            :math:`\nabla^2_{\bf x}f_{\bf a}({\bf x})` at points `x`
        """
        out = np.zeros((x.shape[0],self.dim,self.dim))
        out[:,-1,-1] = -x[:,-1] * np.exp(-x[:,-1]**2./2.) / np.sqrt(2.*np.pi)
        return out

    def grad_x_partial_xd(self, x, *args, **kwargs):
        r""" Evaluate :math:`\nabla_{\bf x}\partial_{{\bf x}_d} f_{\bf a}({\bf x})`

        This is:

        .. math::

           \nabla_{\bf x} \partial_{{\bf x}_d} f_{\bf a}({\bf x}) = \begin{bmatrix}
           \partial_{{\bf x}_1} f_{\bf a}({\bf x}) \\ \partial_{{\bf x}_2} f_{\bf a}({\bf x}) \\
           \vdots \\ \partial_{{\bf x}_d} f_{\bf a}({\bf x})
           \end{bmatrix} = \begin{bmatrix} 0 \\ 0 \\ \vdots \\
           -{\bf x}_d (2\pi)^{-1} \exp(-\frac{{\bf x}^2_d}{2})
           \end{bmatrix}


        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]) --
            :math:`\nabla_{\bf x}\partial_{{\bf x}_d}f_{\bf a}({\bf x})` at points `x`
        """
        out = np.zeros((x.shape[0],self.dim))
        out[:,-1] = - x[:,-1] * np.exp(-x[:,-1]**2./2.) / np.sqrt(2.*np.pi)
        return out

    def partial2_xd(self, x, *args, **kwargs):
        r""" Evaluate :math:`\partial^2_{{\bf x}_d} f_{\bf a}({\bf x}) = -{\bf x}_d (2\pi)^{-1} \exp(-\frac{{\bf x}^2_d}{2})`

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m`]) --
            :math:`\partial^2_{{\bf x}_d}f_{\bf a}({\bf x})` at points `x`
        """
        return - x[:,-1] * np.exp(-x[:,-1]**2./2.) / np.sqrt(2.*np.pi)

    def hess_x_partial_xd(self, x, *args, **kwargs):
        r""" Evaluate :math:`\nabla^2_{\bf x} \partial_{{\bf x}_d} f_{\bf a}({\bf x})`

        This is:

        .. math::

           \nabla^2_{\bf x} \partial_{{\bf x}_d} f_{\bf a}({\bf x}) = \begin{bmatrix}
           \partial^2_{{\bf x}_1} f_{\bf a}({\bf x}) & \partial_{{\bf x}_1{\bf x}_2} f_{\bf a}({\bf x}) & \cdots & \partial_{{\bf x}_1{\bf x}_d} f_{\bf a}({\bf x}) \\
           \partial_{{\bf x}_2 {\bf x}_1} f_{\bf a}({\bf x}) & \partial^2_{{\bf x}_2} f_{\bf a}({\bf x}) & \cdots & \partial_{{\bf x}_2{\bf x}_d} f_{\bf a}({\bf x}) \\
           \vdots &  & \ddots & \\
           \partial_{{\bf x}_d{\bf x}_1} f_{\bf a}({\bf x}) & \partial_{{\bf x}_d{\bf x}_2} f_{\bf a}({\bf x}) & \cdots & \partial^2_{{\bf x}_d} f_{\bf a}({\bf x})
           \end{bmatrix} = \begin{bmatrix}
           0 & \cdots & 0 & 0 \\
           \vdots & \ddots & 0 & \vdots \\
           0 & \cdots & 0 & 0 \\
           0 & \cdots & 0 & ({\bf x}_d - 1) (2\pi)^{-1} \exp(-\frac{{\bf x}^2_d}{2})
           \end{bmatrix}

        Args:
          x (:class:`ndarray<numpy.ndarray>` [:math:`m,d`]): evaluation points.

        Returns:
          (:class:`ndarray<numpy.ndarray>` [:math:`m,d,d`]) --
            :math:`\nabla^2_{\bf x}\partial_{{\bf x}_d}f_{\bf a}({\bf x})` at points `x`
        """
        out = np.zeros((x.shape[0],self.dim,self.dim))
        out[:,-1,-1] = (x[:,-1]**2. - 1.) * np.exp(-x[:,-1]**2./2.) / np.sqrt(2.*np.pi)
        return out

    def invserse(self, xkm1, y):
        r""" Compute :math:`f_{\bf a}^{-1}({\bf x}_{1:d-1})(y):={\bf x}_d` s.t. :math:`f_{\bf a}({\bf x}_{1:d-1},{\bf x}_d) - y = 0`.

        Due to the form of the approximation we have:

        .. math::

           f_{\bf a}^{-1}({\bf x}_{1:d-1})(y) = \sqrt{2} \text{erf}^{-1}(2y-1)

        Args:
          xkm1 (:class:`ndarray<numpy.ndarray>` [:math:`d-1`]): fixed coordinates
            :math:`{\bf x}_{1:d-1}`
          y (float): value :math:`y`

        Returns:
          (:class:`float<float>`) -- inverse value :math:`x`.
        """
        return self.std.ppf( y )
