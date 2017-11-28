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
import SpectralToolbox.Spectral1D as S1D
import TransportMaps as TM
import TransportMaps.Functionals as FUNC
import TransportMaps.Maps as MAPS

__all__ = ['Default_IsotropicIntegratedExponentialTriangularTransportMap',
           'Default_IsotropicIntegratedExponentialDiagonalTransportMap',
           'Default_IsotropicIntegratedSquaredTriangularTransportMap',
           'Default_IsotropicIntegratedSquaredDiagonalTransportMap',
           'Default_IsotropicMonotonicLinearSpanTriangularTransportMap',
           'Default_IsotropicLinearSpanTriangularTransportMap',
           'Default_LinearSpanTriangularTransportMap']

def Default_IsotropicIntegratedExponentialTriangularTransportMap(
        dim, order, span='total', active_vars=None, btype='poly',
        common_basis_flag=True):
    r""" Generate a triangular transport map with default settings.

    Args:
      dim (int): dimension :math:`d` of the map
      order (int): isotropic order of the map
      span (str): 'full' for full order approximations, 'total' for total order
        approximations. If a :class:`list<list>` of ``dim`` strings is provided,
        these will define the approximation type fore each component
        :math:`T^{(k)}`.
      active_vars (list): list of :math:`d` lists containing the row sparsity
        pattern of the transport, i.e. the active variables for each component.
        Default ``None`` will generate a full triangular map.
      btype (string): ``poly`` uses Hermite functions,
        ``rbf`` uses radial basis functions.
        If a :class:`list<list>` of ``dim`` strings is provided,
        these will define the basis type fore each component
        :math:`T^{(k)}`.
      common_basis_flag (bool): use acceleration provided by common basis among the
        components (``span`` and ``btype`` must be a string or a list with all equal
        elements).

    Returns:
      (:class:`IntegratedExponentialTriangularTransportMap<IntegratedExponentialTriangularTransportMap>`)
      -- the constructed transport map
    """
    # Initialize the list of components
    approx_list = []
    # Initialize the list of active variables
    if active_vars is None:
        active_vars = [ list(range(i+1)) for i in range(dim) ]
    else:
        if len(active_vars) != dim:
            raise ValueError("List of active variables must be dim long.")
        for d, avars in enumerate(active_vars):
            if sorted(avars) != avars:
                raise ValueError("List of active components must be provided in " + \
                                 "sorted order.")
            if avars[-1] != d:
                raise ValueError("List of active components must include at least" + \
                                 "the diagonal term.")
    # Initialize the span type
    if isinstance(span,str):
        span_list = [span] * dim
    else:
        if len(span) != dim:
            raise ValueError("List of span types must be dim long.")
        else:
            span_list = span
    # Initialize the basis type
    if isinstance(btype, str):
        btype_list = [btype] * dim
    else:
        if len(btype) != dim:
            raise AttributeError("List of basis types must be dim long.")
        else:
            btype_list = btype
    # Check whether it is possible to use common basis
    common_basis_flag = common_basis_flag and all(x==span_list[0] for x in span_list) and \
                        all(x==btype_list[0] for x in btype_list)

    # Prepare basis in case common_basis
    if common_basis_flag:
        if btype_list[0] == 'poly':
            c_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(dim)]
            e_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(dim-1)] + \
                           [S1D.ConstantExtendedHermiteProbabilistsFunction()]
            # e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction()
            #                 for i in range(dim)]
        elif btype_list[0] == 'rbf':
            if span_list[0] != 'full':
                raise ValueError("The basis span must be 'full' for basis type 'rbf'")
            c_basis_list = [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(
                order, 0.9) for i in range(dim)]
            c_basis_list = [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(
                order, 0.9) for i in range(dim-1)] + \
                [S1D.ConstantExtendedHermiteProbabilistsRadialBasisFunction(
                    order, 0.9)]
            # e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsRadialBasisFunction(
            #     order, 0.9) for i in range(dim)]
        else:
            raise ValueError("Input btype is invalid.")

    # Instantiate the components
    for d, (avars, span, btype) in enumerate(zip(active_vars, span_list, btype_list)):
        c_orders_list = [order]*(len(avars)-1)+[0]
        if common_basis_flag:
            c_basis_comp = [c_basis_list[a] for a in avars]
            e_basis_comp = [e_basis_list[a] for a in avars]
        else:
            if btype == 'poly':
                c_basis_comp = [S1D.HermiteProbabilistsPolynomial()] * len(avars)
                c_basis_comp = [S1D.HermiteProbabilistsPolynomial()] * (len(avars)-1) + \
                               [S1D.ConstantExtendedHermiteProbabilistsFunction()]
                # e_basis_comp = [S1D.ConstantExtendedHermiteProbabilistsFunction()] * \
                #                len(avars)
            elif btype == 'rbf':
                if span != 'full':
                    raise ValueError("The basis span must be 'full' for basis type 'rbf'")
                c_basis_comp = [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(
                    order, 0.9)] * len(avars)
                e_basis_comp = [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(
                    order, 0.9)] * (len(avars)-1) + \
                    [S1D.ConstantExtendedHermiteProbabilistsRadialBasisFunction(
                        order, 0.9)]
                # e_basis_comp = [S1D.ConstantExtendedHermiteProbabilistsRadialBasisFunction(
                #     order, 0.9)] * len(avars)
                
        c_approx = FUNC.LinearSpanApproximation(
            c_basis_comp, spantype=span, order_list=c_orders_list)
        e_orders_list = [order-1]*len(avars)
        e_approx = FUNC.LinearSpanApproximation(
            e_basis_comp, spantype=span, order_list=e_orders_list)
        approx = FUNC.MonotonicIntegratedExponentialApproximation(c_approx, e_approx)
        approx_list.append( approx )

    # Instantiate the map
    if common_basis_flag:    
        tm_approx = MAPS.CommonBasisIntegratedExponentialTriangularTransportMap(
            active_vars, approx_list)
    else:
        tm_approx = MAPS.IntegratedExponentialTriangularTransportMap(
            active_vars, approx_list)
    return tm_approx

def Default_IsotropicIntegratedExponentialDiagonalTransportMap(
        dim, order, btype='poly'):
    r""" Generate a diagonal transport map with default settings.

    Args:
      dim (int): dimension :math:`d` of the map
      order (int): isotropic order of the map
      btype (string): ``poly`` uses Hermite functions,
        ``rbf`` uses radial basis functions.
        If a :class:`list<list>` of ``dim`` strings is provided,
        these will define the basis type fore each component
        :math:`T^{(k)}`.

    Returns:
      (:class:`IntegratedExponentialTriangularTransportMap<IntegratedExponentialTriangularTransportMap>`)
      -- the constructed transport map
    """
    active_vars = [[d] for d in range(dim)]
    return Default_IsotropicIntegratedExponentialTriangularTransportMap(
        dim, order, span='total', active_vars=active_vars, btype=btype,
        common_basis_flag=False)

def Default_IsotropicIntegratedSquaredTriangularTransportMap(
        dim, order, span='total', active_vars=None, btype='poly',
        common_basis_flag=False):
    r""" Generate a triangular transport map with default settings.

    Args:
      dim (int): dimension :math:`d` of the map
      order (int): isotropic order of the map
      span (str): 'full' for full order approximations, 'total' for total order
        approximations. If a :class:`list<list>` of ``dim`` strings is provided,
        these will define the approximation type fore each component
        :math:`T^{(k)}`.
      active_vars (list): list of :math:`d` lists containing the row sparsity
        pattern of the transport, i.e. the active variables for each component.
        Default ``None`` will generate a full triangular map.
      btype (string): ``poly`` uses Hermite functions,
        ``rbf`` uses radial basis functions.
        If a :class:`list<list>` of ``dim`` strings is provided,
        these will define the basis type fore each component
        :math:`T^{(k)}`.
      common_basis_flag (bool): use acceleration provided by common basis among the
        components (``span`` and ``btype`` must be a string or a list with all equal
        elements).

    Returns:
      (:class:`IntegratedSquaredTriangularTransportMap<IntegratedSquaredTriangularTransportMap>`)
      -- the constructed transport map
    """
    # Initialize the list of components
    approx_list = []
    # Initialize the list of active variables
    if active_vars is None:
        active_vars = [ list(range(i+1)) for i in range(dim) ]
    else:
        if len(active_vars) != dim:
            raise ValueError("List of active variables must be dim long.")
        for d, avars in enumerate(active_vars):
            if sorted(avars) != avars:
                raise ValueError("List of active components must be provided in " + \
                                 "sorted order.")
            if avars[-1] != d:
                raise ValueError("List of active components must include at least" + \
                                 "the diagonal term.")
    # Initialize the span type
    if isinstance(span,str):
        span_list = [span] * dim
    else:
        if len(span) != dim:
            raise ValueError("List of span types must be dim long.")
        else:
            span_list = span
    # Initialize the basis type
    if isinstance(btype, str):
        btype_list = [btype] * dim
    else:
        if len(btype) != dim:
            raise AttributeError("List of basis types must be dim long.")
        else:
            btype_list = btype
    # Check whether it is possible to use common basis
    common_basis_flag = common_basis_flag and all(x==span_list[0] for x in span_list) and \
                        all(x==btype_list[0] for x in btype_list)

    # Prepare basis in case common_basis
    if common_basis_flag:
        if btype_list[0] == 'poly':
            c_basis_list = [S1D.LinearExtendedHermiteProbabilistsFunction() for i in range(dim)]
            # c_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(dim)]
            # c_basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction() for i in range(dim)]
            e_basis_list = [S1D.LinearExtendedHermiteProbabilistsFunction()
                            for i in range(dim-1)] + \
                           [S1D.ConstantExtendedHermiteProbabilistsFunction()]
            # e_basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(dim-1)] + \
            #                [S1D.ConstantExtendedHermiteProbabilistsFunction()]
            # e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsFunction() for i in range(dim)]
        elif btype_list[0] == 'rbf':
            if span[0] != 'full':
                raise ValueError("The basis span must be 'full' for basis type 'rbf'")
            c_basis_list = [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(
                order, 0.9) for i in range(dim)]
            e_basis_list = [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(
                order, 0.9) for i in range(dim-1)] + \
                [ S1D.ConstantExtendedHermiteProbabilistsRadialBasisFunction(
                    order, 0.9) ]
            # e_basis_list = [S1D.ConstantExtendedHermiteProbabilistsRadialBasisFunction(
            #     order, 0.9) for i in range(dim)]
        else:
            raise ValueError("Input btype is invalid.")

    # Instantiate the components
    for d, (avars, span, btype) in enumerate(zip(active_vars, span_list, btype_list)):
        c_orders_list = [order]*(len(avars)-1)+[0]
        if common_basis_flag:
            c_basis_comp = [c_basis_list[a] for a in avars]
            e_basis_comp = [e_basis_list[a] for a in avars]
        else:
            if btype == 'poly':
                c_basis_comp = [S1D.LinearExtendedHermiteProbabilistsFunction()] * len(avars)
                # c_basis_comp = [S1D.HermiteProbabilistsPolynomial()] * len(avars)
                # c_basis_comp = [S1D.ConstantExtendedHermiteProbabilistsFunction()] * len(avars)
                e_basis_comp = [S1D.LinearExtendedHermiteProbabilistsFunction()] * \
                               (len(avars)-1) + \
                               [S1D.ConstantExtendedHermiteProbabilistsFunction()]
                # e_basis_comp = [S1D.HermiteProbabilistsPolynomial()] * (len(avars)-1) + \
                #                [S1D.ConstantExtendedHermiteProbabilistsFunction()]
                # e_basis_comp = [S1D.ConstantExtendedHermiteProbabilistsFunction()] * \
                #                len(avars)
            elif btype == 'rbf':
                if span != 'full':
                    raise ValueError("The basis span must be 'full' for basis type 'rbf'")
                c_basis_comp = [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(
                    order, 0.9)] * len(avars)
                e_basis_comp = [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(
                    order, 0.9)] * (len(avars)-1) + \
                    [S1D.ConstantExtendedHermiteProbabilistsRadialBasisFunction(
                        order, 0.9)]
                # e_basis_comp = [S1D.ConstantExtendedHermiteProbabilistsRadialBasisFunction(
                #     order, 0.9)] * len(avars)
                
        c_approx = FUNC.LinearSpanApproximation(
                c_basis_comp, spantype=span, order_list=c_orders_list)
        e_orders_list = [order-1]*len(avars)
        e_approx = FUNC.LinearSpanApproximation(
                e_basis_comp, spantype=span, order_list=e_orders_list)
        approx = FUNC.MonotonicIntegratedSquaredApproximation(c_approx, e_approx)
        approx_list.append( approx )

    # Instantiate the map
    if common_basis_flag:    
        tm_approx = MAPS.CommonBasisIntegratedSquaredTriangularTransportMap(
            active_vars, approx_list)
    else:
        tm_approx = MAPS.IntegratedSquaredTriangularTransportMap(
            active_vars, approx_list)
    return tm_approx

def Default_IsotropicIntegratedSquaredDiagonalTransportMap(
        dim, order, btype='poly'):
    r""" Generate a diagonal transport map with default settings.

    Args:
      dim (int): dimension :math:`d` of the map
      order (int): isotropic order of the map
      btype (string): ``poly`` uses Hermite functions,
        ``rbf`` uses radial basis functions.
        If a :class:`list<list>` of ``dim`` strings is provided,
        these will define the basis type fore each component
        :math:`T^{(k)}`.

    Returns:
      (:class:`IntegratedSquaredTriangularTransportMap<IntegratedSquaredTriangularTransportMap>`)
      -- the constructed transport map
    """
    active_vars = [[d] for d in range(dim)]
    return Default_IsotropicIntegratedSquaredTriangularTransportMap(
        dim, order, span='total', active_vars=active_vars, btype=btype,
        common_basis_flag=False)

    
def Default_IsotropicMonotonicLinearSpanTriangularTransportMap(
        dim, order, span='total', active_vars=None, btype='poly',
        common_basis_flag=True):
    r""" Generate a triangular transport map with default settings.

    Args:
      dim (int): dimension of the map
      order (int): isotropic order of the map
      span (str): 'full' for full order approximations, 'total' for total order
        approximations. If a :class:`list<list>` of ``dim`` strings is provided,
        these will define the approximation type fore each component
        :math:`T^{(k)}`.
      active_vars (list): list of :math:`d` lists containing the row sparsity
        pattern of the transport, i.e. the active variables for each component.
        Default ``None`` will generate a full triangular map.
      btype (string): ``poly`` uses Hermite functions,
        ``rbf`` uses radial basis functions.
        If a :class:`list<list>` of ``dim`` strings is provided,
        these will define the basis type fore each component
        :math:`T^{(k)}`.
      common_basis_flag (bool): use acceleration provided by common basis among the
        components (``span`` and ``btype`` must be a string or a list with all equal
        elements).

    Returns:
      (:class:`LinearSpanTriangularTransportMap<LinearSpanTriangularTransportMap>`) -- the constructed transport map
    """
    # Initialize the list of components
    approx_list = []
    # Initialize the list of active variables
    if active_vars is None:
        active_vars = [ list(range(i+1)) for i in range(dim) ]
    else:
        if len(active_vars) != dim:
            raise ValueError("List of active variables must be dim long.")
        for d, avars in enumerate(active_vars):
            if sorted(avars) != avars:
                raise ValueError("List of active components must be provided in " + \
                                 "sorted order.")
            if avars[-1] != d:
                raise ValueError("List of active components must include at least" + \
                                 "the diagonal term.")
    # Initialize the span type
    if isinstance(span,str):
        span_list = [span] * dim
    else:
        if len(span) != dim:
            raise ValueError("List of span types must be dim long.")
        else:
            span_list = span
    # Initialize the basis type
    if isinstance(btype, str):
        btype_list = [btype] * dim
    else:
        if len(btype) != dim:
            raise AttributeError("List of basis types must be dim long.")
        else:
            btype_list = btype
    # Check whether it is possible to use common basis
    common_basis_flag = common_basis_flag and all(x==span_list[0] for x in span_list) and \
                        all(x==btype_list[0] for x in btype_list)

    # Prepare basis in case common_basis
    if common_basis_flag:
        if btype_list[0] == 'poly':
            basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(dim)]
        elif btype_list[0] == 'rbf':
            if span_list[0] != 'full':
                raise ValueError("The basis span must be 'full' for basis type 'rbf'")
            basis_list = [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(
                order, 0.9) for i in range(dim)]
        else:
            raise ValueError("Input btype is invalid.")

    # Instantiate the components
    for d, (avars, span, btype) in enumerate(zip(active_vars, span_list, btype_list)):
        orders_list = [order]*len(avars)
        if common_basis_flag:
            basis_comp = [basis_list[a] for a in avars]
        else:
            if btype == 'poly':
                basis_comp = [S1D.HermiteProbabilistsPolynomial()] * len(avars)
            elif btype == 'rbf':
                if span != 'full':
                    raise ValueError("The basis span must be 'full' for basis type 'rbf'")
                basis_comp = [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(
                    order, 0.9)] * len(avars)
            else:
                raise ValueError("Input btype is invalid.")
                
        approx = FUNC.MonotonicLinearSpanApproximation(
            basis_comp, spantype=span, order_list=orders_list)
        approx_list.append( approx )

    # Instantiate the map
    if common_basis_flag:    
        tm_approx = MAPS.MonotonicCommonBasisLinearSpanTriangularTransportMap(
            active_vars, approx_list)
    else:
        tm_approx = MAPS.MonotonicLinearSpanTriangularTransportMap(
            active_vars, approx_list)
    return tm_approx

def Default_IsotropicLinearSpanTriangularTransportMap(
        dim, order, span='total', active_vars=None, btype='poly',
        common_basis_flag=True):
    r""" Generate a triangular transport map with default settings.

    Args:
      dim (int): dimension of the map
      order (int): isotropic order of the map
      span (str): 'full' for full order approximations, 'total' for total order
        approximations. If a :class:`list<list>` of ``dim`` strings is provided,
        these will define the approximation type fore each component
        :math:`T^{(k)}`.
      active_vars (list): list of :math:`d` lists containing the row sparsity
        pattern of the transport, i.e. the active variables for each component.
        Default ``None`` will generate a full triangular map.
      btype (string): ``poly`` uses Hermite functions,
        ``rbf`` uses radial basis functions.
        If a :class:`list<list>` of ``dim`` strings is provided,
        these will define the basis type fore each component
        :math:`T^{(k)}`.
      common_basis_flag (bool): use acceleration provided by common basis among the
        components (``span`` and ``btype`` must be a string or a list with all equal
        elements).

    Returns:
      (:class:`LinearSpanTriangularTransportMap<LinearSpanTriangularTransportMap>`) -- the constructed transport map
    """
    # Initialize the list of components
    approx_list = []
    # Initialize the list of active variables
    if active_vars is None:
        active_vars = [ list(range(i+1)) for i in range(dim) ]
    else:
        if len(active_vars) != dim:
            raise ValueError("List of active variables must be dim long.")
        for d, avars in enumerate(active_vars):
            if sorted(avars) != avars:
                raise ValueError("List of active components must be provided in " + \
                                 "sorted order.")
            if avars[-1] != d:
                raise ValueError("List of active components must include at least" + \
                                 "the diagonal term.")
    # Initialize the span type
    if isinstance(span,str):
        span_list = [span] * dim
    else:
        if len(span) != dim:
            raise ValueError("List of span types must be dim long.")
        else:
            span_list = span
    # Initialize the basis type
    if isinstance(btype, str):
        btype_list = [btype] * dim
    else:
        if len(btype) != dim:
            raise AttributeError("List of basis types must be dim long.")
        else:
            btype_list = btype
    # Check whether it is possible to use common basis
    common_basis_flag = common_basis_flag and all(x==span_list[0] for x in span_list) and \
                        all(x==btype_list[0] for x in btype_list)

    # Prepare basis in case common_basis
    if common_basis_flag:
        if btype_list[0] == 'poly':
            basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(dim)]
        elif btype_list[0] == 'rbf':
            if span_list[0] != 'full':
                raise ValueError("The basis span must be 'full' for basis type 'rbf'")
            basis_list = [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(
                order, 0.9) for i in range(dim)]
        else:
            raise ValueError("Input btype is invalid.")

    # Instantiate the components
    for d, (avars, span, btype) in enumerate(zip(active_vars, span_list, btype_list)):
        orders_list = [order]*len(avars)
        if common_basis_flag:
            basis_comp = [basis_list[a] for a in avars]
        else:
            if btype == 'poly':
                basis_comp = [S1D.HermiteProbabilistsPolynomial()] * len(avars)
            elif btype == 'rbf':
                if span != 'full':
                    raise ValueError("The basis span must be 'full' for basis type 'rbf'")
                basis_comp = [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(
                    order, 0.9)] * len(avars)
            else:
                raise ValueError("Input btype is invalid.")
                
        approx = FUNC.LinearSpanApproximation(
            basis_comp, spantype=span, order_list=orders_list)
        approx_list.append( approx )

    # Instantiate the map
    if common_basis_flag:    
        tm_approx = MAPS.CommonBasisLinearSpanTriangularTransportMap(
            active_vars, approx_list)
    else:
        tm_approx = MAPS.LinearSpanTriangularTransportMap(
            active_vars, approx_list)
    return tm_approx

    
def Default_LinearSpanTriangularTransportMap(dim, midxs_list, active_vars,
                                             btype='poly', common_basis_flag=True):
    r""" Generate a linear span triangular transport map with default settings and user defined sparsity and orders.

    Args:
      dim (int): dimension of the map
      midxs_list (list): list of :math:`d` lists of multi-indices for each component
      active_vars (list): list of :math:`d` lists containing the row sparsity
        pattern of the transport, i.e. the active variables for each component.
      btype (string): ``poly`` uses Hermite functions,
        ``rbf`` uses radial basis functions.
        If a :class:`list<list>` of ``dim`` strings is provided,
        these will define the basis type fore each component
        :math:`T^{(k)}`.
      common_basis_flag (bool): use acceleration provided by common basis among the
        components (``btype`` must be a string or a list with all equal
        elements).

    Returns:
      (:class:`LinearSpanTriangularTransportMap<LinearSpanTriangularTransportMap>`) -- the constructed transport map
    """
    # Initialize the list of components
    approx_list = []
    # Initialize the list of active variables
    if len(active_vars) != dim:
        raise ValueError("List of active variables must be dim long.")
    for d, avars in enumerate(active_vars):
        if sorted(avars) != avars:
            raise ValueError("List of active components must be provided in " + \
                             "sorted order.")
        if avars[-1] != d:
            raise ValueError("List of active components must include at least" + \
                             "the diagonal term.")
    # Initialize the basis type
    if isinstance(btype, str):
        btype_list = [btype] * dim
    else:
        if len(btype) != dim:
            raise AttributeError("List of basis types must be dim long.")
        else:
            btype_list = btype
    # Check whether it is possible to use common basis
    common_basis_flag = common_basis_flag and all(x==btype_list[0] for x in btype_list)

    # Prepare basis in case common_basis
    if common_basis_flag:
        if btype_list[0] == 'poly':
            basis_list = [S1D.HermiteProbabilistsPolynomial() for i in range(dim)]
        elif btype_list[0] == 'rbf':
            basis_list = [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(
                order, 0.9) for i in range(dim)]
        else:
            raise ValueError("Input btype is invalid.")

    # Instantiate the components
    for d, (avars, midxs, btype) in enumerate(zip(active_vars, midxs_list, btype_list)):
        if common_basis_flag:
            basis_comp = [basis_list[a] for a in avars]
        else:
            if btype == 'poly':
                basis_comp = [S1D.HermiteProbabilistsPolynomial()] * len(avars)
            elif btype == 'rbf':
                basis_comp = [S1D.LinearExtendedHermiteProbabilistsRadialBasisFunction(
                    order, 0.9)] * len(avars)
            else:
                raise ValueError("Input btype is invalid.")
        approx = FUNC.LinearSpanApproximation(basis_comp, midxs)
        approx_list.append( approx )

    # Instantiate the map
    if common_basis_flag:    
        tm_approx = MAPS.CommonBasisLinearSpanTriangularTransportMap(
            active_vars, approx_list)
    else:
        tm_approx = MAPS.LinearSpanTriangularTransportMap(
            active_vars, approx_list)
    return tm_approx