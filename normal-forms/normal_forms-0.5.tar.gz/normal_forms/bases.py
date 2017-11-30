import multiindex
import combinatorics
import sympy


class poly_basis(object):
    """Basis for polynomials of :math:`n` variables.

    Parameters
    ----------
    var : tuple of ``n sympy.symbol`` objects
        arguments ``x_0``, ..., ``x_{n-1}`` of polynomial

    Attributes
    ----------
    n : int
        number of polynomial arguments
    basis : dict of ``sympy.Matrix`` objects
        ``basis[j]`` is a ``sympy.Matrix`` object of shape :math:`({n-j+1\\choose j},1)` representing a basis for homogenous :math:`j^{th}` degree polynomials in the variables :math:`x_0,\ldots,x_{n-1}` of the form :math:`\\begin{pmatrix}x_0^j & x_0^{j-1}x_1 & \\cdots & x_{n-1}^j \\end{pmatrix}^T`.
    """

    def __init__(self, var):

        self.var = var
        self.n = len(var)
        self.basis = {}

    def add_basis(self, deg):
        """Add representation of degree ``deg`` basis to dictionary ``basis``."""

        n = self.n
        var = self.var

        # number of basis elements by degree
        n_terms = combinatorics.simplicial_list(n, deg)[-1]

        # create basis elements from multiindices
        poly = sympy.ones(n_terms, 1)
        m_idx = multiindex.multiindex(deg, n)
        for term in range(n_terms):
            poly[term] = m_idx.to_polynomial(var)
            m_idx.increment()
        self.basis[deg] = poly

    def __getitem__(self, deg):
        """Return the degree ``deg`` basis."""
        if deg not in self.basis.keys():
            self.add_basis(deg)
        return self.basis[deg]


class vf_basis(object):
    """Basis for :math:`m`-dimensional polynomial vector fields of :math:`n` variables.

    Parameters
    ----------
    pb : ``normal_forms.bases.poly_basis`` object
        basis for polynomials of :math:`n` variables
    m : int
        dimension of vector fields

    Attributes
    ----------
    n : int
       number of polynomial arguments
    basis : dict of lists of ``sympy.Matrix(m,1)`` objects
        ``basis[j]`` is a list of length :math:`m{d-j+1\\choose j}` ``sympy.Matrix(m,1)`` objects representing a basis for :math:`m`-dimensional homogenous :math:`j^{th}` degree polynomial vector fields in the variables :math:`x_0,\ldots,x_{n-1}` of the form :math:`\\begin{pmatrix} x_0^j, & \ldots, & 0\\end{pmatrix}^T`, :math:`\\begin{pmatrix} x_0^{j-1}x_1, & \ldots, & 0\\end{pmatrix}^T`, ..., :math:`\\begin{pmatrix} x_{n-1}^{j}, & \ldots, & 0\\end{pmatrix}^T`, ..., :math:`\\begin{pmatrix} 0, & \ldots, & x_0^j \\end{pmatrix}^T`, :math:`\\begin{pmatrix} 0, & \ldots, &  x_0^{j-1}x_1 \\end{pmatrix}^T`, ..., :math:`\\begin{pmatrix} 0, \ldots, & x_{n-1}^{j} \\end{pmatrix}^T`.
    """

    def __init__(self, pb, m):

        self.pb = pb
        self.var = pb.var
        self.n = pb.n
        self.m = m
        self.basis = {}

    def add_basis(self, deg):
        """Add representation of degree ``deg`` basis to dictionary ``basis``."""

        n = self.n
        m = self.m
        pb = self.pb

        n_terms = len(pb[deg])
        n_vf_basis = m * n_terms

        vf = [sympy.zeros(m, 1) for _ in range(n_vf_basis)]
        for coord in range(m):
            for term in range(n_terms):
                vf[coord * n_terms + term][coord] = pb[deg][term]

        self.basis[deg] = vf

    def __getitem__(self, deg):
        """Return the degree ``deg`` basis."""
        if deg not in self.basis.keys():
            self.add_basis(deg)
        return self.basis[deg]
