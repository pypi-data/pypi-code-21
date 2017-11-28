def get_Omega_flat(bf, parnames):
    return 1 - sum([
        bf[parnames.index(Omega)]/(bf[parnames.index('Gamma')] if Omega == 'Omega_Gamma' else 1) if Omega in parnames else 0 \
                for Omega in ('Omega_Gamma', 'Omega_psi',
                    'Omega_c', 'Omega_nu', 'Omega_baryons',
                    'Omega_radiation')])

def derived_astar_wstar(bf, parnames, model):
    # applies to fv2 and fv3 models
    # fv2:
    tau, at, w0, wp = (bf[parnames.index(par)] for par in ('tau', 'at', 'w0', 'wp'))
    if model == 'fastvarying2':
        astar = (tau/(tau + 1))**tau * at
        wstar = wp + ( (w0-wp) * tau**tau * (tau+1)**(-tau-1) * at )/(1 - at**(-1/tau))
    elif model == 'fastvarying3':
        astar = at / 2**tau
        wstar = wp + 1/4 * (w0-wp) * at**(1/tau) / (1 - at**(-1/tau))
    else:
        raise AssertionError
    return astar, wstar

def derived_EVR_from_xi(bf, parnames):
    xi = bf[parnames.index('xi')]
    EVR = -(1-6*xi)/(2+3*xi)
    return EVR

def build_derived_bestfit(bf, parnames, model):
    der_bf = []

    if 'fastvarying' in model or model == 'lcdm':
        h2 = bf[parnames.index('h')]**2 
        Oc0, Ob0, Or0 = [bf[parnames.index(par)]/h2 if par in parnames \
                else None for par in ['Och2', 'Obh2', 'Orh2']]
        O0s = [O0 for O0 in (Oc0, Ob0, Or0) if O0 is not None]
        Od0 = 1 - sum(O0s)
        O0s.append(Od0)
        for O0 in O0s:
            der_bf.append(O0)

        if 'Deltaw' in parnames:
            par = 'w0' if model == 'fastvarying3' else 'wf' #fastvarying2
            wp = bf[parnames.index(par)] + bf[parnames.index('Deltaw')]
            der_bf.append(wp)

        if model in ('fastvarying2', 'fastvarying3'):
            astar, wstar = derived_astar_wstar(bf, parnames, model)
            der_bf.append(astar)
            der_bf.append(wstar)

    if 'LIclusters' in model:
        h2 = bf[parnames.index('h')]**2 
        Oc0 = bf[parnames.index('Och2')]/h2
        Od0 = 1 - Oc0
        EVR = derived_EVR_from_xi(bf, parnames)
        for par in (Oc0, Od0, EVR):
            der_bf.append(par)
        """
        #acceptable: 16
        for i in range(16):
            der_bf.append(0)
        """

    if 'darkSU2' in model:
        Omega_phiplus = bf[parnames.index('Omega_Gamma')]/bf[parnames.index('Gamma')]
        der_bf.append(Omega_phiplus)

        Omega_phi0 = get_Omega_flat(bf, parnames)
        der_bf.append(Omega_phi0)

        Omega_d = Omega_phiplus + Omega_phi0
        der_bf.append(Omega_d)


    return der_bf




