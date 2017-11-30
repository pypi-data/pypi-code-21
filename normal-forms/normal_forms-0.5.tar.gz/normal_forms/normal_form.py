import sympy
import numpy as np
import lie_operator
import jet
import bases
import combinatorics


class normal_form(object):
    """A normal form of an autonomous vector field :math:`f:\\mathbb{R}^n\\rightarrow\\mathbb{R}^m`.

    Arguments
    ---------
    f : callable
        function that accepts ``n`` arguments and returns tuple of length ``m`` numbers, corresponding to mathematical function :math:`f:\\mathbb{R}^n\\rightarrow\\mathbb{R}^m`
    x : number if ``n==1`` or tuple of length ``n`` if ``n>=1``
        center about which normal form is computed
    k : int
        maximum degree of normal form

    Attributes
    ----------
    n : int
        dimension of domain of :math:`f`
    m : int
        dimension of codomain of :math:`f`
    jet : ``normal_forms.jet.jet``
        series representation of normal form
    L1 : ``normal_forms.lie_operator.lie_operator``
        fundamental operator of the normal form, Lie bracket with the linear term :math:`f_1(x)=f'(x)x`, that is :math:`L_{f_1}(\cdot) = [f_1,\cdot]`, see ``normal_forms.lie_operator.lie_operator``
    g : list of ``k-1`` ``sympy.Matrix(m,1)`` objects
        generators, i.e. homogenous :math:`j^{th}` degree :math:`m`-dimensional polynomial vector fields :math:`g_j` for :math:`j\geq2` used to carry out sequence of near-identity transformations :math:`e^{L_{g_j}}` of :math:`f`
    L : ``normal_forms.lie_operator.lie_operator``
        Lie operators :math:`L_{g_j}` of the generators in ``g``, see ``normal_forms.lie_operator.lie_operator``
    eqv : list of shape ``(k-1,2,.,.)``
        coefficients and ``sympy.Matrix(m,1)`` object representation of normal form equivariant vector fields
    fun : sympy.Matrix(m,1) object
        symbolic representation of normal form
    """

    def __init__(self, f, x, k, f_args=None):

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

        # list of symbolic variables
        var = sympy.symarray('x', (n, ))
        # polynomial basis
        pb = bases.poly_basis(var)
        # vector basis
        vb = bases.vf_basis(pb, m)

        # k-jet of f centered at x
        # call to f
        self.jet = jet.jet(f, x, k, f_args, var, pb)

        # fundamental operator of normal form theory, Lie bracket with f'
        self.L1 = lie_operator.lie_operator(self.jet.fun_deg[1], var, 1, pb, vb)

        # work space of coefficients
        n_terms = combinatorics.simplicial_list(n, k)
        wrk = [[np.zeros(m * n_terms[i + j + 1]) for j in range(k - i)]
               for i in range(k)]
        # initialize first row of workspace as k-jet
        for j in range(k):
            wrk[0][j] = np.concatenate(self.jet.coeff[j + 1])

        # generators
        g = []
        # Lie brackets with generators
        L = []
        # equivariant vector fields
        eqv = []

        # list of factorials
        fac = combinatorics.factorial_list(k)
        # algorithm based on Murdock
        for deg in range(2, k + 1):

            # update workspace and solve for generator
            for j, l in enumerate(L):
                wrk[1][deg - 2] += l[deg - 1 - j].dot(wrk[0][deg - 2 - j])
            f_coeff = np.zeros(m * n_terms[deg])
            for i in range(deg):
                f_coeff += wrk[i][deg - 1 - i] / fac[i]
            g_coeff = np.linalg.lstsq(self.L1[deg], f_coeff)[0]

            # normal form coefficients
            h_coeff = f_coeff - self.L1[deg].dot(g_coeff)

            # represent normal form term in L1.T nullspace basis
            u, s, v = np.linalg.svd(self.L1[deg])
            rank = min(self.L1[deg].shape) - np.isclose(s, 0).sum()
            perp_basis = u[:, rank:]
            e_coeff = perp_basis.T.conj().dot(h_coeff)
            e = [
                sympy.Matrix(perp_basis[:, i].reshape(
                    m, perp_basis[:, i].shape[0] / m)) * pb[deg]
                for i in range(perp_basis.shape[1])
            ]

            # truncate roundoff error
            for coeff in [e_coeff, f_coeff, g_coeff, h_coeff]:
                coeff[np.isclose(coeff, 0)] = 0

            # store generator
            g.append(
                sympy.Matrix(np.reshape(g_coeff, (m, len(g_coeff) / m))) *
                pb[deg])

            # update series coeff
            self.jet.coeff[deg] = np.reshape(h_coeff, (m, len(h_coeff) / m))

            # store equivariant vector fields
            eqv.append((e_coeff, e))

            # store Lie operator
            L.append(lie_operator.lie_operator(g[-1], var, deg, pb, vb))

            # update workspace
            wrk[1][deg - 2] += L[-1][1].dot(wrk[0][0])
            for i in range(2, k - deg + 2):
                for j, l in enumerate(L):
                    wrk[i][deg -
                           2] += l[deg -
                                   2 + i - j].dot(wrk[i - 1][deg - 2 - j])

        self.L = L
        self.g = g
        self.eqv = eqv

        # update series symbolic and lambdified representation
        self.jet.update_fun()

        # make jet.fun accessible from this class
        self.fun = self.jet.fun

    def __call__(self, *args):
        """Evaluate the normal form."""
        return self.jet.fun_lambdified(*args)

    def __getitem__(self, deg):
        """Return symbolic representation of ``deg``th degree normal form term."""
        return self.jet[deg]
