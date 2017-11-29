import numpy as np
import sympy
import combinatorics
from multiindex import multiindex
import bases


class jet(object):
    """Truncated Taylor's series.

    The jet is represented in both a closed and expanded form. The closed form is ``fun``:math:`=\\sum_{0\\leq deg \\leq k}` ``fun_deg[deg]`` where ``fun_deg[deg]=coeff[deg]*pb[deg]`` is a symbolic representation of the degree ``deg`` term. The expanded form is the list ``fun_deg`` of ``sympy.Matrix(m,1)`` objects where ``coeff`` is a list of ``k+1 numpy.array`` objects with shapes :math:`(m,{n+j-1 \\choose j})` for :math:`0\leq j\leq k`. ``pb`` is a dictionary indexed by degree of ``sympy.Matrix`` objects with ``pb[j]`` representing a basis for homogenous :math:`j^{th}` degree polynomials in the variables :math:`x_0,\ldots,x_{n-1}` of the form :math:`\\begin{pmatrix}x_0^j & x_0^{j-1}x_1 & \\cdots & x_{n-1}^j \\end{pmatrix}^T`. ``coeff[deg][coord,term]`` is the coefficient of the monomial ``pb[deg][term]`` in coordinate ``coord`` of the partial derivative of :math:`f` indexed by the ``term`` th ``normal_forms.multiindex.multiindex(deg,n)``.

    Parameters
    ----------
    f : callable
        function that accepts ``n`` arguments and returns tuple of length ``m``, corresponding to mathematical function :math:`f:\\mathbb{R}^n\\rightarrow\\mathbb{R}^m`
    x : number if ``n==1`` or tuple of length ``n`` if ``n>=1``
        center about which jet is expanded
    k : int
        maximum degree of jet

    Attributes
    ----------
    n : int
        dimension of domain of :math:`f`
    m : int
        dimension of codomain of :math:`f`
    var : list of ``n sympy.symbol`` objects
        ``x_0``, ``x_1``, ..., ``x_{n-1}`` representing arguments of :math:`f`
    pb : ``normal_forms.bases.poly_basis``
        a basis for polynomials in the variables ``var``
    coeff : list of ``k+1 numpy.array`` objects of shape :math:`(m,{n+j-1\\choose j})` for :math:`0\leq j\leq k`
        jet coefficients indexed as ``coeff[deg][coord,term]`` where :math:`0\leq` ``deg`` :math:`\leq k`, :math:`0\leq` ``coord`` :math:`\leq m`, and :math:`0\leq` ``term`` :math:`<{m-1+deg \\choose deg}`.
    fun_deg : list of ``k+1 sympy.Matrix(m,1)`` objects
        symbolic representation of each term in the jet indexed as ``fun_deg[deg]`` for ``deg=0,...,k``
    fun : ``sympy.Matrix(m,1)``
        symbolic representation of jet
    fun_lambdified : callable
        lambdified version of fun
    """

    def __init__(self, f, x, k, f_args=None, var=None, pb=None):
        """initialize the jet"""

        self.f = f
        self.x = x
        self.k = k
        if np.array(x).shape == ():
            n, x = 1, [x]
        else:
            n = len(x)
        # call to f
        if f_args is None:
            f_eval = f(*x)
        else:
            f_eval = f(*(list(x) + list(f_args)))
        if np.array(f_eval).shape == ():
            m = 1
        else:
            # call to f
            m = len(f_eval)
        self.m = m
        self.n = n

        if var is None:
            var = sympy.symarray('x', (n, ))
        if pb is None:
            pb = bases.poly_basis(var)

        self.var = var
        self.pb = pb

        # number of terms per degree of expanded form
        n_terms = combinatorics.simplicial_list(n, k)

        coeff = [np.empty([m, n_terms[deg]]) for deg in range(k + 1)]
        basis = [sympy.ones(n_terms[deg], 1) for deg in range(k + 1)]
        # call to f
        if f_args is None:
            f_eval = f(*var)
        else:
            f_eval = f(*(list(var) + list(f_args)))
        coeff[0][:, 0] = list(sympy.Matrix([f_eval]).subs(zip(var, x)))
        for deg in range(1, k + 1):
            m_idx = multiindex(deg, n)
            for term in range(n_terms[deg]):
                # call to f
                if f_args is None:
                    f_eval = f(*var)
                else:
                    f_eval = f(*(list(var) + list(f_args)))
                coeff[deg][:, term] = list(
                    sympy.diff(sympy.Matrix([f_eval]), *m_idx.to_var(var))
                    .subs(zip(var, x)) / m_idx.factorial())
                basis[deg][term] = m_idx.to_polynomial(var, x)
                m_idx.increment()

        for deg in range(k + 1):
            poly = list(sympy.Matrix(coeff[deg]) * basis[deg])
            m_idx = multiindex(deg, n)
            for term in range(n_terms[deg]):
                for coord in range(m):
                    coeff[deg][coord, term] = poly[coord].coeff(pb[deg][term])
                m_idx.increment()

        self.coeff = coeff

        self.update_fun()

    def update_fun(self):
        """Compute symbolic and lambdified versions of the jet from the coefficients."""

        # symbolic representation by degree
        fun_deg = [
            sympy.Matrix(self.coeff[deg]) * self.pb[deg]
            for deg in range(self.k + 1)
        ]
        self.fun_deg = fun_deg
        for deg in range(self.k + 1):
            self.fun_deg[deg] = sympy.Matrix(self.coeff[deg]) * self.pb[deg]

        # symbolic representation, sum of elements in fun_deg
        self.fun = sympy.zeros(self.m, 1)
        for deg in range(self.k + 1):
            self.fun += self.fun_deg[deg]
        self.fun = list(self.fun)
        if len(self.fun) == 1:
            self.fun = self.fun[0]

        # lambdified fun
        self.fun_lambdified = sympy.lambdify(self.var, self.fun)

    def __call__(self, *args):
        """Evaluate the jet."""
        return self.fun_lambdified(*args)

    def __getitem__(self, deg):
        """Return symbolic representation of ``deg``th degree jet term."""
        res = list(self.fun_deg[deg])
        if len(res) == 1:
            return res[0]
        else:
            return res
