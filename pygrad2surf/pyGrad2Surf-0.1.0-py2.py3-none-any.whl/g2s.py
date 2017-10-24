import numpy as np
import scipy.sparse as sp
import scipy.linalg as la
from scipy.linalg import solve_sylvester

from pyGrad2Surf.difflocal import dop, diff_local, norm


# https://docs.scipy.org/doc/numpy-dev/user/numpy-for-matlab-users.html
# http://stackoverflow.com/a/1001716
def mrdivide(a, b):
    # Problem: C = A/B
    #       -> CB = A
    # If B is square:
    #       -> C = A*inv(B)
    # Otherwise:
    #       -> C*(B*B') = A*B'
    #       -> C = A*B'*inv(B*B')
    A = np.asmatrix(a)
    B = np.asmatrix(b)
    dims = B.shape
    if dims[0] == dims[1]:
        return A * B.I
    else:
        return (A * B.T) * (B * B.T).I


def mldivide(a, b):
    dimensions = a.shape
    if dimensions[0] == dimensions[1]:
        return la.solve(a, b)
    else:
        return la.lstsq(a, b)[0]


def _g2sSylvester(A, B, F, G, u, v):
    """
    % Purpose : Solves the semi-definite Sylvester Equation of the form
    %   A'*A * Phi + Phi * B'*B - A'*F - G*B = 0,
    %   Where the null vectors of A and B are known to be
    %   A * u = 0
    %   B * v = 0
    %
    % Use (syntax):
    %   Phi = g2sSylvester( A, B, F, G, u, v )
    %
    % Input Parameters :
    %   A, B, F, G := Coefficient matrices of the Sylvester Equation
    %   u, v := Respective null vectors of A and B
    %
    % Return Parameters :
    %   Phi := The minimal norm solution to the Sylvester Equation
    %
    % Description and algorithms:
    %   The rank deficient Sylvester equation is solved by means of Householder
    %   reflections and the Bartels-Stewart algorithm.  It uses the MATLAB
    %   function "lyap", in reference to Lyapunov Equations, a special case of
    %   the Sylvester Equation.
    """

    # Household vectors (???)
    m, n = len(u), len(v)

    u[0] += norm(u)
    u *= np.sqrt(2) / norm(u)

    v[0] += norm(v)
    v *= np.sqrt(2) / norm(v)

    # Apply householder updates
    A -= np.dot(np.dot(A, u), u.T)
    B -= np.dot(np.dot(B, v), v.T)
    F -= np.dot(np.dot(F, v), v.T)
    G -= np.dot(u, (np.dot(u.T, G)))

    # Solve the system of equations
    phi = np.zeros((m, n))
    phi[0, 1:] = mrdivide(G[0, :], B[:, 1:].T)
    phi[1:, 0] = mldivide(A[:, 1:], F[:, 0].T)
    phi[1:, 1:] = solve_sylvester(np.dot(A[:, 1:].T, A[:, 1:]),
                                  np.dot(B[:, 1:].T, B[:, 1:]),
                                  -np.dot(-A[:, 1:].T, F[:, 1:]) + np.dot(G[1:, :], B[:, 1:]))

    # Invert the householder updates
    if u.dtype == "complex128":
        u = np.sqrt(np.real(u)**2 + np.imag(u)**2)
    if v.dtype == "complex128":
        v = np.sqrt(np.real(v)**2 + np.imag(v)**2)
    phi -= np.dot(u, (np.dot(u.T, phi)))
    phi -= np.dot(np.dot(phi, v), v.T)
    # phi += np.dot(u, np.dot(np.dot(u.T, (np.dot(phi, v))), v.T))
    return phi


def g2s(x, y, Zx, Zy, N=3):
    """
    % Purpose : Computes the Global Least Squares reconstruction of a surface
    %   from its gradient field.
    %
    % Use (syntax):
    %   Z = g2s( Zx, Zy, x, y )
    %   Z = g2s( Zx, Zy, x, y, N )
    %
    % Input Parameters :
    %   Zx, Zy := Components of the discrete gradient field
    %   x, y := support vectors of nodes of the domain of the gradient
    %   N := number of points for derivative formulas (default=3)
    %
    % Return Parameters :
    %   Z := The reconstructed surface
    %
    % Description and algorithms:
    %   The algorithm solves the normal equations of the Least Squares cost
    %   function, formulated by matrix algebra:
    %   e(Z) = || D_y * Z - Zy ||_F^2 + || Z * Dx' - Zx ||_F^2
    %   The normal equations are a rank deficient Sylvester equation which is
    %   solved by means of Householder reflections and the Bartels-Stewart
    %   algorithm.
    """

    if Zx.shape != Zy.shape:
        raise ValueError("Gradient components must be the same size")

    if np.asmatrix(Zx).shape[1] != len(x) or np.asmatrix(Zx).shape[0] != len(y):
        raise ValueError("Support vectors must have the same size as the gradient")

    m, n = Zx.shape

    Dx = diff_local(x, N, N)
    Dy = diff_local(y, N, N)

    Z = _g2sSylvester(Dy, Dx, Zy, Zx, np.ones((m, 1)), np.ones((n, 1)))
    return Z


def g2s_weighted(x, y, Zx, Zy, Lxx, Lxy, Lyx, Lyy, N=3):
    """
    % Purpose : Computes the Global Weighted Least Squares reconstruction of a
    %   surface from its gradient field, whereby the weighting is defined by a
    %   weighted Frobenius norm
    %
    % Use (syntax):
    %   Z = g2sWeighted( Zx, Zy, x, y, N, Lxx, Lxy, Lyx, Lyy )
    %
    % Input Parameters :
    %   Zx, Zy := Components of the discrete gradient field
    %   x, y := support vectors of nodes of the domain of the gradient
    %   N := number of points for derivative formulas (default=3)
    %   Lxx, Lxy, Lyx, Lyy := Each matrix Lij is the covariance matrix of the
    %       gradient's i-component the in j-direction.
    %
    % Return Parameters :
    %   Z := The reconstructed surface
    %
    % Description and algorithms:
    %   The algorithm solves the normal equations of the Weighted Least Squares
    %   cost function, formulated by matrix algebra:
    %   e(Z) = || Lyy^(-1/2) * (D_y * Z - Zy) * Lyx^(-1/2) ||_F^2 +
    %               || Lxy^(-1/2) * ( Z * Dx' - Zx ) * Lxx^(-1/2) ||_F^2
    %   The normal equations are a rank deficient Sylvester equation which is
    %   solved by means of Householder reflections and the Bartels-Stewart
    %   algorithm.
    """

    if Zx.shape != Zy.shape:
        raise ValueError("Gradient components must be the same size")

    if np.asmatrix(Zx).shape[1] != len(x) or np.asmatrix(Zx).shape[0] != len(y):
        raise ValueError("Support vectors must have the same size as the gradient")

    m, n = Zx.shape

    Dx = diff_local(x, N, N)
    Dy = diff_local(y, N, N)

    Wxx = la.sqrtm(Lxx)
    Wxy = la.sqrtm(Lxy)
    Wyx = la.sqrtm(Lyx)
    Wyy = la.sqrtm(Lyy)

    # Solution for Zw (written here Z)
    u = mldivide(Wxy, np.ones((m, 1)))
    v = mldivide(Wyx, np.ones((n, 1)))

    A = mldivide(Wyy, np.dot(Dy, Wxy))
    B = mldivide(Wxx, np.dot(Dx, Wyx))
    F = mldivide(Wyy, mrdivide(Zy, Wyx))
    G = mldivide(Wxy, mrdivide(Zx, Wxx))

    Z = _g2sSylvester(A, B, F, G, u, v)

    # "Unweight" the solution
    Z = Wxy * Z * Wyx
    return Z


def g2s_spectral(x, y, Zx, Zy, mask, N=3, basisFns="poly"):
    """
    % Purpose : Computes the Global Least Squares reconstruction of a surface
    %   from its gradient field with Spectral filtering, using either
    %   polynomial, cosine, or Fourier bases.
    %
    % Use (syntax):
    %   Z = g2sSpectral( Zx, Zy, x, y, N, Mask, basisFns )
    %   Z = g2sSpectral( Zx, Zy, x, y, N, Mask )
    %
    % Input Parameters :
    %   Zx, Zy := Components of the discrete gradient field
    %   x, y := support vectors of nodes of the domain of the gradient
    %   N := number of points for derivative formulas (default=3)
    %   Mask := either a 1x2 matrix, [p,q], specifying the size of a low pass
    %      filter, or a general mxn spectral mask.
    %   basisFns := 'poly', 'cosine', 'fourier', specifying the type of basis
    %      functions used for regularization.  Defaults is polynomial.  For
    %      arbitrary node spacing, only polnomial filtering is implemented.
    %
    % Return Parameters :
    %   Z := The reconstructed surface
    %
    % Description and algorithms:
    %   The algorithm solves the normal equations of the Least Squares cost
    %   function, formulated by matrix algebra:
    %   e(C) = || D_y * By * C * Bx' - Zy ||_F^2 + || By * C * Bx' * Dx' - Zx ||_F^2
    %   The surface is parameterized by its spectrum, C, w.r.t. sets of orthogonal
    %   basis functions, as,
    %   Z = By * C * Bx'
    %   The normal equations are a rank deficient Sylvester equation which is
    %   solved by means of Householder reflections and the Bartels-Stewart
    %   algorithm.
    """

    # For now, use only the polynomial basis function.

    if Zx.shape != Zy.shape:
        raise ValueError("Gradient components must be the same size")

    if np.asmatrix(Zx).shape[1] != len(x) or np.asmatrix(Zx).shape[0] != len(y):
        raise ValueError("Support vectors must have the same size as the gradient")

    mask = np.array(mask)
    # Low Pass Filter
    if mask.shape == (2,):
        p, q = mask
    # Arbitrary Mask
    elif mask.shape == Zx.shape:
        p, q = Zx.shape
    else:
        raise ValueError("Mask must be the same size as the gradient, or define the size of the low-pass filter")

    if basisFns == "poly":
        Dx = diff_local(x, N, N)
        Dy = diff_local(y, N, N)
    else:
        raise ValueError("Not a valid choice of Basis Functions (currently only 'poly' is supported)")

    # Generate the Basis Functions
    Bx = np.array(dop(x)[0])[:, 0:q]
    By = np.array(dop(y)[0])[:, 0:p]

    # Solve the Sylvester Equation
    A = np.dot(Dy, By)
    B = np.dot(Dx, Bx)
    F = np.dot(Zy, Bx)
    G = np.dot(By.T, Zx)

    C = np.zeros((p, q))
    if q != 1:
        C[0, 1:] = mrdivide(G[0, :], B[:, 1:].T)
    if p != 1:
        C[1:, 0] = mldivide(A[:, 1:], F[:, 0])
    if p != 1 and q != 1:
        C[1:, 1:] = solve_sylvester(np.dot(A[:, 1:].T, A[:, 1:]),
                                    np.dot(B[:, 1:].T, B[:, 1:]),
                                    np.dot(-A[:, 1:].T, F[:, 1:]) - np.dot(G[1:, :], B[:, 1:]))

    # Apply the Spectral Filter (if necessary)
    if mask.shape != (2,):
        C *= mask

    Z = np.real(np.dot(By, np.dot(C, Bx.T)))
    return Z


def g2s_dirichlet(x, y, Zx, Zy, ZB=None, N=3):
    """
    % Purpose : Computes the Global Least Squares reconstruction of a surface
    %   from its gradient field with Dirichlet Boundary conditions.  The
    %   solution surface is thereby constrained to have fixed values at the
    %   boundary, specified by ZB.
    %
    % Use (syntax):
    %   Z = g2sDirichlet( Zx, Zy, x, y )
    %   Z = g2sDirichlet( Zx, Zy, x, y, N )
    %   Z = g2sDirichlet( Zx, Zy, x, y, N, ZB )
    %
    % Input Parameters :
    %   Zx, Zy := Components of the discrete gradient field
    %   x, y := support vectors of nodes of the domain of the gradient
    %   N := number of points for derivative formulas (default=3)
    %   ZB := a matrix specifying the value of the solution surface at the
    %      boundary ( omitting this assumes ZB=zeros(m,n) )
    %
    % Return Parameters :
    %   Z := The reconstructed surface
    %
    % Description and algorithms:
    %   The algorithm solves the normal equations of the Least Squares cost
    %   function, formulated by matrix algebra:
    %   e(Z) = || D_y * Z - Zy ||_F^2 + || Z * Dx' - Zx ||_F^2
    %   The normal equations are a rank deficient Sylvester equation which is
    %   solved by means of Householder reflections and the Bartels-Stewart
    %   algorithm.
    """

    if Zx.shape != Zy.shape:
        raise ValueError("Gradient components must be the same size")

    if np.asmatrix(Zx).shape[1] != len(x) or np.asmatrix(Zx).shape[0] != len(y):
        raise ValueError("Support vectors must have the same size as the gradient")

    m, n = Zx.shape

    Dx = diff_local(x, N, N)
    Dy = diff_local(y, N, N)

    # Set Z equal to ZB for memory useage (avoids using ZI)
    if ZB is None:
        Z = np.zeros((m, n))
    else:
        Z = ZB

    # Harker & O'Leary use sparse matrices here, but things are easier without them...
    # P = sp.diags(np.ones(m-2), -1, shape=(m, m-2))
    # Q = sp.diags(np.ones(m-2), -1, shape=(m, m-2))
    P = sp.diags(np.ones(m-2), -1, shape=(m, m-2)).toarray()
    Q = sp.diags(np.ones(m-2), -1, shape=(m, m-2)).toarray()

    A = np.dot(Dy, P)
    B = np.dot(Dx, Q)

    F = np.dot(Zy - np.dot(Dy, Z), Q)  # Note: Z = ZB here
    G = np.dot(P.T, (Zx - np.dot(Z, Dx.T)))  # Note: Z = ZB here

    # Harker & O'Leary use += below, but -= seems to be correct.
    Z[1:m-1, 1:n-1] -= solve_sylvester((np.dot(A.T, A)),
                                       (np.dot(B.T, B)),
                                       -np.dot(A.T, F) - np.dot(G, B))
    return Z
