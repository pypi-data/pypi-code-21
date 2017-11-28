import numpy as np
#from EPIC import load_data, common

def derived_Omega_from_Oh2(par, f, burnin, parnames):
    # applies to Och2, Obh2, Omh2, Orh2 for Oc0, Ob0, Om0, Or0
    O0 = np.concatenate([
        F[burnin:, parnames.index(par)]/F[burnin:, parnames.index('h')]**2 \
                for F in f]) if par in parnames else 0
    return O0

def get_Omegas(f, burnin, parnames):
    Oc0, Ob0, Or0 = (derived_Omega_from_Oh2(par, f, burnin, parnames) for par in ('Och2', 'Obh2', 'Orh2'))
    Od0 = 1 - (Oc0 + Ob0 + Or0)
    return (O0 for O0 in (Oc0, Ob0, Or0, Od0) if type(O0) is np.ndarray)

def get_Omega_flat(f, burnin, parnames):
    return 1 - np.sum([
        np.concatenate([F[burnin:, parnames.index(Omega)]/(F[burnin:, parnames.index('Gamma')] if Omega == 'Omega_Gamma' else 1) for F in f]) \
                if Omega in parnames else 0 for Omega in ('Omega_Gamma',
                    'Omega_psi', 'Omega_c', 'Omega_nu',
                    'Omega_baryons', 'Omega_radiation')],
                axis=0)

def derived_wp_from_Deltaw(f, burnin, parnames, model):
    # applies to wf (wp = Deltaw + wf) or w0 (wp = Delta + w0)
    par = 'w0' if model == 'fastvarying3' else 'wf' #fastvarying2
    wp = np.concatenate([
        F[burnin:, parnames.index(par)] + F[burnin:, parnames.index('Deltaw')] \
                for F in f])
    return wp

def derived_astar_wstar(f, burnin, parnames, model):
    # applies to fv2 and fv3 models
    # fv2:
    tau, at, w0, wp = (np.concatenate([F[burnin:, parnames.index(par)] for F in f]) for par in ('tau', 'at', 'w0', 'wp'))
    if model == 'fastvarying2':
        astar = (tau/(tau + 1))**tau * at
        wstar = wp + ( (w0-wp) * tau**tau * (tau+1)**(-tau-1) * at )/(1 - at**(-1/tau))
    elif model == 'fastvarying3':
        astar = at / 2**tau
        wstar = wp + 1/4 * (w0-wp) * at**(1/tau) / (1 - at**(-1/tau))
    else:
        raise AssertionError
    return astar, wstar

def derived_EVR_from_xi(f, burnin, parnames):
    xi = np.concatenate([F[burnin:, parnames.index('xi')] for F in f])
    EVR = -(1-6*xi)/(2+3*xi)
    return EVR

def build_derived_parameters(f, burnin, parnames, model):
    der_combo_chains = []
    der_parnames = [] 

    if 'fastvarying' in model or model == 'lcdm':
        Oc0, Ob0, Or0, Od0 = get_Omegas(f, burnin, parnames)
        for par in ('Oc0', 'Ob0', 'Or0', 'Od0'): 
            der_combo_chains.append(eval(par))
            der_parnames.append(par)
        if model in ('fastvarying2', 'fastvarying3'):
            astar, wstar = derived_astar_wstar(f, burnin, parnames, model)
            for par in ('astar', 'wstar'):
                der_combo_chains.append(eval(par))
                der_parnames.append(par)

        if 'Deltaw' in parnames:
            wp = derived_wp_from_Deltaw(f, burnin, parnames, model)
            der_combo_chains.append(wp)
            der_parnames.append('wp')

    if 'LIclusters' in model:
        Oc0, Od0 = get_Omegas(f, burnin, parnames)
        TVR = derived_EVR_from_xi(f, burnin, parnames)
        for par in ('Oc0', 'Od0', 'TVR'):
            der_combo_chains.append(eval(par))
            der_parnames.append(par)

        """
        #with open('good_NFW_fits.txt', 'r') as group_file:
        #with open('regular.txt', 'r') as group_file:
        with open('acceptable_NFW_fits.txt', 'r') as group_file:
            clusters = group_file.readlines()
        clusters = [cl.strip() for cl in clusters]
        obsble = clusters[0]
        clusters = clusters[1:]

        r200, M200, c200, kTX = ({} for _ in range(4))
        samples = {}
        from collections import OrderedDict
        import scipy.stats as st
        h = np.concatenate([F[burnin:, parnames.index('h')] for F in f])
        Och2 = np.concatenate([F[burnin:, parnames.index('Och2')] for F in f])
        xi = np.concatenate([F[burnin:, parnames.index('xi')] for F in f])
        g = np.concatenate([F[burnin:, parnames.index('gamma')] for F in f])
        if h.size > 10000:
            h = np.random.choice(h, 10000)
            Och2 = np.random.choice(Och2, 10000)
            xi = np.random.choice(xi, 10000)
            g = np.random.choice(g, 10000)
            TVR = np.random.choice(TVR, 10000)


        from hobservables import a
        for cl in clusters:
            cluster = load_data.Cluster(cl, obsble)
            a_of_z = a(cluster.z)
            # w = -1 only
            E2h2 = h**2 + Och2*(a_of_z**(-3*(1-xi)) - 1)/(1-xi)
            Hz = 100 * np.sqrt(E2h2)/ h
            rhoc = common.rho_critical(Hz)
            Gprime_over_F = cluster.fc / cluster.r200**2
            Gprime_over_F *= 1 / rhoc * (- 9)/(8*np.pi) /200 / common.GmumH # 1/keV
            dlnF_times_r200 = 2 - cluster.dFdc/cluster.fc * cluster.c # this product is adimensional
            dlnrhoH = (3 * Gprime_over_F * cluster.kTX + dlnF_times_r200)
            dlnrhoH *= (g**2 * 3**(g+1))**(1/(1-g))
            dlnrhoH /= Hz
            DfE = (- 1/(2+3*xi)) * dlnrhoH /TVR
            DfE = DfE[abs(DfE) < 0.05]
            der_combo_chains.append(DfE)
            der_parnames.append('DfE_EVR_%s' % cl)
        """

    if 'darkSU2' in model:
        Omega_phiplus = np.concatenate([F[burnin:, parnames.index('Omega_Gamma')]/F[burnin:, parnames.index('Gamma')] for F in f])
        der_combo_chains.append(Omega_phiplus)
        der_parnames.append('Omega_phiplus')

        Omega_phi0 = get_Omega_flat(f, burnin, parnames)
        der_combo_chains.append(Omega_phi0)
        der_parnames.append('Omega_phi0')

        Omega_d = Omega_phiplus + Omega_phi0
        der_combo_chains.append(Omega_d)
        der_parnames.append('Omega_d')

    return der_parnames, der_combo_chains




