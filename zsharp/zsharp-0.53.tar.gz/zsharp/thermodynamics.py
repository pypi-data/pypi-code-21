# conduct basic thermodynamics calculation
# EF2n convert fermi energy to density
# n2EF convert density to fermi energy

import numpy as np
from scipy.optimize import curve_fit
from scipy.special import gamma
from scipy.interpolate import interp1d
from . import  constants
import scipy.constants as spconstants
from zsharp import Virial


cst_LiD2=constants.cst(atom='LiD2')

# EF2n convert EF to density n, in unit of hertz and um^-3
def EF2n(EF,m=9.988346e-27):
    hbar = 1.0545718e-34 #SI
    hh = 2*np.pi * hbar #SI
    n = (2 * m * np.abs(EF) * hh / hbar ** 2)** (3 / 2) / (6 * np.pi ** 2) / 1e18 * np.sign(EF)

    return n


def n2EF(n,m=9.988346e-27):
    hbar = 1.0545718e-34  # SI
    hh = 2 * np.pi * hbar  # SI
    EF = (1 / (2 * m)) * (hbar ** 2) * (6 * np.pi ** 2 * np.abs(n) * 1e18)** (2 / 3)*np.sign(n) / hh
    return EF

def z2V(z,f,m=9.988346e-27):
    hbar = 1.0545718e-34 #SI
    hh = 2*np.pi * hbar #SI
    V=0.5* m * (2*np.pi*f)**2 * (z/1e6)**2 /hh
    return V

def V2z(V,f,m=9.988346e-27):
    hbar = 1.0545718e-34  # SI
    hh = 2 * np.pi * hbar  # SI
    z=np.sqrt(2*V*hh/(m*(2*np.pi*f)**2))*1e6
    return z

# Thomas Fermi Profile
def TFfun(z,mu0,z0,rTF):
    return np.real( mu0**(3/2)* ((1-(z-z0)**2/(rTF)**2)* (0.5 * (np.sign(1-(z-z0)**2/(rTF)**2) + 1)))**(3/2))

# Thomas Fermi Fitting
def TFfit(z,n,R0):
    '''Thomas Fermi profile fit, output P: P[0]=amplitude^(2/3), P[1]=center of the trap, P[2]=Thomas Fermi radius'''
    m=np.argmax(n)
    n_max=n[m]
    mu0=n_max**(2/3)
    z0=z[m]
    P=curve_fit(TFfun, z, n,[mu0,z0,R0])
    return P

# Bose-Einstein Function
def BE(nu,zz,j):
    out=zz*0
    for l in np.arange(1,j+1):
        out = out + zz**l/(l**nu)
    return out
def FD(nu,zz,j):
    out = zz * 0
    for l in np.arange(1, j+1):
        out = out + (-1)**(l-1)*zz**l/l**nu
    return out
def zeta(n):
    def eta(nu,j):
        return np.sum(((-1) ** (np.arange(1, j+1)+1)) / (np.arange(1, j+1)**nu) )

    prefactor = 2 ** (n - 1) / (2 ** (n - 1) - 1)
    numerator = 1 + 36 * 2 ** n * eta(n, 2) + 315 * 3 ** n * eta(n, 3) + 1120 * 4 ** n * eta(n, 4) + 1890 * 5 ** n * eta(n, 5) + 1512 * 6 ** n * eta(n, 6) + 462 * 7 ** n * eta(n, 7)
    denominator = 1 + 36 * 2 ** n + 315 * 3 ** n + 1120 * 4 ** n + 1890 * 5 ** n + 1512 * 6 ** n + 462 * 7 ** n
    Z = prefactor * numerator / denominator
    return Z


def PolyLogFrac(n,z):
    if (n % 1) == 0:
        return z*0 # return integet polylog, not implemented yet
    z=np.asanyarray(z,dtype='float64')
    id1 = (z >= 0.55)
    z1 = z[id1]
    id2 = (z > 0) & (z < 0.55)
    z2 = z[id2]
    id3 = (z <= 0) & (z > -50)
    z3 = np.abs(z[id3])
    id4 = (z <= -50)
    z4 = np.abs(z[id4])
    g=np.asanyarray(z*0)

    # Solution Method z-Range 1
    alpha = -np.log(z1)
    def b(i):
        return zeta(n-i)
    preterm = gamma(1 - n)  / (alpha ** (1 - n))

    nominator = b(0)- alpha * (b(1) - 4 * b(0) * b(4) / 7 / b(3)) + \
                alpha**2*(b(2) / 2 + b(0) * b(4) / 7 / b(2) - 4 * b(1) * b(4) / 7 / b(3)) + \
                 - alpha ** 3 * (b(3) / 6 - 2 * b(0) * b(4) / 105 / b(1) + b(1) * b(4) / 7 / b(2) - 2 * b(2) * b(4) / 7 / b(3))

    denominator = 1 + alpha* 4 * b(4) / 7 / b(3) + \
    alpha**2 * b(4) / 7 / b(2) + \
    alpha**3 * 2 * b(4) / 105 / b(1) + \
    alpha**4 * b(4) / 840 / b(0)
    g1 = preterm + nominator/ denominator;
    g[id1] = g1

    #Solution Method z-Range 2
    nominator = 6435 * 9 ** n * BE(n, z2, 8) - 27456 * 8 ** n * z2 * BE(n, z2, 7) + \
    48048 * 7 ** n * z2 ** 2 * BE(n, z2, 6) - 44352 * 6 ** n * z2** 3 * BE(n, z2, 5) + \
    23100 * 5 ** n * z2 ** 4 * BE(n, z2, 4) - 6720 * 4 ** n * z2 ** 5 * BE(n, z2, 3) + \
    1008 * 3 ** n * z2 ** 6 * BE(n, z2, 2) - 64 * 2 ** n * z2 ** 7 * BE(n, z2, 1)
    denominator = 6435 * 9 ** n - 27456 * 8 ** n * z2 + \
    + 48048 * 7 ** n * z2 ** 2 - 44352 * 6 ** n * z2** 3 + \
    + 23100 * 5 ** n * z2 ** 4 - 6720 * 4 ** n * z2 ** 5 + \
    + 1008 * 3 ** n * z2 ** 6 - 64 * 2 ** n * z2 ** 7 + \
    + z2 ** 8;
    g2 = nominator / denominator;
    g[id2] = g2;

    #Solution Method z-Range 3
    nominator = 6435 * 9 ** n * FD(n, z3, 8) + 27456 * 8 ** n * z3 * FD(n, z3, 7) + \
    + 48048 * 7 ** n * z3 ** 2 * FD(n, z3, 6) + 44352 * 6 ** n * z3** 3 * FD(n, z3, 5) + \
    + 23100 * 5 ** n * z3 ** 4 * FD(n, z3, 4) + 6720 * 4 ** n * z3** 5 * FD(n, z3, 3) + \
    + 1008 * 3 ** n * z3 ** 6 * FD(n, z3, 2) + 64 * 2 ** n * z3 ** 7 * FD(n, z3, 1)


    denominator = 6435 * 9 ** n + 27456 * 8 ** n * z3 + \
    + 48048 * 7 ** n * z3 ** 2 + 44352 * 6 ** n * z3 ** 3 + \
    + 23100 * 5 ** n * z3 ** 4 + 6720 * 4 ** n * z3 ** 5 + \
    + 1008 * 3 ** n * z3 ** 6 + 64 * 2 ** n * z3 ** 7 + \
    + z3 ** 8
    g3 = - nominator/ denominator
    g[id3] = g3

    # Solution Method z-Range 4
    xi = np.log(z4)
    preterm = (xi**n)/gamma(n+1);
    series = 1 + n*(n-1)*(np.pi**2/6)*(1/xi**2) + \
             n*(n-1)*(n-2)*(n-3)*(7*np.pi**4/360)*(1/xi**4)
    g4 = - preterm * series
    g[id4]=g4
    return g

# Out put the ideal Fermi gas EoS as a dictionary
def IdealFermiEoS():
    LogPoints = 50000
    beta_mu_start = -30
    # beta_mu_stop = 30
    beta_mu_stop = 100
    beta_mu_vec = np.linspace(beta_mu_start, beta_mu_stop, LogPoints)
    Z_vec = np.exp(beta_mu_vec)

    PTilde = 10 * np.pi / (6 * np.pi ** 2) ** (2 / 3) * (-PolyLogFrac(5 / 2, -Z_vec) / (-PolyLogFrac(3 / 2, -Z_vec)) ** (5 / 3))
    KappaTilde = (6 * np.pi ** 2) ** (2 / 3) / (6 * np.pi) * (-PolyLogFrac(1 / 2, -Z_vec) / (-PolyLogFrac(3 / 2, -Z_vec)) ** (1 / 3))
    TTilde = (4 * np.pi) / (6 * np.pi ** 2 * (-PolyLogFrac(3 / 2, -Z_vec))) ** (2 / 3)
    CV_NkB = 15 / 4 * (-PolyLogFrac(5 / 2, -Z_vec)) / (-PolyLogFrac(3 / 2, -Z_vec)) - 9 / 4 * (-PolyLogFrac(3 / 2, -Z_vec)) / (-PolyLogFrac(1 / 2, -Z_vec))

    return {'TTilde':TTilde, 'KappaTilde':KappaTilde ,'PTilde':PTilde, 'CV_NkB': CV_NkB, 'Beta_mu':beta_mu_vec, 'Z_vec': Z_vec}

IdealEoS_dict=IdealFermiEoS()
PTilde_T_fun=interp1d(IdealEoS_dict['TTilde'],IdealEoS_dict['PTilde'], kind='linear',fill_value = 'extrapolate')
Z_T_fun=interp1d(IdealEoS_dict['TTilde'],IdealEoS_dict['Z_vec'], kind='linear',fill_value = 'extrapolate')
TTilde_P_fun=interp1d(IdealEoS_dict['PTilde'],IdealEoS_dict['TTilde'],fill_value = 'extrapolate')

# Get the profile of ideal fermi gas given the chemical potential and temperature
def IdealGasnV( P,V ):
    #P[0]: chemical potential #P[1]: temperature
    mli = 9.988346e-27
    hbar = 1.0545718e-34
    hh = 2 * np.pi * hbar

    mu_local = P[0] - V
    beta_mu = mu_local / P[1]
    Z_vec = np.exp(beta_mu)

    TTilde = (4 * np.pi)/(6 * np.pi ** 2 * (-PolyLogFrac(3 / 2, -Z_vec))) ** (2 / 3)
    EF = P[1]/ TTilde

    n = (2 * mli * EF * hh / hbar ** 2) ** (3 / 2) / (6 * np.pi ** 2) / 1e18
    return n

# Fit the ideal fermi gas EOS to get mu and T
def IdealGasFitFudge( V,n,P0 ):
    def fitfun(x,mu,T,fudge):
        return fudge * IdealGasnV([mu, T],x)
    P = curve_fit(fitfun, V, n, P0)

    return P

def IdealGasFit( V,n,P0 ):
    def fitfun(x, mu, T):
        return IdealGasnV([mu, T], x)
    P = curve_fit(fitfun, V, n, P0)
    return P

def Gaussian1d(P,x):
    y=P[0]*np.exp(-(x-P[1])**2/(P[2]**2))
    return y

def GaussianFit(x,y,r0):
    P0=np.max(y)
    P1=x[np.argmax(y)]
    P2=r0
    def fitfun(x, P0, P1,P2):
        return Gaussian1d([P0,P1,P2], x)
    P = curve_fit(fitfun, x, y, [P0,P1,P2])
    return P

def ImbalancedVirialnV( P,V ):
    # P[0]: mu_S1, P[1]: mu_S2, P[2]: k_B T
    # V an array of trapping potential
    mli = 9.988346 * 10 ** (-27)
    hbar = 1.0545718 * 10 ** (-34)
    hh = 2 * np.pi * hbar

    Db2 = 1 / np.sqrt(2) #PHYSICAL REVIEW A 82, 023619 (2010)
    Db3 = -0.35501298 #PHYSICAL REVIEW A 82, 043626 (2010)

    mu1_vec = P[0] - V
    mu2_vec = P[1] - V
    BetaMu1_vec = mu1_vec / P[2]
    BetaMu2_vec = mu2_vec / P[2]
    Z1_vec = np.exp(BetaMu1_vec)
    Z2_vec = np.exp(BetaMu2_vec)

    CommonMatrix1 = -PolyLogFrac(3 / 2, -Z1_vec) + 2 * Db2 * Z1_vec * Z2_vec + Db3 * (2 * Z1_vec ** 2 * Z2_vec + Z1_vec * Z2_vec ** 2)
    CommonMatrix2 = -PolyLogFrac(3 / 2, -Z2_vec) + 2 * Db2 * Z2_vec * Z1_vec + Db3 * (2 * Z2_vec ** 2 * Z1_vec + Z2_vec * Z1_vec ** 2)

    TTilde1 = 4 * np.pi / ((6 * (np.pi ** 2) * CommonMatrix1) ** (2 / 3))
    EF1 = P[2] / TTilde1
    n1 = ((2 * mli * EF1 * hh / (hbar ** 2)) ** (3 / 2)) / (6 * np.pi ** 2) / 1e18
    n2 = n1 * (CommonMatrix2 / CommonMatrix1)

    return [n1,n2]

def ImbalancedVirialnV_vec( P,V ):

    mli = 9.988346 * 10 ** (-27)
    hbar = 1.0545718 * 10 ** (-34)
    hh = 2 * np.pi * hbar

    V = V[range(0,np.int_((len(V))/2))]

    Db2 = 1 / np.sqrt(2)  # PHYSICAL REVIEW A 82, 023619 (2010)
    Db3 = -0.35501298  # PHYSICAL REVIEW A 82, 043626 (2010)

    mu1_vec = P[0] - V
    mu2_vec = P[1] - V
    BetaMu1_vec = mu1_vec / P[2]
    BetaMu2_vec = mu2_vec / P[2]
    Z1_vec = np.exp(BetaMu1_vec)
    Z2_vec = np.exp(BetaMu2_vec)

    CommonMatrix1 = -PolyLogFrac(3 / 2, -Z1_vec) + 2 * Db2 * Z1_vec * Z2_vec + Db3 * (
    2 * Z1_vec ** 2 * Z2_vec + Z1_vec * Z2_vec ** 2)
    CommonMatrix2 = -PolyLogFrac(3 / 2, -Z2_vec) + 2 * Db2 * Z2_vec * Z1_vec + Db3 * (
    2 * Z2_vec ** 2 * Z1_vec + Z2_vec * Z1_vec ** 2)

    TTilde1 = 4 * np.pi / ((6 * (np.pi ** 2) * CommonMatrix1) ** (2 / 3))
    EF1 = P[2] / TTilde1
    n1 = ((2 * mli * EF1 * hh / (hbar ** 2)) ** (3 / 2)) / (6 * np.pi ** 2) / 1e18
    n2 = n1 * (CommonMatrix2 / CommonMatrix1)

    n_vec=np.concatenate((n1,n2))

    return n_vec




def ImbalancedVirialFit( V,n1,n2,P0 ):

    V_vec = np.concatenate((V,V))
    n_vec = np.concatenate((n1,n2))

    def fitfun(V, P0, P1,P2):
        return ImbalancedVirialnV_vec( [P0,P1,P2],V )

    P = curve_fit(fitfun, V_vec, n_vec, P0)

    return P



def PolaronGasnV( P, V, meff=1.25, A=-0.615):
    #P[0]: polaron chemical potential:
    #P[1]: temperature
    mli = 9.988346e-27
    mli_eff=mli*meff;

    hbar = 1.0545718e-34
    hh = 2 * np.pi * hbar

    mu_local = P[0] - (1-A)*V
    beta_mu = mu_local / P[1]
    Z_vec = np.exp(beta_mu)

    TTilde = (4 * np.pi)/(6 * np.pi ** 2 * (-PolyLogFrac(3 / 2, -Z_vec))) ** (2 / 3)
    EF = P[1]/ TTilde

    n = (2 * mli_eff * EF * hh / hbar ** 2) ** (3 / 2) / (6 * np.pi ** 2) / 1e18
    return n

def PolaronFitFixT(V,n,T,mu0,meff=1.25,A=-0.615):

    def fitfun(V,P0):
        return PolaronGasnV( [P0,T],V, meff, A )

    P = curve_fit(fitfun, V, n, mu0)

    return P

def PolaronFit(V,n,P0,meff=1.25,A=-0.615):

    def fitfun(V, P0, P1):
        return PolaronGasnV( [P0,P1],V, meff, A )

    P = curve_fit(fitfun, V, n, P0)

    return P

def FD1d_au(P,z):
    # P[0]: overall amplitude P[1]:beta, P[2]:mu P[3]: z0 P[4]: offset
    nz=P[0] * np.log(1 + np.exp(P[1] * (P[2] - (z - P[3]) ** 2))) + P[4]
    return nz

def FermiDirac(P,k):
    #P[0]=beta*mu, P[1]=mu (in k^2 unit)
    return 1/(np.exp(P[0]*(k**2/P[1]-1))+1)

def GetEF_Ideal(mu,T):

    mli = 9.988346 * 10 ** (-27)
    hbar = 1.0545718 * 10 ** (-34)
    hh = 2 * np.pi * hbar

    beta_mu = mu / T
    mu_k = mu * hh * 2 * mli / hbar ** 2

    kgrid = np.linspace(0, 2 * np.sqrt(np.max([mu, T]) * hh * 2 * mli / hbar ** 2), 4000)
    fk = FermiDirac([beta_mu, mu_k], kgrid)

    Intfun = fk * kgrid ** 2 / (2 * np.pi ** 2)

    n = np.trapz(Intfun, kgrid)
    EF = hbar ** 2 * (6 * np.pi ** 2 * n) ** (2 / 3) / (2 * mli) / hh

    return EF

def P_Pup_IdealFermigas_EOS(TTilde_up,x):
    # Return P_total/P_0up using the ideal two component ideal Fermi gas EoS
    # TTilde_up is the
    if np.isscalar(TTilde_up): TTilde_up=np.array([TTilde_up])
    if np.isscalar(x): x = np.array([x])

    TTilde_EOS=IdealEoS_dict['TTilde']
    PTIlde_EOS=IdealEoS_dict['PTilde']
    TTilde_down=TTilde_up/(x**(2/3))

    mask1=TTilde_up<min(TTilde_EOS)
    mask2=TTilde_up<min(TTilde_EOS)
    TTilde_up[mask1] = min(TTilde_EOS)
    TTilde_down[mask2] = min(TTilde_EOS)

    PTilde_up=PTilde_T_fun(TTilde_up)
    PTilde_down=PTilde_T_fun(TTilde_down)

    P_Pup=PTilde_up+PTilde_down*(x**(5/3))

    return P_Pup

def z_IdealFermigas_EOS(TTilde_up,x):
    # Return P_total/P_0up using the ideal two component ideal Fermi gas EoS
    # TTilde_up is the
    if np.isscalar(TTilde_up): TTilde_up=np.array([TTilde_up])
    if np.isscalar(x): x = np.array([x])

    TTilde_EOS=IdealEoS_dict['TTilde']
    PTIlde_EOS=IdealEoS_dict['PTilde']
    TTilde_down=TTilde_up/(x**(2/3))

    mask1=TTilde_up<min(TTilde_EOS)
    mask2=TTilde_up<min(TTilde_EOS)
    TTilde_up[mask1] = min(TTilde_EOS)
    TTilde_down[mask2] = min(TTilde_EOS)

    PTilde_up=PTilde_T_fun(TTilde_up)
    PTilde_down=PTilde_T_fun(TTilde_down)

    P_Pup=PTilde_up+PTilde_down*(x**(5/3))

    return P_Pup


def ETilde_IdealFermigas_EOS(TTilde_up,x):
    # return E/E0 of an ideal imbalanced Fermi gas
    # E0 is the total energy of gas at same density and imbalance at zero temperature
    # E is the total energy of the gas
    if np.isscalar(TTilde_up): TTilde_up=np.array([TTilde_up])
    if np.isscalar(x): x = np.array([x])

    TTilde_EOS=IdealEoS_dict['TTilde']
    PTIlde_EOS=IdealEoS_dict['PTilde']
    TTilde_down=TTilde_up/(x**(2/3))

    mask1=TTilde_up<min(TTilde_EOS)
    mask2=TTilde_up<min(TTilde_EOS)
    TTilde_up[mask1] = min(TTilde_EOS)
    TTilde_down[mask2] = min(TTilde_EOS)

    PTilde_up=PTilde_T_fun(TTilde_up)
    PTilde_down=PTilde_T_fun(TTilde_down)

    ETilde=(PTilde_up+PTilde_down*(x**(5/3)))/(1+(x**(5/3)))

    return ETilde



def mu_Polaron_EOS(TTilde_up, x, A=-0.615, m_eff=1.25):
    # Return P_total/P_0up using the Fermi liquid pressure ansatz
    # A and m_eff are the binding energy and effective mass for the polaron
    # all the unitful number in the calculation is normalized by the Fermi energy of the majority

    if np.isscalar(TTilde_up): TTilde_up=np.array([TTilde_up])
    if np.isscalar(x): x = np.array([x])


    TTilde_EOS = IdealEoS_dict['TTilde']
    PTIlde_EOS = IdealEoS_dict['PTilde']

    TTilde_down = TTilde_up / (x ** (2 / 3))
    TTilde_down_eff = TTilde_down*m_eff

    mask_down_eff = TTilde_down_eff < min(TTilde_EOS)
    TTilde_down_eff[mask_down_eff]= min(TTilde_EOS)
    # mu_polaron=mu_down-A*mu_up, Z_mu_polaron=exp(mu_polaron/k_B T)
    Z_mu_polaron=Z_T_fun(TTilde_down_eff)
    mu_polaron=np.log(Z_mu_polaron)*TTilde_up

    #EF_up_0 is the Fermi energy corresponds to n_0(mu_up,T,m)
    n_up_0=1+A*x
    EF_up_0=n_up_0**(2/3)
    #get mu_up
    Z_mu_up = Z_T_fun(TTilde_up/EF_up_0)
    mu_up = np.log(Z_mu_up) * TTilde_up

    #mu_down=mu_polaron+A*mu_up
    mu_down=mu_polaron+A*mu_up

    return mu_up,mu_down

def P_Pup_Polaron_EOS(TTilde_up, x, A=-0.615, m_eff=1.25):
    # Return P_total/P_0up using the Fermi liquid pressure ansatz
    # A and m_eff are the binding energy and effective mass for the polaron
    # all the unitful number in the calculation is normalized by the Fermi energy of the majority

    if np.isscalar(TTilde_up): TTilde_up=np.array([TTilde_up])
    if np.isscalar(x): x = np.array([x])


    TTilde_EOS = IdealEoS_dict['TTilde']
    PTIlde_EOS = IdealEoS_dict['PTilde']

    TTilde_down = TTilde_up / (x ** (2 / 3))
    TTilde_down_eff = TTilde_down*m_eff

    mask_down_eff = TTilde_down_eff < min(TTilde_EOS)
    TTilde_down_eff[mask_down_eff]= min(TTilde_EOS)
    # mu_polaron=mu_down-A*mu_up, Z_mu_polaron=exp(mu_polaron/k_B T)
    Z_mu_polaron=Z_T_fun(TTilde_down_eff)
    mu_polaron=np.log(Z_mu_polaron)*TTilde_up

    #EF_up_0 is the Fermi energy corresponds to n_0(mu_up,T,m)
    n_up_0=1+A*x
    EF_up_0=n_up_0**(2/3)
    #get mu_up
    Z_mu_up = Z_T_fun(TTilde_up/EF_up_0)
    mu_up = np.log(Z_mu_up) * TTilde_up

    #mu_down=mu_polaron+A*mu_up
    mu_down=mu_polaron+A*mu_up

    P_up = 15*np.sqrt(np.pi)/(2**3)*(TTilde_up**(5/2))*(-PolyLogFrac(5/2, -Z_mu_up))
    P_down= 15*np.sqrt(np.pi)/(2**3)*(m_eff**(3/2))*(TTilde_up**(5/2))*(-PolyLogFrac(5/2, -Z_mu_polaron))

    P_Pup0=P_up+P_down

    return P_Pup0


def P_Ideal_mu(mu, T, m=9.988346e-27):
    """Output the pressure of the Ideal gas in unit of Hz*um^{-3}.\n
     mu is the chemical potential, T is the temperature (in Hz)"""
    if np.isscalar(mu):
        mu = np.array([mu])
    if np.isscalar(T):
        T = np.array([T])

    z=np.exp(mu/T)
    P=1e-18*(T**(5/2))/(spconstants.h**(3/2))*(2*np.pi*m)**(3/2) * (-PolyLogFrac(5 / 2, -z))
    return P

def IdealGasPV( P,V ):
    '''Get the pressure of the ideal Fermi gas with trap chemical potential mu (P[0]), and temperature T(P[1]), The
    pressure is  in unit of um^{-3}*Hz'''
    mli = 9.988346e-27
    hbar = 1.0545718e-34
    hh = 2 * np.pi * hbar

    mu_local = P[0] - V
    beta_mu = mu_local / P[1]
    Z_vec = np.exp(beta_mu)

    P = 1e-18 * (P[1] ** (5 / 2)) / (spconstants.h ** (3 / 2)) * (2 * np.pi * mli) ** (3 / 2) * (-PolyLogFrac(5 / 2, -Z_vec))

    return P

# Fit the ideal fermi gas EOS to get mu and T
def PressureIdealFitFudge( V,P,P0 ):
    '''Fit the pressure distribution with a fudge'''
    def fitfun(x,mu,T,fudge):
        return fudge * IdealGasPV( [mu,T],x )
    P = curve_fit(fitfun, V, P, P0)

    return P

def PressureIdealFit( V,P,P0 ):
    '''Fit the pressure distribution with a fudge'''
    def fitfun(x,mu,T):
        return IdealGasPV( [mu,T],x )
    P = curve_fit(fitfun, V, P, P0)

    return P


def TFfun_project_r(x,n0,x0,rTF):
    '''Calculate the line of sight intgrated density of a Thomas-Fermi profile:
    n_0 is the center density, x0 is the trap center and r_TF is the Thomas Fermi radius'''
    return np.real( n0* ((1-(x-x0)**2/(rTF)**2)* (0.5 * (np.sign(1-(x-x0)**2/(rTF)**2) + 1)))**2)

def TF_project_r_fit(x,n,R0):
    '''line of sight intgrated Thomas Fermi profile fit, output P: P[0]=center density,
    P[1]=center of the trap, P[2]=Thomas Fermi radius.
    Input: x,n: fitting profile, RO: initial guess'''
    m=np.argmax(n)
    n_max=n[m]
    x0=x[m]
    P=curve_fit(TFfun_project_r, x, n,[n_max,x0,R0])
    return P

def TFfun_project_z(z,n0,z0,zTF):
    '''Calculate the line of sight intgrated density of a Thomas-Fermi profile:
    n_0 is the center density, x0 is the trap center and r_TF is the Thomas Fermi radius'''
    return np.real( n0* ((1-(z-z0)**2/(zTF**2))* (0.5 * (np.sign(1-(z-z0)**2/(zTF)**2) + 1)))**(5/2))

def TF_project_z_fit(z,n,R0):
    '''line of sight intgrated Thomas Fermi profile fit, output P: P[0]=center density,
    P[1]=center of the trap, P[2]=Thomas Fermi radius.
    Input: x,n: fitting profile, RO: initial guess'''
    m=np.argmax(n)
    n_max=n[m]
    z0=z[m]
    P=curve_fit(TFfun_project_z, z, n,[n_max,z0,R0])
    return P

def Boltzmann(P,V):
    '''P[0]: amplitude, P[1]: k_BT'''
    return P[0]*np.exp(-V/P[1])


def BoltzmannFit(V, n, P0):
    '''P[0]: amplitude, P[1]: k_BT'''

    def fitfun(V, n0, T):
        return Boltzmann([n0, T], V)

    P = curve_fit(fitfun, V, n, P0)
    return P


def PTilde_Arb(TTilde, x, T0=0.5, T1=1.3):
    """An arbitrary connection between the polaron EoS and the virial expansion"""

    if np.isscalar(TTilde):
        TTilde = np.array([TTilde])

    mask1 = TTilde < T0
    mask2 = (TTilde >= T0) & (TTilde < T1)
    mask3 = (TTilde >= T1)

    PTilde = TTilde*0

    DeltaP=Virial.PTilde_Virial_imb(T1,x)[0]-P_Pup_Polaron_EOS(T1, x)
    Deltax=T1-T0

    PTilde[mask1] = P_Pup_Polaron_EOS(TTilde[mask1], x)

    PTilde[mask2] = P_Pup_Polaron_EOS(TTilde[mask2], x) + np.sin((TTilde[mask2]-T0)/Deltax*np.pi/2)*DeltaP

    if sum(mask3)>0:
        PTilde[mask3] = Virial.PTilde_Virial_imb(TTilde[mask3],x)[0]

    return PTilde

def T_sol_arb(PTilde,x):
    """Solve the normalized temperature T/T_F from the connected EoS between polaron EoS and Virial,
    see zsharp.thermodynamics.PTilde_Arb"""
    T_0 = TTilde_P_fun(PTilde)

    if T_0 < 0.2:
        T_low = 0.01
        T_high = 0.4
        N_grid = 30
    else:
        T_low = T_0 * 0.6
        T_high = T_0 * 1.4
        N_grid = 15

    if T_0 > 1:
        N_grid = 5

    T_sol_grid = np.linspace(T_low, T_high, N_grid)
    P_sol_grid = PTilde_Arb(T_sol_grid, x)
    # print(N_grid)

    T_interp_sol = interp1d(P_sol_grid, T_sol_grid, fill_value='extrapolate')

    T_sol = T_interp_sol(PTilde)
    if T_sol < 0.01:
        T_sol = 0.00

    return T_sol