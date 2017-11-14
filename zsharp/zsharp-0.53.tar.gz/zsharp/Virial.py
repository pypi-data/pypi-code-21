# functions and calculations about the virial expansion for a imbalanced Fermi gas

import numpy as np
from scipy.optimize import curve_fit
from scipy.optimize import root
from scipy.special import gamma
from scipy.interpolate import interp1d
from zsharp import thermodynamics

# The virial expansion coefficient we use here:
Db2ref = 1/np.sqrt(2) # PHYSICAL REVIEW A 82, 023619 (2010)
Db3ref = -0.35501298 # PHYSICAL REVIEW A 82, 043626 (2010)
import scipy.constants as spconstants

def nTilde_up_Virial_imb(z1,z2):
    # z1, z2 is the vector of the fugacity of majority and minority of the cloud, the function returns the normalized density in the cloud.
    # The density is normailized by (\lambda)^(-3), lambda is the thermal wavelength of the single particle lambda=h/(2\pi m k_B T)

    if np.isscalar(z1):
        z1 = np.array([z1])
    if np.isscalar(z2):
        z2 = np.array([z2])

    nTilde_0=-thermodynamics.PolyLogFrac(3/2,-z1) #ideal fermi gas density
    nTilde_up=nTilde_0+(2*z1*z2*Db2ref)+(2*z1**2*z2+z1*z2**2)*Db3ref

    return nTilde_up


def nTilde_down_Virial_imb(z1, z2):
    # z1, z2 is the vector of the fugacity of majority and minority of the cloud, the function returns the normalized density in the cloud.
    # The density is normailized by (\lambda)^(-3), lambda is the thermal wavelength of the single particle lambda=h/(2\pi m k_B T)

    if np.isscalar(z1):
        z1 = np.array([z1])
    if np.isscalar(z2):
        z2 = np.array([z2])

    nTilde_0 = -thermodynamics.PolyLogFrac(3 / 2, -z2)  # ideal fermi gas density
    nTilde_up = nTilde_0 + (2 * z1 * z2 * Db2ref) + ( (z1 ** 2) * z2 + 2 * z1 * (z2 ** 2)) * Db3ref

    return nTilde_up

def TTilde_up_Virial_imb(z1,z2):
    # k_B T/EF_up as a function of the fugacity of the two state
    if np.isscalar(z1):
        z1 = np.array([z1])
    if np.isscalar(z2):
        z2 = np.array([z2])
    return 4*np.pi/((6*(np.pi**2))**(2/3))*(nTilde_up_Virial_imb(z1,z2)**(-2/3))

def x_con_Virial_imb(z1,z2):
    # minority concentration x=n_down/n_up as a function of fugacity
    if np.isscalar(z1):
        z1 = np.array([z1])
    if np.isscalar(z2):
        z2 = np.array([z2])
    return nTilde_down_Virial_imb(z1,z2)/nTilde_up_Virial_imb(z1, z2)

def f_z(z1,z2,x,TTilde):
    # the function for solving the fugacity: minority concentration and normalized temperature
    f1=x_con_Virial_imb(z1,z2)[0]-x
    f2=TTilde_up_Virial_imb(z1,z2)[0]-TTilde
    return [f1,f2]

def Solve_z_Virial_imb(TTilde_up,x):
    """solve the fugacity with Virial expansion at TTilde and x"""
    if np.isscalar(TTilde_up):
        TTilde_up = np.array([TTilde_up])
    if np.isscalar(x):
        x = np.array([x])

    z1=TTilde_up*x*0
    z2=TTilde_up*x*0
    sollist=[]
    flag=[]


    for i in range(0,len(z1)):

        def solvefun(z_sol):
            return f_z(z_sol[0],z_sol[1],(x*TTilde_up/TTilde_up)[i],(TTilde_up*x/x)[i])

        x0 = [max(min(thermodynamics.Z_T_fun(TTilde_up)[i], 1), 0),
              max(min(thermodynamics.Z_T_fun(TTilde_up / (x** (2 / 3)))[i], 1), 0)]
        sol = root(solvefun, x0, jac=False, method='lm')
        z1[i] = sol.x[0]
        z2[i] = sol.x[1]
        sollist.append(sol)
        flag.append(not sol.success)

    # mask1=z1>5
    # mask2=z2>5
    mask1 = z1 > 1
    mask2 = z2 > 1
    mask=mask1 | mask2 | flag
    z1[mask]=np.nan
    z2[mask]=np.nan

    return z1,z2,sollist,flag

def PTilde_Virial_imb(TTilde_up,x):
    """Output the total pressure of the imbalanced gas normalized by the majority zero temperature pressure P_0.\n
    TTilde_up and x are the majority normalized temperature and minority concentration n_down/n_up"""
    if np.isscalar(TTilde_up):
        TTilde_up = np.array([TTilde_up])
    if np.isscalar(x):
        x = np.array([x])

    z1,z2,sollist,flag=Solve_z_Virial_imb(TTilde_up, x)

    P_up_0 = 15 * np.sqrt(np.pi) / (2 ** 3) * (TTilde_up ** (5 / 2)) * (-thermodynamics.PolyLogFrac(5 / 2, -z1))
    P_down_0 = 15 * np.sqrt(np.pi) / (2 ** 3)  * (TTilde_up ** (5 / 2)) * (-thermodynamics.PolyLogFrac(5 / 2, -z2))

    P_int=15/8*np.sqrt(np.pi) * (TTilde_up ** (5 / 2)) * 2 * (z1*z2*Db2ref+((z1**2*z2+z1*z2**2)/2)*Db3ref)

    PTilde=P_up_0+P_down_0+P_int

    return PTilde,z1,z2

def P_Virial_imb_mu(mu_up,mu_down,T):
    """Output the total pressure of the imbalanced gas in unit of Hz*um^{-3}.\n
    TTilde_up and x are the majority normalized temperature and minority concentration n_down/n_up"""
    m = 9.988346e-27

    if np.isscalar(mu_up):
        mu_up = np.array([mu_up])
    if np.isscalar(mu_down):
        mu_down = np.array([mu_down])
    if np.isscalar(T):
        T = np.array([T])
    z_up=np.exp(mu_up/T)
    z_down=np.exp(mu_down/T)
    P0_up=thermodynamics.P_Ideal_mu(mu_up,T)
    P0_down=thermodynamics.P_Ideal_mu(mu_down,T)
    P_int=1e-18*(T**(5/2))/(spconstants.h**(3/2))*(2*np.pi*m)**(3/2)*(2*z_up*z_down*Db2ref+((z_up**2)*z_down+z_up*(z_down**2))*Db3ref)

    P=P0_up+P0_down+P_int

    return P

