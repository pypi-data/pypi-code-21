#import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from math import factorial


#sns.set(font_scale=1.5)
def cubic_elastic_mat(C11, C12, C44):
    elas_mat = np.zeros([6, 6])
    elas_mat[0, 0] = C11
    elas_mat[1, 1] = C11
    elas_mat[2, 2] = C11
    elas_mat[3, 3] = C44
    elas_mat[4, 4] = C44
    elas_mat[5, 5] = C44
    elas_mat[0, 1] = C12
    elas_mat[0, 2] = C12
    elas_mat[1, 2] = C12
    elas_mat[1, 0] = C12
    elas_mat[2, 0] = C12
    elas_mat[2, 1] = C12
    return elas_mat


def FluoriteElasticMat(C11, C12, C22, C23, C44, C55, **kwargs):
    elas_mat = np.zeros([6, 6])
    elas_mat[0, 0] = C11
    elas_mat[1, 1] = C22
    elas_mat[2, 2] = C22
    elas_mat[3, 3] = C44
    elas_mat[4, 4] = C55
    elas_mat[5, 5] = C55
    elas_mat[0, 1] = C12
    elas_mat[0, 2] = C12
    elas_mat[1, 2] = C23
    elas_mat[1, 0] = C12
    elas_mat[2, 0] = C12
    elas_mat[2, 1] = C23
    if 'C13' in kwargs:
        elas_mat[0, 2] = kwargs['C13']
        elas_mat[2, 0] = kwargs['C13']
    if 'C33' in kwargs:
        elas_mat[2, 2] = kwargs['C33']
    if 'C66' in kwargs:
        elas_mat[5, 5] = kwargs['C66']
    return elas_mat


def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """

    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order + 1)
    half_window = (window_size - 1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range]
                for k in range(-half_window, half_window + 1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs(y[1:half_window + 1][::-1] - y[0])
    lastvals = y[-1] + np.abs(y[-half_window - 1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve(m[::-1], y, mode='valid')


def reduce_stf(S, direction):
    S11 = S[0, 0]
    S12 = S[0, 1]
    S44 = S[3, 3]
    I, J, K = direction
    angle1 = I / np.sqrt(I**2 + J**2 + K**2)
    angle2 = J / np.sqrt(I**2 + J**2 + K**2)
    angle3 = K / np.sqrt(I**2 + J**2 + K**2)
    reduce_S = S11 - 2 * (S11 - S12 - S44 / 2) * ((angle1 * angle2)**2 +
                                                  (angle2 * angle3)**2 +
                                                  (angle1 * angle3)**2)
    return reduce_S


def reduce_possion(S, direction_load, direction_strain):
    S11 = S[0, 0]
    S12 = S[0, 1]
    S44 = S[3, 3]
    I, J, K = direction_load
    X, Y, Z = direction_strain
    angle_load_1 = I / np.sqrt(I**2 + J**2 + K**2)
    angle_load_2 = J / np.sqrt(I**2 + J**2 + K**2)
    angle_load_3 = K / np.sqrt(I**2 + J**2 + K**2)
    angle_strain_1 = X / np.sqrt(X**2 + Y**2 + Z**2)
    angle_strain_2 = Y / np.sqrt(X**2 + Y**2 + Z**2)
    angle_strain_3 = Z / np.sqrt(X**2 + Y**2 + Z**2)
    D = (angle_load_1 * angle_strain_1)**2 + (
        angle_load_2 * angle_strain_2)**2 + (angle_load_3 * angle_strain_3)**2
    P = (angle_load_1 * angle_load_2)**2 + (angle_load_2 * angle_load_3)**2 + (
        angle_load_3 * angle_load_1)**2
    s = S11 - S12 - S44 / 2  # Attention, s is Different from compliance matrix S !!!
    v = -(S12 + s * D) / (S11 - 2 * s * P
                          )  # possion ration at specific direction
    return v


# compute E*
def reduce_young_modulus(young_moudulus, possion_ratio):
    E = young_moudulus
    v = possion_ratio
    reduce_E = ((1 - v**2) / E)**-1
    return reduce_E


# compute hardness
def theoratical_hardness(reduce_E, indenter_r, indent_depth):
    P = (4 / 3) * reduce_E * (indenter_r**0.5) * (indent_depth**1.5)  # load
    A = np.pi * indent_depth * (2 * indenter_r - indent_depth
                                )  # indentation area
    H = P / A  # hardness
    return H


def get_Estar(C11, C12, C44, direction_load, direction_strain):
    stiff_mat = cubic_elastic_mat(C11, C12, C44)
    compli_mat = np.linalg.inv(stiff_mat)
    reduce_compli = reduce_stf(compli_mat, direction_load)
    reduce_E = 1 / reduce_compli
    possion = reduce_possion(compli_mat, direction_load, direction_strain)
    Estar = reduce_young_modulus(reduce_E, possion)
    return Estar


class Indentation:
    def __init__(self, FileName, scale=1.6, radius=45):
        self.data = np.loadtxt(FileName, comments='#')
        self.force = self.data[:, 2] * scale
        self.depth = self.data[:, 3]
        self.radius = radius
        self.area = np.pi * self.depth * (2 * self.radius - self.depth)

    def PlotHardness(self, legend, start=10, depth=np.inf):
        N = len(self.depth < depth)
        depth = self.depth[start:N]
        force = self.force[start:N]
        area = self.area[start:N]
        hardness = force / area * 100
        plt.plot(depth, hardness, label=legend)

    def PlotForceVsDepth(self, legend, depth=np.inf):
        N = len(self.depth < depth)
        depth = self.depth[:N]
        force = self.force[:N]
        plt.plot(depth, force, label=legend)
