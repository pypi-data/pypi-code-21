import numpy as np
import sympy
import combinatorics
import bases
import copy


class lie_operator(object):
    """Lie operator of a vector field.

    In this implementation, the Lie bracket of vector fields :math:`f,g:\\mathbb{R}^n\\rightarrow\\mathbb{R}^n` is defined as :math:`[f,g]=f'(x)g(x)-g'(x)f(x)`. An object of this class represents the Lie bracket with a particular vector field :math:`g`, denoted :math:`L_g(\\cdot)=[g,\\cdot]`.

    Parameters
    ----------
    g : ``sympy.Matrix(m,1)``
        symbolic representation of degree ``deg`` homogenous polynomial vector field in variables ``var``
    var : list of ``n sympy.symbol`` objects
        arguments ``x_0``, ``x_``, ..., ``x_{n-1}`` of polynomial components of ``g``
    deg : int, optional
        degree of ``g``. If not supplied, it is guessed from the terms in ``g``.
    pb : ``normal_forms.bases.poly_basis``, optional
        polynomial basis, see ``normal_forms.bases``
    vb : ``normal_forms.bases.vf_basis``, opetional
        polynomial vector field basis, see ``normal_forms.bases``

    Attributes
    ----------
    dg : ``sympy.Matrix(m,n)``
        coefficients of derivative of ``g`` with respect to basis ``pb``
    matrix : dict of ``numpy.array`` objects
        matrix representations of Lie operator acting on homogenous polynomial vector fields
    """

    def __init__(self, g, var, deg=None, pb=None, vb=None):

        m = len(g)
        n = len(var)

        self.g = g

        # try to guess degree of g if not supplied
        if deg is None and g.norm() != 0:
            idx = 0
            while g[idx] == 0:
                idx += 1
            deg = sympy.poly(g[idx]).total_degree()
        self.deg = deg

        self.var = var
        self.m = m
        self.n = n

        # construct bases if not supplied
        if pb is None:
            pb = bases.poly_basis(var)
        if vb is None:
            vb = bases.vf_basis(pb, m)
        self.pb = pb
        self.vb = vb

        # derivative of g with respect to basis pb
        dg = sympy.zeros(m, n)
        for i in range(n):
            dg[:, i] = sympy.diff(g, var[i])
        self.dg = dg

        # dict of matrix representations of Lie operator
        self.matrix = {}

    def add_matrix(self, deg):
        """Add to dict ``matrix`` the matrix representation of Lie operator acting on homogenous degree ``deg`` :math:`m`-dimensional polynomial vector field.

        Parameters
        ----------
        deg : int
            degree of vector field argument to Lie operator :math:`L_g`
        """
        m = self.m
        n = self.n
        pb = self.pb
        vb = self.vb
        var = self.var
        g = self.g
        dg = self.dg

        # number of vf basis elements of degree deg
        n_vf = len(vb[deg])

        # derivatives of vb with respect to pb
        dvb = [sympy.zeros(m, n) for _ in range(n_vf)]
        for i in range(n_vf):
            for j in range(n):
                dvb[i][:, j] = sympy.diff(vb[deg][i], var[j])

        # symbolic Lie operator action on vb
        bracket = [
            sympy.expand(dvb[i] * g - dg * vb[deg][i]) for i in range(n_vf)
        ]

        # number of coefficients to specify a vector field in Lie operator codomain
        n_terms = len(pb[self.deg + deg - 1])

        # store matrix representation from coefficients of bracket
        mat = np.empty([m * n_terms, n_vf])
        for j in range(n_vf):
            for coord in range(m):
                for i in range(n_terms):
                    mat[coord * n_terms + i, j] = bracket[j][coord].coeff(
                        pb[self.deg + deg - 1][i])
        self.matrix[deg] = mat

    def __call__(self, f):
        """Apply Lie operator to a vector field.

        Parameters
        ----------
        f : ``sympy.Matrix(m,1)``
            symbolic representation of homogenous polynomial vector field

        Returns
        -------
        ``sympy.Matrix(m,1)``
            symbolic representation of Lie operator of vector field
        """

        m = self.m
        pb = self.pb

        # Return zero if argument is zero, otherwise guess degree of argument
        if f.norm() == 0:
            return sympy.zeros(m, 1)
        else:
            idx = 0
            while f[idx] == 0:
                idx += 1
            deg = sympy.poly(f[idx]).total_degree()

        # if necessary matrix representation does not exist, construct it
        if deg not in self.matrix.keys():
            self.add_matrix(deg)
        mat = self.matrix[deg]

        # compute action of Lie operator as matrix-vector product
        n_terms = mat.shape[1] / m
        coeff = np.empty(m * n_terms)
        for term in range(n_terms):
            for coord in range(m):
                coeff[coord * n_terms + term] = f[coord].coeff(pb[deg][term])
        coeff = mat.dot(coeff)

        # symbolic representation of result from coefficients
        n_terms = mat.shape[0] / m
        h = sympy.zeros(m, 1)
        for coord in range(m):
            h[coord] = pb[self.deg + deg - 1].dot(
                coeff[coord * n_terms:(coord + 1) * n_terms]).expand()

        return h

    def __getitem__(self, deg):
        """Return matrix representation of operator acting on degree ``deg`` polynomial vector fields.

        Parameters
        ----------
        deg : int
            degree of argument to Lie operator

        Returns
        -------
        ``numpy.array``
        """

        # if necessary matrix representation does not exist, construct it
        if deg not in self.matrix.keys():
            self.add_matrix(deg)
        return self.matrix[deg]
