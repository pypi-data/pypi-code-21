__author__ = 'anna'


import modelbase.algebraicModule as am
import modelbase.parameters as param

import scipy
import numpy as np
import scipy.optimize as opt
from scipy.optimize import fsolve



class MinimalCalvinEQM(am.AlgebraicModule):

    defaultPars = {'nu01': -1.82, #DHAP
                   #'KT': 1/4.5e-2,  # FIXME: should, in last consequence, also be calculated from a 'nu' (transformed Gibbs energy of formation)
                   #'kp': 0.6,  # see above -- and this appears to be wrong!! should be around 1.66 (3/5->5/3 ??)
                   
                   # calculate d1, d2 from the nu's
                   #'d1': 6.48e-6,
                   ##'d2': 7.39e-5, this seems wrong. New calculation
                   #'d2': 3.43e-6,
                   #'f0': 23.22,
                   #'f2': 2.26,

                   

                   'nu2': -1.46, # X5P
                   'nu21': -1.76, # R5P
                   'nu22': -1.22, # Ru5P

                   'nu3': -2.93, # F6P
                   'nu4': -3.31, # S7P


                   'nuFBP': -7.07, # 2 * mu_0 - mu_FBP
                   'nuSBP': -7.45, # mu_0 + mu_1 - mu_SBP

                   'R': 1.987e-3,  # universal gas constant [kcal/mol K]
                   'T': 298.,    # Standard temp. conditions [K = 25C]

                   'compoundNames': ['GAP', 'E4P', 'X5P', 'DHAP', 'R5P', 'F6P', 'S7P', 'Ru5P', 'FBP', 'SBP']
    }

    def __init__(self, par={}):

        pars = MinimalCalvinEQM.defaultPars
        pars.update(par)
        pars.update({'RT': pars['R'] * pars['T']})

        compositePars = {'k2': np.exp(-(pars['nu2'] / pars['RT'])),
                         'k3': np.exp(-(pars['nu3'] / pars['RT'])),
                         'k4': np.exp(-(pars['nu4'] / pars['RT'])),
                         'd1': np.exp(pars['nuFBP'] / pars['RT']),
                         'd2': np.exp(pars['nuSBP'] / pars['RT']),
                         'KT': np.exp(-pars['nu01'] / pars['RT']),
                         'kp': np.exp(-(pars['nu21']-pars['nu2'])/pars['RT']),
                         'kp2': np.exp(-(pars['nu22']-pars['nu2'])/pars['RT'])
        }

        compositePars['f0'] = 1 + compositePars['KT']
        compositePars['f2'] = 1 + compositePars['kp'] + compositePars['kp2']

        pars.update(compositePars)

        super(MinimalCalvinEQM,self).__init__(pars)


    def solve_x0(self, z, P1, P2, Q):

        par = self.par

        gamma = 2.*par.k3*z / (1. + par.k3*z)

        p = par.d1/2. * (par.f0 + (gamma+2)/gamma * par.f2 * par.k2 * z + (gamma+4)/gamma * par.k4 * z**2)
        q = par.d1/2. * ((gamma+1)/gamma * P2 - P1 - Q/gamma)

        x0 = -p/2. + np.sqrt(p**2/4. - q)

        return x0

    def solve_x1(self, x0, z, P1, P2):

        par = self.par

        x1 = (2./par.d1 * x0**2 + x0 * (par.f0 + par.f2 * par.k2 * z + par.k4 * z**2) + P2 - P1) / \
             (1. + par.k3*z)

        return x1

    def solve_z(self, z, P1, P2, Q):

        par = self.par

        zz = self.solve_x1(self.solve_x0(z, P1, P2, Q), z, P1, P2)*(1 + par.k3*z) + \
             self.solve_x0(z, P1, P2, Q) * self.solve_x1(self.solve_x0(z, P1, P2, Q), z, P1, P2) / par.d2 - P2

        return zz

    def solve(self, P1, P2, Q):
        try:
            z = scipy.optimize.brentq(self.solve_z, .0001, 1000, args=(P1, P2, Q))
        except(ValueError):
            print("Did not find a solution for P1=%f, P2=%f, Q=%f" % (P1,P2,Q))
            raise

        return z


    def solve_eq(self, y):
        ''' returns z, x0, x1 '''
        p1=y[0]
        p2=y[1]
        q=y[2]

        z = self.solve(p1,p2,q)
        x0 = self.solve_x0(z,p1,p2,q)
        x1 = self.solve_x1(x0,z,p1,p2)

        return [z,x0,x1]


    def get_all(self, P1, P2, Q):

        par = self.par

        z = self.solve(P1, P2, Q)
        # x
        GAP = self.solve_x0(z, P1, P2, Q)
        E4P = self.solve_x1(GAP, z, P1, P2)
        X5P = GAP * par.k2 * z
        # y
        DHAP = par.KT * GAP
        R5P = par.kp * X5P
        F6P = par.k3 * E4P * z
        S7P = par.k4 * GAP * z**2
        # z
        Ru5P = par.f2 * par.k2 * GAP * z - (X5P + R5P)
        # p
        FBP = GAP**2 / par.d1
        SBP = GAP * E4P / par.d2

        return [GAP, E4P, X5P, DHAP, R5P, F6P, S7P, Ru5P, FBP, SBP]


    def getConcentrations(self, y):
        '''
        input: vector of conserved quantities y=(P1,P2,Q)
        output: vector of intermediate concentrations [GAP, E4P, X5P, DHAP, R5P, F6P, S7P, Ru5P, FBP, SBP]
        '''

        if len(y.shape) == 1:
            return self.get_all(y[0],y[1],y[2])

        else:
            return np.array([self.get_all(y[i,0],y[i,1],y[i,2]) for i in range(y.shape[0])])




    # routines to test alternative calculation method#

    def linz(self, x0, y0):
        
        [P1, P2, Q] = y0
        par = self.par

        denom = 2 * x0 * par.k2 * par.f2

        a = (6 * x0 / par.d2 + 2) / denom
        b = (4 * P1 + 3 * P2 - Q - 4 * x0 * par.f0 - 8 * (x0**2) / par.d1) / denom

        return a,b

    def _x1explicit(self, x0, y0):

        [P1, P2, Q] = y0
        par = self.par

        (a,b) = self.linz(x0,y0)
        denom = a * par.k3
        p = - (1 + b * par.k3 + x0 / par.d2) / denom
        q = P2 / denom
        rp = -p/2 + np.sqrt((p**2)/4 - q)
        rm = -p/2 - np.sqrt((p**2)/4 - q)

        return rp,rm,p,q

    def x1explicit(self, x0, y0, possgn = True):
        (rp, rn, p, q) = self._x1explicit(x0,y0)
        if possgn:
            return rp
        else:
            return rn

    def radicand(self, x0, y0):
        (rp, rn, p, q) = self._x1explicit(x0,y0)
        return (p**2)/4 - q

    def findbounds(self, y0):

        def r(x):
            return self.radicand(x,y0)

        res1 = opt.minimize_scalar(r)

        def x1(x):
            return self.radicand(x,y0)

        res2 = opt.brentq(x1, 1e-12, res1.x)

        return res2

    def C3_C2(self, x0, y0, possgn = True):
        '''
        determining equation for x0 that needs to be solved numerically
        results from the two conservation equations for Q (C3) and P2 (C2)
        possgn says which sign of the root to take to calculate E4P (x1) from GAP (x0)
        '''
        par = self.par
        x1 = self.x1explicit(x0,y0, possgn)
        (a,b) = self.linz(x0,y0)
        z = b - a * x1
        return x0 * (2 * par.f2 * par.k2 * z + 4 * par.k4 * (z**2)) + 2 * x1 * par.k3 * z - y0[2] + y0[1]
        
    def C3_C2n(self, x0, y0):
        '''
        obsolete: took negative sign of root. Now the same as calling C3_C2 with possgn = False
        '''
        par = self.par
        (rp, rn, p, q) = self._x1explicit(x0,y0)
        x1 = rn
        (a,b) = self.linz(x0,y0)
        z = b - a * x1
        return x0 * (2 * par.f2 * par.k2 * z + 4 * par.k4 * (z**2)) + 2 * x1 * par.k3 * z - y0[2] + y0[1]




    def getx0(self, y0):

        par = self.par

        ub = self.findbounds(y0)-1e-12
        lb = 1e-12

        # check for different signs of the determining equation (C3)-(C2) first
        # then chose wether to take the positive or negative root
        # ATTENTION: this is purely heuristic. Whether the situation exists in which both roots would result in a positive x0 is currently unclear

        sgn = True

        if (np.sign(self.C3_C2(lb,y0)) == np.sign(self.C3_C2(ub,y0))):
            #def f(x):
                #return self.C3_C2n(x,y0)

            #x0 = opt.brentq(f, 1e-12, ub, xtol=1e-16)
            sgn = False

        #else:
            #def f(x):
                #return self.C3_C2(x,y0)

            #x0 = opt.brentq(f, 1e-12, ub, xtol=1e-16)

        def f(x):
            return self.C3_C2(x,y0,sgn)

        x0 = opt.brentq(f, 1e-12, ub, xtol=1e-16)

        return x0, sgn


    def getall2(self, y0):

        par = self.par

        (GAP,possgn) = self.getx0(y0)
        E4P = self.x1explicit(GAP,y0,possgn)
        (a,b) = self.linz(GAP,y0)
        z = b - a * E4P
        
        X5P = GAP * par.k2 * z
        # y
        DHAP = par.KT * GAP
        R5P = par.kp * X5P
        F6P = par.k3 * E4P * z
        S7P = par.k4 * GAP * z**2
        # z
        Ru5P = par.f2 * par.k2 * GAP * z - (X5P + R5P)
        # p
        FBP = GAP**2 / par.d1
        SBP = GAP * E4P / par.d2

        return np.array([GAP, E4P, X5P, DHAP, R5P, F6P, S7P, Ru5P, FBP, SBP])
    
    # ----------------------------------------------------- #


    def conservedQuantities(self, conc):
        """
        input: all concentrations [GAP, E4P, X5P, DHAP, R5P, F6P, S7P, Ru5P, FBP, SBP]
        output: vector with conserved quantities y0 = [P1,P2,Q]
        """

        [GAP, E4P, X5P, DHAP, R5P, F6P, S7P, Ru5P, FBP, SBP] = conc
        P1 = GAP + DHAP + X5P + R5P + Ru5P + S7P + 2 * FBP + SBP
        P2 = E4P + F6P + SBP
        Q = E4P + 2 * (X5P + R5P + Ru5P) + 3 * F6P + 4 * S7P + SBP

        y0 = np.array([P1,P2,Q])

        return y0


    def massActionRatios(self, conc):
        """ 
        input: all concentrations [GAP, E4P, X5P, DHAP, R5P, F6P, S7P, Ru5P, FBP, SBP]
        e.g. Chlamy data from Tabea: [.02,.02,.04,.48,.06,.49,1.37,.02,.30,.56]/1000.
        output: the mass-action ratios for all reactions in the equilibrium module
        """

        [GAP, E4P, X5P, DHAP, R5P, F6P, S7P, Ru5P, FBP, SBP] = conc
        
        par = self.par

        gamma = {'TPI': (DHAP/GAP)/par.KT,
                 'RPE': (Ru5P/X5P)/par.kp2,
                 'RPI': (Ru5P/R5P)/np.exp(-(par.nu22-par.nu21)/par.RT),
                 'TK2': (E4P*X5P/(GAP*F6P))/np.exp(-(par.nu2-par.nu3)/par.RT),
                 'TK1': (R5P*X5P/(GAP*S7P))/np.exp(-(par.nu2+par.nu21-par.nu4)/par.RT),
                 'Ald1': (FBP/(GAP*DHAP))/np.exp(-(par.nuFBP-par.nu01)/par.RT),
                 'Ald2': (SBP/(E4P*DHAP))/np.exp(-(par.nuSBP-par.nu01)/par.RT)
             }

        return gamma

    def deltaG(self,conc):
        '''
        returns the actual Delta-G's from observed concentrations
        '''
        gamma = self.massActionRatios(conc)
        par=self.par
        return {k:par.RT*np.log(v) for k,v in gamma.items()}



    def massActionRatiosSimpleInverse(self, conc):
        """ 
        input: all concentrations [GAP, E4P, X5P, DHAP, R5P, F6P, S7P, Ru5P, FBP, SBP]
        e.g. Chlamy data from Tabea: [.02,.02,.04,.48,.06,.49,1.37,.02,.30,.56]/1000.
        output: the mass-action ratios for all reactions in the equilibrium module
        
        NOTE: this is the first primitive implementation. If values > 0, then Delta-G<0 (opposite to massActionRatios!)
        """

        [GAP, E4P, X5P, DHAP, R5P, F6P, S7P, Ru5P, FBP, SBP] = conc
        
        y0 = self.conservedQuantities(conc)

        [GAPeq, E4Peq, X5Peq, DHAPeq, R5Peq, F6Peq, S7Peq, Ru5Peq, FBPeq, SBPeq] = self.getConcentrations(y0)

        gamma = {'TPI': (DHAPeq/GAPeq)/(DHAP/GAP),
                 'PPI': (R5Peq/X5Peq)/(R5P/X5P),
                 'PPE': (Ru5Peq/R5Peq)/(Ru5P/R5P),
                 'TK1': (E4Peq*X5Peq/(GAPeq*F6Peq))/(E4P*X5P/(GAP*F6P)),
                 'TK2': (R5Peq*X5Peq/(GAPeq*S7Peq))/(R5P*X5P/(GAP*S7P)),
                 'Ald1': (FBPeq/(GAPeq*DHAPeq))/(FBP/(GAP*DHAP)),
                 'Ald2': (SBPeq/(E4Peq*DHAPeq))/(SBP/(E4P*DHAP))
             }

        return gamma


class MinimalPPPEQM(MinimalCalvinEQM):

    def __init__(self, par={}):

        super(MinimalPPPEQM,self).__init__(par)
        self.par.update(
            {'g0':1./self.par.d1,
             'g1':1./self.par.d2,
             'f1':1.,
             'f3':1.,
             'f4':1.,
             'f5':0.,
             'k0':1.,
             'k1':1.,
             'k5':1.
         }
        )
        self.par.update({'f':np.array([getattr(self.par,'f'+str(i)) for i in range(6)])})
        self.par.update({'kappa':np.array([getattr(self.par,'k'+str(i)) for i in range(6)])})
        

    def x0_z_Q(self, z, Q):

        par = self.par

        
        psiprime = np.array([(j+1)*par.f[j+1]*par.kappa[j+1]*(z**j) for j in range(4)]).sum()
        p2 = psiprime/(2*par.g1)

        x0 = -p2+np.sqrt(p2**2+Q/(par.g1*z))
        return x0

    def get_z(self, P, Q):

        def z1dim(z):
            x0 = self.x0_z_Q(z,Q)
            phi = np.array([self.par.f[j]*self.par.kappa[j]*(z**j) for j in range(5)]).sum()
            return x0*phi+2*(x0**2)*(self.par.g0+self.par.g1*z) - P

        z = opt.brentq(z1dim,1e-10,1e10)

        return z


    def get_all(self, P, Q):

        par = self.par

        z = self.get_z(P,Q)

        GAP = self.x0_z_Q(z, Q)
        DHAP = par.KT * GAP

        E4P = GAP * z

        X5P = par.k2 * GAP * z**2
        R5P = par.kp * X5P
        Ru5P = par.kp2 * X5P

        F6P = par.k3 * GAP * z**3
        S7P = par.k4 * GAP * z**4

        FBP = GAP**2 * par.g0
        SBP = GAP * E4P * par.g1

        return [GAP, E4P, X5P, DHAP, R5P, F6P, S7P, Ru5P, FBP, SBP]


    def getConcentrations(self, y):
        '''
        input: vector of conserved quantities y=(P,Q)
        output: vector of intermediate concentrations [GAP, E4P, X5P, DHAP, R5P, F6P, S7P, Ru5P, FBP, SBP]
        '''

        if len(y.shape) == 1:
            return self.get_all(y[0],y[1])

        else:
            return np.array([self.get_all(y[i,0],y[i,1]) for i in range(y.shape[0])])



    def conservedQuantities(self, conc):
        """
        input: all concentrations [GAP, E4P, X5P, DHAP, R5P, F6P, S7P, Ru5P, FBP, SBP]
        output: vector with conserved quantities y0 = [P,Q]
        """
        y0 = super(MinimalPPPEQM,self).conservedQuantities(conc)
        return np.array([y0[0]+y0[1],y0[2]])


    def massActionRatios(self, conc):

        [GAP, E4P, X5P, DHAP, R5P, F6P, S7P, Ru5P, FBP, SBP] = conc
        par = self.par

        gamma = super(MinimalPPPEQM,self).massActionRatios(conc)
        gamma.update({'TA': (E4P*F6P/(GAP*S7P))/np.exp(-(par.nu3-par.nu4)/par.RT)})

        return gamma



class ExtendedPetterssonEQM(am.AlgebraicModule):

    """
    This class defines an equilibrium module as that used by Pettersson1988, but with one extension:
    Whereas in Pettersson1988 NADPH and NADP+ were held constant, they are dynamic variables here,
    and only their sum is conserved.

    Reference concentrations from Bassham1969 in mM:
    
    PGA: 1.40
    BPGA: not given, must be very small, have not yet found any in vivo concentration
    GAP: 0.64
    DHAP: 0.032
    
    E4P: 0.02

    X5P: 0.021
    R5P: 0.034
    Ru5P: 0.012 
    ----------- total pentoses: 0.067

    G6P: 0.73
    F6P: 0.53
    G1P: not given, but with K_eq from Colowick1942 should be around 0.042
    ----------- total hexoses: 1.302

    S7P: 0.248

    FBP: 0.097
    SBP: 0.114

    RuBP: 2.04

    from Pettersson1988:

    Pi: 1
    ATP: 0.375 (total 0.5 from Pettersson1998, ratio 1:3 in light from Bassham1969)
    ADP: 0.125
    NADPH: 0.21
    NADP: 0.29

    These values give the following steady-state values for the conserved moieties:
    P1 = 2.695
    P2 = 1.436
    Q = 5.166
    B1 = 1.525
    B2 = 2.4
    R = 1.21
    or y0 = np.array([2.695,1.436,5.166,1.525,2.4,1.21])/1000

    TODO: investigate the sign problem that was also discovered in the alternative calculation routine for the minimal EQM
    """


    defaultPars = {'nu01': -1.82, # DHAP
                   # chemical potentials are expressed as mu(xjk) = mu(x00) + j * delta-mu + nu(xjk)
                   # with delta-mu = mu(x10) - mu(x00).
                   # Here: x00 = GAP, x10 = E4P
                   # values from Bassham1969 except where otherwise stated

                   'nu20': -1.46, # X5P
                   'nu21': -1.76, # R5P
                   'nu22': -1.22, # Ru5P

                   'nu30': -3.43, # G6P
                   'nu31': -2.93, # F6P
                   'nu32': -1.74, # G1P - back-calculated from Colowick1942

                   'nu40': -3.31, # S7P

                   'nuFBP': -7.07, # 2 * mu_0 - mu_FBP
                   'nuSBP': -7.45, # mu_0 + mu_1 - mu_SBP

                   'Lambda0': 3.18e3, # K_eq for PGK: BPGA + ADP <=> PGA + ATP, see also Pettersson1988, and also based on Buecher1947
                   'Lambda1': 1.6e7*(10**(-7.9)), # K_eq for GAPDH: GAP + NADP+ + Pi <=> BPGA + NADPH + H+ for pH=7.9, see also Pettersson1988 (inverse!)

                   # conserved quantitites
                   # need to be defined in eq module, because otherwise they would have to be passed as variable.
                   # However, if they are constant in the whole model, they do not exist as variables.
                   # This is a bit illogic and may change in the future.
                   # For example: flag whether they should be considered constant

                   'Atot': 5e-4, # ADP + ATP, 0.5mM, Pettersson1988
                   'Ntot': 5e-4, # NADPH + NADP+, 0.5 mM, Pettersson1988 (there, NADPH = 0.21mM, NADP+ = 0.29mM fixed)

                   # other physical and environmental  constants

                   'R': 1.987e-3,  # universal gas constant [kcal/mol K]
                   'T': 298.,    # Standard temp. conditions [K = 25C]

                   'compoundNames': ['PGA', 'BPGA', 'GAP', 'DHAP', 
                                     'E4P',
                                     'X5P', 'R5P', 'Ru5P',
                                     'G6P', 'F6P', 'G1P', 
                                     'S7P', 
                                     'FBP', 
                                     'SBP',
                                     'ATP', 'ADP', 'Pi',
                                     'NADPH', 'NADP']
                   
    }

    def __init__(self, par={}):

        pars = ExtendedPetterssonEQM.defaultPars
        pars.update(par)

        super(ExtendedPetterssonEQM,self).__init__(pars)

        self.setCompositePars()


    def setCompositePars(self):
        par = self.par

        par.RT = par.R * par.T
    
        par.kappa20 = np.exp(-par.nu20/par.RT)
        par.kappa30 = np.exp(-par.nu30/par.RT)
        par.kappa40 = np.exp(-par.nu40/par.RT)

        par.k01 = np.exp(-par.nu01/par.RT)
        par.k21 = np.exp(-(par.nu21-par.nu20)/par.RT)
        par.k22 = np.exp(-(par.nu22-par.nu20)/par.RT)
        par.k31 = np.exp(-(par.nu31-par.nu30)/par.RT)
        par.k32 = np.exp(-(par.nu32-par.nu30)/par.RT)

        par.f0 = 1 + par.k01
        par.f1 = 1
        par.f2 = 1 + par.k21 + par.k22
        par.f3 = 1 + par.k31 + par.k32
        par.f4 = 1

        par.g0 = np.exp(-par.nuFBP/par.RT)
        par.g1 = np.exp(-par.nuSBP/par.RT)

        

    def r(self, xi0, B1):
        '''
        calculates PGA (xi1) from BPGA (xi0). Requires B1 ( = PGA + ADP)
        a reference value for B1 from Bassham1969: PGA = 1.4 mM, ADP = 0.125 mM => B1 = 1.525e-3 M
        '''
        par = self.par
        p = par.Atot - B1 + par.Lambda0 * xi0
        q = - par.Lambda0 * B1 * xi0
        xi1 = - (p/2) + np.sqrt((p**2)/4 - q)
        return xi1

    def s(self, xi0, B1, B2, R):
        '''
        calculates GAP (x0) from BPGA (xi0). 
        Requires B1 (= PGA + ADP), B2 (= PGA + BPGA + Pi) and R (= Pi + NADPH)
        a reference value for B1 from Bassham1969: PGA = 1.4 mM, ADP = 0.125 mM => B1 = 1.525e-3 M
        a reference value for B2 from Bassham1969: PGA = 1.4 mM, BPGA = ?? (close to zero), Pi = 1 mM => B2 = 2.4e-3 M
        a reference value for R from Bassham1969/Pettersson1988: Pi = 1 mM, NADPH = 0.21 => R = 1.21e-3 M
        '''
        par = self.par

        Pi = B2 - xi0 - self.r(xi0, B1)
        x0 = par.Lambda1 * xi0 * (R - Pi) / (Pi * (par.Ntot - R + Pi))
        return x0

    def linz(self, xi0, y0):
        '''
        calculates the parameters a, b, such that z = b - a * x1
        Lagrange parameter z is calculated from BPGA (xi0) and E4P (x1).
        Requires all conserved quantities in y0=[P1,P2,Q,B1,B2,R]
        '''
        [P1,P2,Q,B1,B2,R] = y0
        par = self.par

        x0 = self.s(xi0, B1, B2, R)

        denom = 2 * x0 * par.kappa20 * par.f2

        a = (6 * x0 * par.g1 + 2 * par.f1) / denom
        b = (4 * P1 + 3 * P2 - Q - 4 * (self.r(xi0,B1) + xi0 + x0 * par.f0 + 2 * par.g0 * x0**2)) / denom

        return a, b

    def _x1explicit(self, xi0, y0):
        '''
        calculates the concentration of x1 (E4P) from xi0 (BPGA)
        Requires all conserved quantities in y0=[P1,P2,Q,B1,B2,R]
        '''
        [P1,P2,Q,B1,B2,R] = y0
        par = self.par

        (a,b) = self.linz(xi0, y0)
        x0 = self.s(xi0, B1, B2, R)

        p = - (par.f1 + par.g1 * x0 + par.kappa30 * par.f3 * b) / (par.kappa30 * par.f3 * a)
        q = P2 / (par.kappa30 * par.f3 * a)

        x11 = - p/2 + np.sqrt( (p**2)/4 - q )
        x12 = - p/2 - np.sqrt( (p**2)/4 - q )

        return x11,x12,p,q

    def x1explicit(self, x0, y0):
        (rp, rn, p, q) = self._x1explicit(x0,y0)
        return rp

    def radicand(self, x0, y0):
        (rp, rn, p, q) = self._x1explicit(x0,y0)
        return (p**2)/4 - q


    def findbounds(self, y0):
        '''
        finds bounds for xi0 where system can be solved. 
        '''
        [P1,P2,Q,B1,B2,R] = y0
        eps = 1e-12

        # determine where s becomes positive
        N = self.par.Ntot
        ub11 = opt.brentq(lambda x: B2 - x - self.r(x,B1), 0, B2)
        ub12 = opt.brentq(lambda x: N - R + B2 - x - self.r(x,B1), 0, N - R + B2)
        ub1 = min(ub11,ub12) - eps

        # this should be generalised to allow for positive/negative combinations of conserved moieties
        # R-B2 and N-R+B2
        if R - B2 < 0:
            lb = opt.brentq(lambda x: R - B2 + x + self.r(x,B1), 0, B2 - R) + eps
        else:
            lb = eps

        # determine where b becomes negative
        def getb(x):
            (a,b) = self.linz(x,y0)
            return b

        ub2 = opt.brentq(getb, lb, ub1) - eps

        # now make sure the radicand is always positive
        if self.radicand(ub2,y0) < 0:
            ub = opt.brentq(lambda x: self.radicand(x,y0), lb, ub2) - eps
        else:
            ub = ub2

        # set this as upper bound
        return (lb, ub)

    

    def getxi0(self, y0):

        [P1,P2,Q,B1,B2,R] = y0
        par = self.par

        def f(xi0):
            x0 = self.s(xi0,B1,B2,R)
            x1 = self.x1explicit(xi0,y0)
            (a,b) = self.linz(xi0,y0)
            z = b - a * x1
            return x0 * (2 * par.f2 * par.kappa20 * z + 4 * par.f4 * par.kappa40 * (z**2)) + 2 * par.f3 * par.kappa30 * x1 * z - Q + P2

        (lb, ub) = self.findbounds(y0)

        return opt.brentq(f, lb, ub, xtol=1e-16)


    def getall(self, y0):

        [P1,P2,Q,B1,B2,R] = y0
        par = self.par

        BPGA = self.getxi0(y0) # xi0
        PGA = self.r(BPGA, B1) # xi1
        GAP = self.s(BPGA, B1, B2, R) # x00
        DHAP = par.k01 * GAP # x01

        E4P = self.x1explicit(BPGA,y0) # x10
        (a,b) = self.linz(BPGA,y0)
        z = b - a * E4P
        
        X5P = par.kappa20 * GAP * z
        R5P = par.k21 * X5P
        Ru5P = par.k22 * X5P

        G6P = par.kappa30 * E4P * z
        F6P = par.k31 * G6P
        G1P = par.k32 * G6P

        S7P = par.kappa40 * GAP * z**2

        FBP = par.g0 * GAP**2
        SBP = par.g1 * GAP * E4P

        ADP = B1 - PGA
        ATP = par.Atot - ADP
        Pi = B2 - PGA -BPGA

        NADPH = R - Pi
        NADP = par.Ntot - NADPH

        return np.array([PGA, BPGA, GAP, DHAP, 
                         E4P, 
                         X5P, R5P, Ru5P, 
                         G6P, F6P, G1P,
                         S7P, 
                         FBP, 
                         SBP,
                         ATP, ADP, Pi,
                         NADPH, NADP])




    def getConcentrations(self, y):
        '''
        input: vector of conserved quantitites y=[P1,P2,Q,B1,B2,R]
        output: vector of intermediate concentrations 
        [PGA,BPGA,GAP,DHAP,E4P,X5P,R5P,Ru5P,G6P,F6P,G1P,S7P,FBP,SBP,ATP,ADP,Pi,NADPH,NADP]
        '''

        if len(y.shape) == 1:
            return self.getall(y)

        else:
            return np.hstack([self.getall(y[i,:]) for i in range(y.shape[0])])


class PetterssonEQM(am.AlgebraicModule):

    """
    This class defines an equilibrium module as that used by Pettersson1988.

    or y0 = np.array([2.695,1.436,5.166,1.525,2.4])/1000
    """


    defaultPars = {'nu01': -1.82, # DHAP
                   # chemical potentials are expressed as mu(xjk) = mu(x00) + j * delta-mu + nu(xjk)
                   # with delta-mu = mu(x10) - mu(x00).
                   # Here: x00 = GAP, x10 = E4P
                   # values from Bassham1969 except where otherwise stated

                   'nu20': -1.46, # X5P
                   'nu21': -1.76, # R5P
                   'nu22': -1.22, # Ru5P

                   'nu30': -3.43, # G6P
                   'nu31': -2.93, # F6P
                   'nu32': -1.74, # G1P - back-calculated from Colowick1942

                   'nu40': -3.31, # S7P

                   'nuFBP': -7.07, # 2 * mu_0 - mu_FBP
                   'nuSBP': -7.45, # mu_0 + mu_1 - mu_SBP

                   'Lambda0': 3.18e3, # K_eq for PGK: BPGA + ADP <=> PGA + ATP, see also Pettersson1988, and also based on Buecher1947
                   'Lambda1': 1.6e7*(10**(-7.9))*2.1/2.9, # K_eq for GAPDH: BPGA + NADPH + H+ <=> GAP + NADP+ + Pi for pH=7.9, NADPH = .21 mM, NADP+ = .29 mM, see also Pettersson1988

                   # conserved quantitites
                   # need to be defined in eq module, because otherwise they would have to be passed as variable.
                   # However, if they are constant in the whole model, they do not exist as variables.
                   # This is a bit illogic and may change in the future.
                   # For example: flag whether they should be considered constant

                   'Atot': 5e-4, # ADP + ATP, 0.5mM, Pettersson1988

                   # other physical and environmental  constants

                   'R': 1.987e-3,  # universal gas constant [kcal/mol K]
                   'T': 298.,    # Standard temp. conditions [T = 25C]

                   'compoundNames': ['PGA', 'BPGA', 'GAP', 'DHAP', 
                                     'E4P',
                                     'X5P', 'R5P', 'Ru5P',
                                     'G6P', 'F6P', 'G1P', 
                                     'S7P', 
                                     'FBP', 
                                     'SBP',
                                     'ATP', 'ADP', 'Pi']
                   
    }

    def __init__(self, par={}):

        pars = PetterssonEQM.defaultPars
        pars.update(par)

        super(PetterssonEQM,self).__init__(pars)

        self.setCompositePars()


    def setCompositePars(self):
        par = self.par

        par.RT = par.R * par.T
    
        par.kappa20 = np.exp(-par.nu20/par.RT)
        par.kappa30 = np.exp(-par.nu30/par.RT)
        par.kappa40 = np.exp(-par.nu40/par.RT)

        par.k01 = np.exp(-par.nu01/par.RT)
        par.k21 = np.exp(-(par.nu21-par.nu20)/par.RT)
        par.k22 = np.exp(-(par.nu22-par.nu20)/par.RT)
        par.k31 = np.exp(-(par.nu31-par.nu30)/par.RT)
        par.k32 = np.exp(-(par.nu32-par.nu30)/par.RT)

        par.f0 = 1 + par.k01
        par.f1 = 1
        par.f2 = 1 + par.k21 + par.k22
        par.f3 = 1 + par.k31 + par.k32
        par.f4 = 1

        par.g0 = np.exp(-par.nuFBP/par.RT)
        par.g1 = np.exp(-par.nuSBP/par.RT)

        

    def r(self, xi0, B1):
        '''
        calculates PGA (xi1) from BPGA (xi0). Requires B1 ( = PGA + ADP)
        a reference value for B1 from Bassham1969: PGA = 1.4 mM, ADP = 0.125 mM => B1 = 1.525e-3 M
        '''
        par = self.par
        p = par.Atot - B1 + par.Lambda0 * xi0
        q = - par.Lambda0 * B1 * xi0
        xi1 = - (p/2) + np.sqrt((p**2)/4 - q)
        return xi1

    def s(self, xi0, B1, B2):
        '''
        calculates GAP (x0) from BPGA (xi0). 
        Requires B1 (= PGA + ADP), B2 (= PGA + BPGA + Pi)
        a reference value for B1 from Bassham1969: PGA = 1.4 mM, ADP = 0.125 mM => B1 = 1.525e-3 M
        a reference value for B2 from Bassham1969: PGA = 1.4 mM, BPGA = ?? (close to zero), Pi = 1 mM => B2 = 2.4e-3 M
        '''
        par = self.par

        Pi = B2 - xi0 - self.r(xi0, B1)
        x0 = par.Lambda1 * xi0 / Pi
        return x0

    def linz(self, xi0, y0):
        '''
        calculates the parameters a, b, such that z = b - a * x1
        Lagrange parameter z is calculated from BPGA (xi0) and E4P (x1).
        Requires all conserved quantities in y0=[P1,P2,Q,B1,B2]
        '''
        [P1,P2,Q,B1,B2] = y0
        par = self.par

        x0 = self.s(xi0, B1, B2)

        denom = 2 * x0 * par.kappa20 * par.f2

        a = (6 * x0 * par.g1 + 2 * par.f1) / denom
        b = (4 * P1 + 3 * P2 - Q - 4 * (self.r(xi0,B1) + xi0 + x0 * par.f0 + 2 * par.g0 * x0**2)) / denom

        return a, b


    def getb(self, xi0, y0):
        (a,b) = self.linz(xi0,y0)
        return b


    def _x1explicit(self, xi0, y0):
        '''
        calculates quantities required for determining x1 from xi0. Needed to define valid intervals.
        '''
        [P1,P2,Q,B1,B2] = y0
        par = self.par

        (a,b) = self.linz(xi0, y0)
        x0 = self.s(xi0, B1, B2)

        p = - (par.f1 + par.g1 * x0 + par.kappa30 * par.f3 * b) / (par.kappa30 * par.f3 * a)
        q = P2 / (par.kappa30 * par.f3 * a)

        x11 = - p/2 + np.sqrt( (p**2)/4 - q )
        x12 = - p/2 - np.sqrt( (p**2)/4 - q )

        return x11,x12,p,q

    def x1explicit(self, x0, y0, possgn = True):
        '''
        calculates the concentration of x1 (E4P) from xi0 (BPGA)
        Requires all conserved quantities in y0=[P1,P2,Q,B1,B2]
        '''
        (rp, rn, p, q) = self._x1explicit(x0,y0)
        if possgn:
            return rp
        else:
            return rn


    def radicand(self, x0, y0):
        (rp, rn, p, q) = self._x1explicit(x0,y0)
        return (p**2)/4 - q



    def C3_C2(self, xi0, y0, possgn = True):
        '''
        this is the one-dimensional determining function for xi0 (BPGA), which results
        from subtracting the conservation equation of Q (C3) the conservation equation of P2 (C2).
        possgn indicates whether positive or negative root has to be taken to determine 
        y1 (E4P) from x0 (G3P) in method x1explicit.
        '''

        [P1,P2,Q,B1,B2] = y0
        par = self.par

        x0 = self.s(xi0,B1,B2)
        x1 = self.x1explicit(xi0,y0,possgn)
        (a,b) = self.linz(xi0,y0)
        z = b - a * x1

        return x0 * (2 * par.f2 * par.kappa20 * z + 4 * par.f4 * par.kappa40 * (z**2)) + 2 * par.f3 * par.kappa30 * x1 * z - Q + P2





    # Continue here... (and check linz)
    def findbounds(self, y0):
        '''
        finds bounds for xi0 where system can be solved. 
        '''
        [P1,P2,Q,B1,B2] = y0
        eps = 1e-12

        # determine where s becomes positive
        ub1 = opt.brentq(lambda x: B2 - x - self.r(x,B1), 0, B2) - eps

        lb = eps

        # determine where b becomes negative
        # FIXME: not clear whether there is always a sign change between 0 and ub1
        # FIXME: introduce check that B1-A < P1 (then all trioses except PGA zero, but formally no solution exists (b always negative))
        def getb(x):
            (a,b) = self.linz(x,y0)
            return b

        ub2 = opt.brentq(getb, lb, ub1) - eps

        # now make sure the radicand is always positive
        if self.radicand(ub2,y0) < 0:
            ub = opt.brentq(lambda x: self.radicand(x,y0), lb, ub2) - eps
        else:
            ub = ub2

        # set this as upper bound


        # verify wether C3_C2 has opposite signs at bounds
        possgn = True
        if np.sign(self.C3_C2(lb,y0)) == np.sign(self.C3_C2(ub,y0)):
            possgn = False
        
        return (lb, ub, possgn)
        # TODO: add check whether possgn or not

    

    def getxi0(self, y0):

        [P1,P2,Q,B1,B2] = y0
        par = self.par

        #def f(xi0):
            #x0 = self.s(xi0,B1,B2)
            #x1 = self.x1explicit(xi0,y0)
            #(a,b) = self.linz(xi0,y0)
            #z = b - a * x1
            #return x0 * (2 * par.f2 * par.kappa20 * z + 4 * par.f4 * par.kappa40 * (z**2)) + 2 * par.f3 * par.kappa30 * x1 * z - Q + P2

        try:
            (lb, ub, possgn) = self.findbounds(y0)
        except ValueError:
            #print "lb=",lb," ub=",ub," possgn=",possgn
            print("can't find bounds for y0=",y0)
            raise

        #(lb, ub, possgn) = self.findbounds(y0)

        if not possgn and np.sign(self.C3_C2(lb,y0,possgn)) == np.sign(self.C3_C2(ub,y0,possgn)):
            print("y0=", y0)
            return ub

        else:
            def f(xi0):
                return self.C3_C2(xi0,y0,possgn)

            return opt.brentq(f, lb, ub, xtol=1e-16)


    def getall(self, y0):

        [P1,P2,Q,B1,B2] = y0
        par = self.par

        BPGA = self.getxi0(y0) # xi0
        PGA = self.r(BPGA, B1) # xi1
        GAP = self.s(BPGA, B1, B2) # x00
        DHAP = par.k01 * GAP # x01

        E4P = self.x1explicit(BPGA,y0) # x10
        (a,b) = self.linz(BPGA,y0)
        z = b - a * E4P
        
        X5P = par.kappa20 * GAP * z
        R5P = par.k21 * X5P
        Ru5P = par.k22 * X5P

        G6P = par.kappa30 * E4P * z
        F6P = par.k31 * G6P
        G1P = par.k32 * G6P

        S7P = par.kappa40 * GAP * z**2

        FBP = par.g0 * GAP**2
        SBP = par.g1 * GAP * E4P

        ADP = B1 - PGA
        ATP = par.Atot - ADP
        Pi = B2 - PGA -BPGA

        return np.array([PGA, BPGA, GAP, DHAP, 
                         E4P, 
                         X5P, R5P, Ru5P, 
                         G6P, F6P, G1P,
                         S7P, 
                         FBP, 
                         SBP,
                         ATP, ADP, Pi])


    def conservedQuantities(self, c):
        '''
        input: vector with all concentrations [PGA,BPGA,GAP,DHAP,E4P,X5P,R5P,Ru5P,G6P,F6P,G1P,S7P,FBP,SBP,ATP,ADP,Pi]
        output: conserved quantities y0=[P1,P2,Q,B1,B2]
        also sets self.par.Atot to ATP+ADP

        example with simulated values from Pettersson1998:
        c = np.array([.59,.001,.01,.27,.04,.04,.06,.02,3.12,1.36,.18,.22,.024,.13,.39,.11,8.1])/1000.
        y0 = self.conservedQuantities(c)
        example with values for Chlamy from Tabea:
        c=np.array([3.68,.002,.02,.48,.02,.04,.06,.02,.31,.49,.02,1.37,.30,.56,1.46,.59,10])/1000.
        resulting in
        y0 = np.array([ 0.006832,  0.0014  ,  0.00876 ,  0.00514 ,  0.013682])
        ATTENTION: Here, Atot is modified accordingly...
        '''

        [PGA,BPGA,GAP,DHAP,E4P,X5P,R5P,Ru5P,G6P,F6P,G1P,S7P,FBP,SBP,ATP,ADP,Pi] = c
        P1 = PGA+BPGA+GAP+DHAP+X5P+R5P+Ru5P+S7P+2*FBP+SBP
        P2 = E4P+G6P+F6P+G1P+SBP
        Q = E4P+2*(X5P+R5P+Ru5P)+3*(G6P+F6P+G1P)+4*S7P+SBP
        B1 = PGA+ADP
        B2 = PGA+BPGA+Pi

        Atot = ATP + ADP
        self.par.Atot = Atot

        return np.array([P1,P2,Q,B1,B2])




    def getConcentrations(self, y):
        '''
        input: vector of conserved quantitites y=[P1,P2,Q,B1,B2]
        P1 = PGA + BPGA + DHAP + GAP + X5P + R5P + Ru5P + S7P + 2*FBP + SBP
        P2 = E4P + G6P + F6P + G1P + SBP
        Q = E4P + 2*(X5P + R5P + Ru5P) + 3*(G6P + F6P + G1P) + 4*S7P + SBP
        B1 = PGA + ADP
        B2 = PGA + BPGA + Pi

        reference values from Pettersson1998 (in mM, Table 4, calculated):
        C3 = PGA + BPGA + DHAP + GAP = 0.871, 
        C4 = E4P = 0.04,
        C5 = X5P + R5P + Ru5P = 0.12,
        C6 = G6P + F6P + G1P = 4.66,
        C7 = S7P = 0.22,
        FBP = 0.024,
        SBP = 0.13,
        ATP = 0.39 (ADP = 0.11)
        Pi = 8.1

        This gives:
        P1 = C3+C5+C7+2*FBP+SBP = 1.389e-3 M
        P2 = C4+C6+SBP = 4.83e-3 M
        Q = C4+2*C5+3*C6+4*C7+SBP = 15.27e-3 M
        B1 = 0.7e-3 M
        B2 = 8.691e-3 M

        y0 = np.array([1.389,4.83,15.27,0.7,8.691])/1000.

        output: vector of intermediate concentrations 
        [PGA,BPGA,GAP,DHAP,E4P,X5P,R5P,Ru5P,G6P,F6P,G1P,S7P,FBP,SBP,ATP,ADP,Pi]
        '''

        if len(y.shape) == 1:
            return self.getall(y)

        else:
            return np.vstack([self.getall(y[i,:]) for i in range(y.shape[0])])




    def massActionRatios(self, conc):
        """ 
        input: all concentrations [PGA,BPGA,GAP,DHAP,E4P,X5P,R5P,Ru5P,G6P,F6P,G1P,S7P,FBP,SBP,ATP,ADP,Pi]
        e.g. Chlamy data from Tabea: conc = np.array([.59,.001,.01,.27,.04,.04,.06,.02,3.12,1.36,.18,.22,.024,.13,.39,.11,8.1])/1000.
        output: the mass-action ratios for all reactions in the equilibrium module
        """
    
        [PGA,BPGA,GAP,DHAP,E4P,X5P,R5P,Ru5P,G6P,F6P,G1P,S7P,FBP,SBP,ATP,ADP,Pi] = conc

        par = self.par

        gamma = {'PGK': par.Lambda0/(PGA*ATP/(BPGA*ADP)), # forward: PGA+ATP->BPGA+ADP
                 'GAPDH': (GAP*Pi/BPGA)/par.Lambda1,
                 'TPI': (DHAP/GAP)/par.k01,
                 'PPE': (Ru5P/X5P)/par.k22,
                 'RPI': (Ru5P/R5P)/np.exp(-(par.nu22-par.nu21)/par.RT),
                 'TK1': (E4P*X5P/(GAP*F6P))/np.exp(-(par.nu20-par.nu30)/par.RT),
                 'TK2': (R5P*X5P/(GAP*S7P))/np.exp(-(par.nu20+par.nu21-par.nu40)/par.RT),
                 'Ald1': (FBP/(GAP*DHAP))/np.exp(-(par.nuFBP-par.nu01)/par.RT),
                 'Ald2': (SBP/(E4P*DHAP))/np.exp(-(par.nuSBP-par.nu01)/par.RT),
                 'HPI': par.k31/(F6P/G6P), # forward: F6P->G6P
                 'PGM': (G1P/G6P)/par.k32
             }

        return gamma

    def deltaG(self,conc):
        '''
        returns the actual Delta-G's from observed concentrations
        '''
        gamma = self.massActionRatios(conc)
        par=self.par
        return [(k,par.RT*np.log(v)) for k,v in gamma.items()]

