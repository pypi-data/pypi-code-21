from __future__ import division
import numpy as np
#import pdb
from EPIC.common import if_not_given, speedoflight, CL68 # in m/s
from EPIC.common import LogNormalMode, LogNormalPDF, LogNormalCDF, NormalPDF, z_of_a
import warnings
import uncertainties.umath as um
import scipy.integrate as integrate
from scipy.special import erf

warnings.filterwarnings('ignore')

def growth_rate_sigma_eight(z, cosmology):
    '''
    um.sqrt and um.exp are used in order to support uncertainties. However, they don't work with arrays of redshift. 
    Need to perform the calculation at individual z's and then group them
    '''

    assert cosmology.model == 'model2'

    #These variables aren't needed in this function
    #Obh2 = 0
    #Orh2 = 0
    #Okh2 = 0

    h2 = if_not_given(cosmology.params, cosmology.fixed, 'h', 0.7)**2
    Och2 = if_not_given(cosmology.params, cosmology.fixed, 'Och2', 0.26*h2)
    OmegaDE0 = 1 - Och2/h2
    #old best fit value:
    #OmegaDE0 = if_not_given(cosmology.params, cosmology.fixed, 'Ode0', 0.686438213675)

    sigma8today = if_not_given(cosmology.params, cosmology.fixed, 's8',
            0.726599529253)
    w0 = if_not_given(cosmology.params, cosmology.fixed, 'w0', -1.0)
    w1 = if_not_given(cosmology.params, cosmology.fixed, 'w1', 0.)

    xi = if_not_given(cosmology.params, cosmology.fixed, 'xi', 0.)

    ## model 2 only
    tw0 = w0 + xi
    tw1 = w1 + xi

    gamma_0 = 3*(1. - tw0 + 6*xi)/(5. - 6 * tw0)
    gamma_1 = (-gamma_0**2 + gamma_0*(1. + 12*tw1 + 6*xi) - 6*w1 + 6*xi*(5. - 6 * (w0 - xi)))
    gamma_1 /= 2*(5. - 12 * tw0)
    
    baromega01 = (w0 - w1)/tw0

    aux = OmegaDE0 * (1.+z)**(3*tw0)
    OmegaDEz = aux * (1 - OmegaDE0 + aux)**(tw1/tw0)
    OmegaDEz /= 1 - OmegaDE0 + aux * (1 - OmegaDE0 + aux)**(tw1/tw0)


    Delta2DE = OmegaDEz**2 - OmegaDE0**2
    Delta1DE = OmegaDEz - OmegaDE0

    epsilon_1 = gamma_0 - baromega01
    w2 = 0
    epsilon_2 = - gamma_0**2/4. + gamma_0/2. * (0.5 + baromega01) + gamma_1/2. - 1./2/tw0 * (w0 * baromega01 - w2 + w1*tw1/tw0)
    sigma8 = sigma8today * (OmegaDEz/OmegaDE0)**(-1./(3*tw0)) * um.exp(1./(3*tw0) * (Delta2DE*epsilon_2 + Delta1DE*epsilon_1))
    gamma_ = gamma_0 + gamma_1 * OmegaDEz
    f = (1. - OmegaDEz)**gamma_
    ftil = f + 3 * xi * OmegaDEz/(1. - OmegaDEz)

    return f, ftil, sigma8, gamma_0, gamma_1, gamma_, OmegaDEz

def myfsigma8(z, cosmology):

    _, ftil, sigma8, _, _, _, _ = growth_rate_sigma_eight(z, cosmology)
    return ftil * sigma8

#### JLA functions
def Eh(z, cosmology):
    # valid for the following models:
    # 'wCDM', 'fastvarying1', 'fastvarying2', 'fastvarying3'

    if hasattr(cosmology, 'H_solution'):
        return float(cosmology.H_solution(z))/100

    h2 = if_not_given(cosmology.params, cosmology.fixed, 'h', 0.7)**2
    Och2 = if_not_given(cosmology.params, cosmology.fixed, 'Och2', 0.26*h2)
    Obh2 = if_not_given(cosmology.params, cosmology.fixed, 'Obh2', 0.04*h2)
    Orh2 = if_not_given(cosmology.params, cosmology.fixed, 'Orh2', 8e-5*h2)
    #Okh2 = if_not_given(cosmology.params, cosmology.fixed, 'Okh2', 0)
    Okh2 = 0
    Odh2 = h2 - Och2 - Obh2 - Orh2 - Okh2
    
    # h is defined by Obh2 + Och2 + Odh2 + Okh2 + Orh2 = h2

    if cosmology.model == 'lcdm':
        return np.sqrt((Obh2 + Och2) * (1+z)**3 + Orh2 * (1+z)**4 + Okh2 * (1+z)**2 + Odh2)

    elif cosmology.model == 'wCDM':
        wDE = if_not_given(cosmology.params, cosmology.fixed, 'w0', -1)
        return np.sqrt((Obh2 + Och2) * (1+z)**3 + Orh2 * (1+z)**4 + Okh2 * (1+z)**2 + Odh2 * (1+z)**(3*(1+wDE)))

    elif cosmology.model == 'model2':
        Obh2 = 0
        Orh2 = 0
        Okh2 = 0
        h2 = Obh2 + Och2 + Orh2 + Odh2 + Okh2
        Omega_DE0 = Odh2/h2
        w0 = if_not_given(cosmology.params, cosmology.fixed, 'w0', -1)
        w1 = if_not_given(cosmology.params, cosmology.fixed, 'w1', 0)
        xi = if_not_given(cosmology.params, cosmology.fixed, 'xi', 0.0)

        def OmegaDE(Z):
            tw0 = w0 + xi
            tw1 = w1 + xi
            aux = Omega_DE0 * (1.+Z)**(3*tw0)
            OmegaDEz = aux * (1 - Omega_DE0 + aux)**(tw1/tw0)
            OmegaDEz /= 1 - Omega_DE0 + aux * (1 - Omega_DE0 + aux)**(tw1/tw0)
            return OmegaDEz

        #full solution, xi <> 0 and w1 <> 0:
        #return np.sqrt( (1-Omega_DE0) * np.exp(integrate.quad(lambda zbar: 3/(1+zbar)*(1 - xi * OmegaDE(zbar)/(1 - OmegaDE(zbar))), 0, z)[0]) + Omega_DE0 * np.exp(integrate.quad(lambda zbar: 3/(1+zbar)*(1 + w0 + w1*OmegaDE(zbar) + xi), 0, z)[0]) )

        # for w constant:
        #if xi == 0:
        #return np.sqrt( (1-Omega_DE0) * (1+z)**3 + Omega_DE0 * (1+z)**(3*(1 + w0)))
        #xi <> 0
        return np.sqrt( (1-Omega_DE0) * np.exp(integrate.quad(lambda zbar: 3/(1+zbar)*(1 - xi * OmegaDE(zbar)/(1 - OmegaDE(zbar))), 0, z)[0]) + Omega_DE0 * (1+z)**(3*(1 + w0 + xi)))

    elif cosmology.model == 'fastvarying1':
        wf = if_not_given(cosmology.params, cosmology.fixed, 'wf', -1)
        wp = if_not_given(cosmology.params, cosmology.fixed, 'wp', 0)
        #Deltaw = if_not_given(cosmology.params, cosmology.fixed, 'Deltaw', 2)
        #wp = wf + Deltaw
        at = if_not_given(cosmology.params, cosmology.fixed, 'at', 0.5)
        tau = if_not_given(cosmology.params, cosmology.fixed, 'tau', 0.1)

        def f1(A):
            taum1 = 1/tau
            logf1 = 3*tau*(wp-wf) * ( taum1 * np.log(A) + np.log(1 + np.exp(taum1 * np.log(at/A)) ) - np.log(1 + np.exp(taum1 * np.log(at)) ) )
            return np.exp(logf1)
            #return ((A**taum1 + at**taum1)/(1 + at**taum1))**(3*tau*(wp-wf))

        a_of_z = a(z)
        return np.sqrt(Okh2 * a_of_z**-2 + Orh2 * a_of_z**-4 + (Och2 + Obh2) * a_of_z**-3 + Odh2 * a_of_z**(-3*(1+wp)) * f1(a_of_z))

    elif cosmology.model == 'fastvarying2':
        wp = if_not_given(cosmology.params, cosmology.fixed, 'wp', 0)
        w0 = if_not_given(cosmology.params, cosmology.fixed, 'w0', -1)
        #Deltaw = if_not_given(cosmology.params, cosmology.fixed, 'Deltaw', 2)
        #wp = w0 + Deltaw
        at = if_not_given(cosmology.params, cosmology.fixed, 'at', 0.5)
        tau = if_not_given(cosmology.params, cosmology.fixed, 'tau', 0.1)

        def f2(A):
            taum1 = 1/tau
            one_minus_at_to_mtaum1 = 1 - np.exp( - taum1 * np.log( at ))
            return 3*(w0-wp)*\
                    (1 + one_minus_at_to_mtaum1*tau +\
                    A * (tau * ( np.exp( taum1 * np.log(A/at) ) - 1) - 1)) /\
                    (1+tau) / one_minus_at_to_mtaum1

        a_of_z = a(z)
        return np.sqrt(Okh2 * a_of_z**-2 + Orh2 * a_of_z**-4 + (Och2 + Obh2) * a_of_z**-3 + Odh2 * a_of_z**(-3*(1+wp)) * np.exp(f2(a_of_z)))

    elif cosmology.model == 'fastvarying3':
        wp = if_not_given(cosmology.params, cosmology.fixed, 'wp', -1)
        w0 = if_not_given(cosmology.params, cosmology.fixed, 'w0', -1)
        at = if_not_given(cosmology.params, cosmology.fixed, 'at', 0.5)
        tau = if_not_given(cosmology.params, cosmology.fixed, 'tau', 0.1)

        def f3(A):
            taum1 = 1/tau
            one_minus_at_to_mtaum1 = 1 - np.exp( - taum1 * np.log( at ))
            return 3*(w0-wp)*tau *\
                    (1 + one_minus_at_to_mtaum1 +\
                    np.exp(taum1 * np.log(A)) -\
                    2 * np.exp(taum1 * np.log(at)) \
                    ) / 2 /one_minus_at_to_mtaum1

        a_of_z = a(z)
        return np.sqrt(Okh2 * a_of_z**-2 + Orh2 * a_of_z**-4 + (Och2 + Obh2) * a_of_z**-3 + Odh2 * a_of_z**(-3*(1+wp)) * np.exp(f3(a_of_z)))

    elif cosmology.model == 'LIclusters': # constant dark energy equation of state
        Och2 = if_not_given(cosmology.params, cosmology.fixed, 'Och2', 0.36*h2)
        xi = if_not_given(cosmology.params, cosmology.fixed, 'xi', 0)
        a_of_z = a(z)
        E2h2 = h2 + Och2*(a_of_z**(-3*(1-xi)) - 1)/(1-xi)
        return um.sqrt(E2h2)

def integrate_densities(cosmology, log10Ai=-5, size=10000):
    H0 = if_not_given(cosmology.params, cosmology.fixed, 'H0', 72.)
    Gamma = if_not_given(cosmology.params, cosmology.fixed, 'Gamma')
    Omega_Gamma = if_not_given(cosmology.params, cosmology.fixed,
            'Omega_Gamma')
    Omega_baryons = if_not_given(cosmology.params, cosmology.fixed,
            'Omega_baryons')
    Omega_radiation = if_not_given(cosmology.params, cosmology.fixed,
            'Omega_radiation')
    rho_Gamma, rho_phi0 = (np.zeros(size) for _ in range(2))
    rho_Gamma[-1] = Omega_Gamma
    Omega_phiplus = Omega_Gamma / Gamma
    if 'wnu0' in cosmology.model:
        Omega_c = if_not_given(cosmology.params, cosmology.fixed, 'Omega_c')
        Omega_phi0 = 1 - (Omega_phiplus + Omega_c + Omega_baryons + Omega_radiation)
        rho_c = np.zeros(size)
        rho_c[-1] = Omega_c
        derivatives = [
                rho_Gamma_derivative,
                rho_phi0_derivative,
                rho_c_derivative,
                ]

    else:
        rho_psi, rho_nu = (np.zeros(size) for _ in range(2))
        Omega_psi = if_not_given(cosmology.params, cosmology.fixed, 'Omega_psi')
        Omega_nu = if_not_given(cosmology.params, cosmology.fixed, 'Omega_nu')
        Omega_phi0 = 1 - (Omega_phiplus + Omega_nu + Omega_psi + Omega_baryons \
                + Omega_radiation)
        rho_psi[-1] = Omega_psi
        rho_nu[-1] = Omega_nu
        derivatives = [
                rho_Gamma_derivative,
                rho_phi0_derivative,
                rho_psi_derivative,
                rho_nu_derivative
                ]
    rho_phi0[-1] = Omega_phi0

    A = np.logspace(log10Ai, 0, size)

    i = -2
    if 'wnu0' in cosmology.model:
        while i >= -size:
            da = -(A[i+1] - A[i])
            densities = np.array([rho_Gamma[i+1], rho_phi0[i+1], rho_c[i+1]])
            rho_Gamma[i], rho_phi0[i], rho_c[i] = darkSU2_rk4(da, A[i+1],
                    Hubble, densities, derivatives, cosmology)
            i -= 1
        return A, rho_Gamma, rho_phi0, rho_c

    else:
        while i >= -size:
            da = -(A[i+1] - A[i])
            densities = np.array([rho_Gamma[i+1], rho_phi0[i+1], rho_psi[i+1],
                    rho_nu[i+1]])
            rho_Gamma[i], rho_phi0[i], rho_psi[i], rho_nu[i] = \
                    darkSU2_rk4(da, A[i+1], Hubble,
                            densities, derivatives, cosmology)
            i -= 1
        return A, rho_Gamma, rho_phi0, rho_psi, rho_nu

def integrate_rhod_wcons(cosmology, log10Ai=-4, size=10000):
    h2 = if_not_given(cosmology.params, cosmology.fixed, 'h', 0.7)**2
    Och2 = if_not_given(cosmology.params, cosmology.fixed, 'Och2', 0.36 * h2)
    Omega_c = Och2/h2
    Omega_d = 1 - Omega_c
    rho_d = np.zeros(size)
    rho_d[-1] = Omega_d
    A = np.logspace(log10Ai, 0, size)

    i = -2
    while i >= -size:
        da = -(A[i+1] - A[i])
        rho_d[i] = LIclusters_wd_rk4(da, A[i+1], rho_d[i+1], rho_d_derivative, cosmology)
        i -= 1
    return A, rho_d

def darkSU2_rk4(da, A, Hubble, rk_densities, derivatives, cosmology):
    Ha = Hubble(A, rk_densities, cosmology)
    k1 = np.array([function(rk_densities, A, Ha, cosmology) \
            for function in derivatives]
            ) 
    k1_densities = rk_densities + da/2 * k1

    Ha = Hubble(A + da/2, k1_densities, cosmology)
    k2 = np.array([function(k1_densities, A, Ha, cosmology) \
            for function in derivatives]
            ) 
    k2_densities = k1_densities + da/2 * k2

    Ha = Hubble(A + da/2, k2_densities, cosmology)
    k3 = np.array([function(k2_densities, A, Ha, cosmology) \
            for function in derivatives]
            ) 
    k3_densities = k2_densities + da * k3

    Ha = Hubble(A + da, k3_densities, cosmology)
    k4 = np.array([function(k3_densities, A, Ha, cosmology) \
            for function in derivatives]
            ) 

    rk_densities += da/6 * (k1 + 2*k2 + 2*k3 + k4) 
    return rk_densities

def LIclusters_wd_rk4(da, A, rk_density, derivative, cosmology):
    k1 = derivative(rk_density, A, cosmology)
    k1_density = rk_density + da/2 * k1

    k2 = derivative(k1_density, A, cosmology)
    k2_density = k1_density + da/2 * k2

    k3 = derivative(k2_density, A, cosmology)
    k3_density = k2_density + da * k3

    k4 = derivative(k3_density, A, cosmology)

    rk_density += da/6 * (k1 + 2*k2 + 2*k3 + k4) 
    return rk_density

def rho_Gamma_derivative(densities, A, Ha, cosmology):
    Gamma = if_not_given(cosmology.params, cosmology.fixed, 'Gamma')
    rhoGamma = densities[0]
    return - Gamma * rhoGamma / A / Ha

def rho_phi0_derivative(densities, A, Ha, cosmology):
    mu_phi0 = if_not_given(cosmology.params, cosmology.fixed, 'mu_phi0')
    rhoGamma = densities[0]
    return mu_phi0 * rhoGamma / A / Ha

def rho_c_derivative(densities, A, Ha, cosmology):
    mu_phi0 = if_not_given(cosmology.params, cosmology.fixed, 'mu_phi0')
    rhoGamma, _, cdm = densities
    return (1 - mu_phi0) * rhoGamma / A / Ha - 3 * cdm / A

def rho_psi_derivative(densities, A, Ha, cosmology):
    mu_psi = if_not_given(cosmology.params, cosmology.fixed, 'mu_psi')
    rhoGamma, _, psi, _ = densities
    return mu_psi * rhoGamma / A / Ha - 3 * psi / A

def rho_nu_derivative(densities, A, Ha, cosmology):
    w_nu = if_not_given({}, cosmology.fixed, 'w_nu', 1/3)
    mu_psi = if_not_given(cosmology.params, cosmology.fixed, 'mu_psi')
    mu_phi0 = if_not_given(cosmology.params, cosmology.fixed, 'mu_phi0')
    rhoGamma, _, _, nu = densities
    return (1 - mu_phi0 - mu_psi) * rhoGamma / A / Ha - 3 * (1 + w_nu) * nu / A

def rho_d_derivative(densities, A, cosmology):
    wd = if_not_given(cosmology.params, cosmology.fixed, 'wd')
    xi = if_not_given(cosmology.params, cosmology.fixed, 'xi')
    rho_c = rho_c_of_a(A, cosmology)
    rho_d = densities
    return - 3/A * ( rho_d * (1 + wd) + xi * rho_c ) 

def rho_c_of_a(a, cosmology):
    xi = if_not_given(cosmology.params, cosmology.fixed, 'xi')
    Och2 = if_not_given(cosmology.params, cosmology.fixed, 'Och2')
    h = if_not_given(cosmology.params, cosmology.fixed, 'h')
    Omega_c = Och2/h**2
    return Omega_c * a**(-3*(1-xi))

def rho_baryons_of_a(a, cosmology):
    Omega_baryons = if_not_given(cosmology.params, cosmology.fixed, 'Omega_baryons')
    return Omega_baryons * a**-3

def rho_radiation_of_a(a, cosmology):
    Omega_radiation = if_not_given(cosmology.params, cosmology.fixed,
            'Omega_radiation')
    return Omega_radiation * a**-4

def Hubble_LIclusters(A, DE_density, cosmology):
    cdm = rho_c_of_a(A, cosmology)
    H0 = if_not_given(cosmology.params, cosmology.fixed, 'h', 0.7) * 100
    Ha = H0 * np.sqrt(DE_density + cdm)
    return Ha

def Hubble(A, densities, cosmology):
    Gamma = if_not_given(cosmology.params, cosmology.fixed, 'Gamma')
    baryons = rho_baryons_of_a(A, cosmology)
    radiation = rho_radiation_of_a(A, cosmology)
    H0 = if_not_given(cosmology.params, cosmology.fixed, 'H0', 72.)
    Ha = H0 * np.sqrt(densities[0]/Gamma + sum(densities[1:]) + baryons + radiation)
    #Hz *= 31557600 * 3.2407793877e-11 # in Gyr^-1
    #Hz /= 3.08567758e19 # in s^-1
    #Hz /= 7.18964869e10 # in yr^-1
    return Ha

def wDE1(A, cosmology): #fastvarying
    wf = if_not_given(cosmology.params, cosmology.fixed, 'wf', -1)
    wp = if_not_given(cosmology.params, cosmology.fixed, 'wp', 0)
    #Deltaw = if_not_given(cosmology.params, cosmology.fixed, 'Deltaw', 2)
    #wp = wf + Deltaw
    at = if_not_given(cosmology.params, cosmology.fixed, 'at', 0.5)
    tau = if_not_given(cosmology.params, cosmology.fixed, 'tau', 0.1)
    return wf + (wp - wf)/(1 + np.exp((1/tau) * np.log(A/at)))

def wDE2(A, cosmology): #fastvarying
    wp = if_not_given(cosmology.params, cosmology.fixed, 'wp', 0)
    w0 = if_not_given(cosmology.params, cosmology.fixed, 'w0', -1)
    #Deltaw = if_not_given(cosmology.params, cosmology.fixed, 'Deltaw', 2)
    #wp = w0 + Deltaw
    at = if_not_given(cosmology.params, cosmology.fixed, 'at', 0.5)
    tau = if_not_given(cosmology.params, cosmology.fixed, 'tau', 0.1)
    taum1 = 1/tau
    return wp + (w0 - wp) * A * (1 - np.exp(taum1 * np.log(A/at))) / (1 - np.exp(-taum1 * np.log(at)))

def wDE3(A, cosmology): #fastvarying
    wp = if_not_given(cosmology.params, cosmology.fixed, 'wp', -1)
    w0 = if_not_given(cosmology.params, cosmology.fixed, 'w0', -1)
    at = if_not_given(cosmology.params, cosmology.fixed, 'at', 0.5)
    tau = if_not_given(cosmology.params, cosmology.fixed, 'tau', 0.1)
    taum1 = 1/tau
    return wp + (w0 - wp) * np.exp(taum1 * np.log(A)) * (1 - np.exp(taum1 * np.log(A/at))) / (1 - np.exp(-taum1*np.log(at)))

def a(z):
    return 1/(1+z)

def lumdistsimple(z, cosmology):
    H0 = 100 # in h km/s/Mpc
    H0 *= 1e-3  # in h m/s/pc
    return (1. + z) * speedoflight/H0 * integrate.quad(lambda Z: 1/Eh(Z, cosmology), 0, z)[0] # distance in pc

def lumdist(zhel, zcmb, cosmology):
    H0 = 100 # in h km/s/Mpc
    H0 *= 1e-3  # in h m/s/pc
    return (1. + zhel) * speedoflight/H0 * integrate.quad(lambda z: 1/Eh(z, cosmology), 0, zcmb)[0] # distance in pc

def muth(datapoints, cosmology):
    return np.array([5 * np.log10(  lumdist(zhel, zcmb, cosmology) / 10  ) for zhel, zcmb in zip(datapoints.zHEL, datapoints.zCMB)])

def muthsimple(redshifts, cosmology):
    return np.array([5 * np.log10( lumdistsimple(z, cosmology) / 10) for z in redshifts])

def H(z, cosmology):
    if hasattr(cosmology, 'H_solution'):
        return float(cosmology.H_solution(z))
    else:
        return 100 * Eh(z, cosmology)
    
def r_s(Z, cosmology): # is actually r_s * (H0/h) /speedoflight
    if cosmology.model == 'model2':
        R_S = integrate.quad(lambda z: 1/Eh(z, cosmology) / np.sqrt(3), Z, np.inf)[0] # * speedoflight/(H0/h) 
    elif 'darkSU2' in cosmology.model:
        Omega_baryons = if_not_given(cosmology.params, cosmology.fixed, 'Omega_baryons')
        Omega_radiation = if_not_given(cosmology.params, cosmology.fixed, 'Omega_radiation')
        zinf = z_of_a(cosmology.rk_densities[0][0])
        R_S = integrate.quad(lambda z: 1/Eh(z, cosmology) / np.sqrt( 3 * (1 + 3*Omega_baryons/(4*Omega_radiation*(1+z))) ), Z, zinf)[0] # * speedoflight/(H0/h) 
    else:
        Orh2 = if_not_given(cosmology.params, cosmology.fixed, 'Orh2', 3.92e-5)
        Obh2 = if_not_given(cosmology.params, cosmology.fixed, 'Obh2', 0.0196)
        R_S = integrate.quad(lambda z: 1/Eh(z, cosmology) / np.sqrt( 3 * (1 + 3*Obh2/(4*Orh2*(1+z))) ), Z, np.inf)[0] # * speedoflight/(H0/h) 
    return R_S

def d_a(z, cosmology): # is actually da_c * (H0/h) / speedoflight
    da_c = integrate.quad(lambda Z: 1/Eh(Z, cosmology), 0, z)[0]
    return da_c # * speedoflight / (H0/h)

def PlanckDistancePriors(cosmology):
    if 'darkSU2' in cosmology.model:
        Omega_baryons = if_not_given(cosmology.params, cosmology.fixed, 'Omega_baryons')
        H0 = if_not_given(cosmology.params, cosmology.fixed, 'H0')
        h = H0/100
        Obh2 = Omega_baryons * h * h
        if 'wnu0' in cosmology.model:
            Omega_c = if_not_given(cosmology.params, cosmology.fixed, 'Omega_c')
            Och2 = Omega_c * h * h 
        else:
            Omega_psi = if_not_given(cosmology.params, cosmology.fixed, 'Omega_psi')
            Och2 = Omega_psi * h * h
    else:
        Och2 = if_not_given(cosmology.params, cosmology.fixed, 'Och2', 0.1274)
        Obh2 = if_not_given(cosmology.params, cosmology.fixed, 'Obh2', 0.0196)

    g1 = 0.0783 * Obh2**-0.238/(1 + 39.5 * Obh2**0.763)
    g2 = 0.560/(1 + 21.1 * Obh2**1.81)
    Omh2 = Obh2 + Och2
    zdec = 1048 * (1 + 0.00124 * Obh2**-0.738) * (1 + g1 * Omh2**g2)
    da_comoving = d_a(zdec, cosmology) # * speedoflight / (H0/h)
    R = np.sqrt( Omh2 ) * da_comoving
    rs = r_s(zdec, cosmology)
    try:
        l_A = np.pi * da_comoving / rs
    except ZeroDivisionError:
        l_A = np.nan
    return np.array([R, l_A, Obh2])

def CMBdistances(cosmology): # old function for WMAP
    if 'darkSU2' in cosmology.model:
        Omega_baryons = if_not_given(cosmology.params, cosmology.fixed, 'Omega_baryons')
        H0 = if_not_given(cosmology.params, cosmology.fixed, 'H0')
        h = H0/100
        Obh2 = Omega_baryons * h * h
        if 'wnu0' in cosmology.model:
            Omega_c = if_not_given(cosmology.params, cosmology.fixed, 'Omega_c')
            Och2 = Omega_c * h * h
        else:
            Omega_psi = if_not_given(cosmology.params, cosmology.fixed, 'Omega_psi')
            Och2 = Omega_psi * h * h
    else:
        Och2 = if_not_given(cosmology.params, cosmology.fixed, 'Och2', 0.1274)
        Obh2 = if_not_given(cosmology.params, cosmology.fixed, 'Obh2', 0.0196)

    g1 = 0.0783 * Obh2**-0.238/(1 + 39.5 * Obh2**0.763)
    g2 = 0.560/(1 + 21.1 * Obh2**1.81)
    Omh2 = Och2 + Obh2
    zdec = 1048 * (1 + 0.00124 * Obh2**-0.738) * (1 + g1 * Omh2**g2)
    da_comoving = d_a(zdec, cosmology) # * speedoflight / H0
    R = np.sqrt( Omh2 ) * da_comoving
    rs = r_s(zdec, cosmology)
    l_A = np.pi * da_comoving / rs
    return np.array([l_A, R, zdec])

def D_V(z, cosmology): # is actually H0/h * D_V / speedoflight
    dac = d_a(z, cosmology)
    DV = dac**2 * z / Eh(z, cosmology)
    DV = DV**(1/3)
    return DV

def rBAO(z_i, cosmology):
    if 'darkSU2' in cosmology.model:
        Omega_baryons = if_not_given(cosmology.params, cosmology.fixed, 'Omega_baryons')
        H0 = if_not_given(cosmology.params, cosmology.fixed, 'H0')
        h = H0/100
        Obh2 = Omega_baryons * h * h
        if 'wnu0' in cosmology.model:
            Omega_c = if_not_given(cosmology.params, cosmology.fixed, 'Omega_c')
            Och2 = Omega_c * h * h
        else:
            Omega_psi = if_not_given(cosmology.params, cosmology.fixed, 'Omega_psi')
            Och2 = Omega_psi * h * h
    else:
        Och2 = if_not_given(cosmology.params, cosmology.fixed, 'Och2', 0.1274)
        Obh2 = if_not_given(cosmology.params, cosmology.fixed, 'Obh2', 0.0196)

    Omh2 = Obh2 + Och2
    b1 = 0.313 * Omh2**-0.419 * (1 + 0.607 * Omh2**0.674)
    b2 = 0.238 * Omh2**0.223
    zd = 1291 * Omh2**0.251 * (1 + b1 * Obh2**b2) / (1 + 0.659 * Omh2**0.828)
    rszd = r_s(zd, cosmology)
    return rszd / D_V(z_i, cosmology)

def th_virial_ratio(cosmology):
    xi = if_not_given(cosmology.params, cosmology.fixed, 'xi', 0.)
    TVR = - (1-6*xi)/(2+3*xi)
    return TVR

def lognormal_parameters_function(cosmology):
    mu = if_not_given(cosmology.params, cosmology.fixed, 'mu', 0.)
    sigma = if_not_given(cosmology.params, cosmology.fixed, 'sigma', 1.)
    x0 = if_not_given({}, cosmology.fixed, 'x0')
    xp = if_not_given({}, cosmology.fixed, 'xp')
    xm = if_not_given({}, cosmology.fixed, 'xm')
    ref_xmin = x0 - xm
    ref_xmax = x0 + xp
    pdf_up = LogNormalPDF(ref_xmax, mu, sigma)
    pdf_low = LogNormalPDF(ref_xmin, mu, sigma)
    cdf_up = LogNormalCDF(ref_xmax, mu, sigma)
    cdf_low = LogNormalCDF(ref_xmin, mu, sigma)
    

    return np.array([
        abs(LogNormalMode(mu, sigma) - x0)/x0,
        abs(pdf_up - pdf_low)/pdf_up,
        abs((cdf_up - cdf_low) - CL68)/CL68,
        ])


