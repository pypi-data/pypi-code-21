__author__ = 'oliver'

'''
This file will become the main repository for models of the Calvin-Benson-Bassham Cycle.
TODO: Move all models developed so far to this file.
Shall include:
- minimal models with and without equilibrium module
- the model by Pettersson 1988
- models on carbon label distributions
'''


import modelbase
import modelbase.ratelaws as rl
import modelbase.algebraicModule as algModule

import calvinmodel.equilibriumModule as eqmodule

import numpy as np
import numpy.linalg as LA

import scipy.optimize as opt

import pickle


####### definition of regularly used reference values ##############################


eqm = eqmodule.MinimalCalvinEQM()
RT = eqm.par.RT

nuA = np.array([0.,0.,eqm.par.nu21])
nuK = np.array([eqm.par.nu2, eqm.par.nu3, eqm.par.nu4])
dG = np.repeat(nuA.reshape(3,1),3,1)+np.repeat(nuK.reshape(1,3),3,0)
Q = np.exp(-(dG-dG.transpose())/eqm.par.RT)
kTK = np.sqrt(Q)

# equilibrium concentrations after Bassham1969
eqConcBassham = {'GAP': 2.52e-5, # all concentration in M
                 'E4P': 2.00e-5,
                 'R5P': 8.66e-5,
                 'X5P': 5.22e-5,
                 'F6P': 4.97e-4,
                 'S7P': 2.09e-4,
                 'DHAP': 5.45e-4,
                 'Ru5P': 3.58e-5,
                 'FBP': 9.76e-5,
                 'SBP': 1.47e-4
}

expConcBassham = {'GAP': 3.2e-5, # all concentration in M
                  'E4P': 2.00e-5,
                  'R5P': 3.4e-5,
                  'X5P': 2.1e-5,
                  'F6P': 5.3e-4,
                  'S7P': 2.48e-4,
                  'DHAP': 6.4e-4,
                  'Ru5P': 1.2e-5,
                  'FBP': 9.7e-5,
                  'SBP': 1.14e-4
}


nu0 = {'GAP': 0.,
       'E4P': 0.,
       'R5P': eqm.par.nu21,
       'X5P': eqm.par.nu2,
       'F6P': eqm.par.nu3,
       'S7P': eqm.par.nu4,
       'DHAP': eqm.par.nu01,
       'Ru5P': eqm.par.nu22,
       'FBP': eqm.par.nuFBP,
       'SBP': eqm.par.nuSBP
}


# kinetic parameters for the reactions in the equilibrium module
# (when modelled without rapid equilibrium approximation)
defaultEqmReactionPars = {'fTK': 1000.,
                          'kf_TK1': 1000.,
                          'Keq_TK1': np.exp(-(eqm.par.nu21+eqm.par.nu2-eqm.par.nu4)/RT), # GAP+S7P=X5P+R5P
                          'kf_TK2': 1000.,
                          'Keq_TK2': np.exp(-(eqm.par.nu2-eqm.par.nu3)/RT), # GAP+F6P=E4P+X5P
                          'kf_TPI': 1.,
                          'Keq_TPI': np.exp(-eqm.par.nu01/RT),
                          'kf_RPE': 1.,
                          'Keq_RPE': np.exp(-(eqm.par.nu22-eqm.par.nu2)/RT),
                          'kf_RPI': 1.,
                          'Keq_RPI': np.exp(-(eqm.par.nu22-eqm.par.nu21)/RT),
                          'kf_Ald1': 2000.,
                          'Keq_Ald1': np.exp(-(eqm.par.nuFBP-eqm.par.nu01)/RT),
                          'kf_Ald2': 2000.,
                          'Keq_Ald2': np.exp(-(eqm.par.nuSBP-eqm.par.nu01)/RT)
}


# example parameter sets resulting from method minimalEQMModelMM.optimizeStability()
optimizedMMkineticPars1 = {'KM1': 0.0001649103296236226,
                           'KM2': 7.6574625040419167e-08,
                           'KM3': 2.1006176281255491e-05,
                           'KM4': 2.9768341465869432e-05,
                           'KM5': 10467.482559675052,
                           'Vmax1': 4.1642175845100293e-05,
                           'Vmax2': 1.16080077933606e-05,
                           'Vmax3': 5.5812092094761904e-05,
                           'Vmax4': 8.4326890397565498e-06,
                           'Vmax5': 81.489385947337482
}

optimizedMMkineticPars2 = {'KM1': 0.0018519126370239842,
                           'KM2': 7.7468340492472102e-06,
                           'KM3': 4.0769753558336325e-05,
                           'KM4': 0.00047911888003253123,
                           'KM5': 0.009438552117785411,
                           'Vmax1': 0.00030938591834199687,
                           'Vmax2': 1.221260203982704e-05,
                           'Vmax3': 7.5575669371842738e-05,
                           'Vmax4': 7.73464795857063e-05,
                           'Vmax5': 7.734647958555378e-05
}

irreversibleReactions = {'FBP': 'FBP', 
                         'SBP': 'SBP', 
                         'RuBisCO': 'Ru5P',
                         'TPTGAP': 'GAP',
                         'TPTDHAP': 'DHAP',
                         'vstarch': 'F6P'
}

vanillaPars = {}
for r in irreversibleReactions:
    vanillaPars['KM_'+r] = 1.
    vanillaPars['Vmax_'+r] = 1.




######## methods not belonging to classes #########################################

class CBBModel(object):

    @staticmethod
    def mmParameters(y0, v0, e0):
        '''
        calculates KM and Vmax from given steady-state solution (y0), rates (v0) and normalized(!) elasticities e0.
        Substrates and Fluxes must have the same order, i.e. i-th substrate is substrate for i-th reaction
        :param y0: stationary concentrations of substrates
        :param v0: stationary fluxes
        :param e0: normalized elasticities
        :returns: Vmax, KM
        '''

        KM = y0*(e0/(1-e0))
        Vm = v0/(1-e0)

        return Vm, KM


    @staticmethod
    def reverseEngineerMMParameters(y0, v0, e0):
        """
        calculates the parameters KM1...KM5 and Vmax1...Vmax5 from a given steady-state solution
        (y0), steady-state rates (v0) and pre-defined elasticities (e0). 
        :param y0: steady-state concentrations (substrates of reactions in v0)
        :param v0: steady-state rates
        :param e0: elasticities
        :return: Vmax, KM
        """
        
        KM = v0/(v0/y0-e0)-y0
        Vmax = v0*(KM+y0)/y0
        
        return Vmax, KM

    @staticmethod
    def reverseEngineerInhibitionConstants(y0, I0, v0, eX, eI):
        
        KM = v0/(v0/y0-eX)-y0
        KI = -v0/eI-I0
        Vmax = v0*(KM+y0)*(1+I0/KI)/y0
        
        return Vmax, KM, KI

    @staticmethod
    def normalizeMatrix(M,vnumer,vdenom):
        '''
        returns a 'normalized' matrix. E.g. 
        normalizeMatrix(N,v0,y0) normalizes stoichiometry matrix: v_j^0/y_i^0*n_ij -> n_ij^*
        normalizeMatrix(TH,y0,x0) normalizes equilibrium/elasticities: y_k^0/x_l^0*th_lk -> th_lk^*
        '''
        fnorm = (1./vdenom)[np.newaxis].T * vnumer[np.newaxis]
        return(np.multiply(M,fnorm))

    @staticmethod
    def standardCBBFluxByPartition(alpha,beta,scale=1.,TK3=False):
        '''
        calculated CBB flux distribution
        :param beta: fraction of carbon exported as starch
        :param alpha: fraction of trioses (1-beta) exported through TPTGAP
        :param scale: optional, scales all fluxes by this factor
        :param TK3: optional, if set adds a third TK reaction (E4P+S7P=R5P+F6P). Value is 0..1 proportion of vTK1. TK fluxes are adjusted as (vTK1, vTK2, 0) -> ((1-TK3)*vTK1, vTK2+TK3*vTK1, TK3*vTK1)
        :return: dict with fluxes. Keys are standard 13 reactions (7 reversible, among these two standard TKs; 6 irreversible). Normalized so that v_RuBisCO=scale (defaults to 1)
        '''

        v = {}
        v['TPI'] = 6. - 2.*alpha + (2.*alpha-1.) * beta
        v['RPE'] = 4.
        v['RPI'] = 2.
        v['TK1'] = 2.
        v['TK2'] = 2.
        v['Ald1'] = 2. + beta
        v['Ald2'] = 2.
        v['RuBisCO'] = 6.
        v['TPTGAP'] = (2. - 2.*beta) * alpha
        v['TPTDHAP'] = (2. - 2.*beta) * (1. - alpha)
        v['vstarch'] = beta
        v['FBP'] = 2. + beta
        v['SBP'] = 2.

        if TK3 is not False:
            v['TK3'] = TK3 * v['TK1']
            v['TK2'] = v['TK2'] + TK3 * v['TK1']
            v['TK1'] = (1 - TK3) * v['TK1']

        for r in v.keys():
            v[r] = (v[r]/6.)*scale

        return v



####### DEFINITION OF MODEL CLASSES ###############################################


class CBBODEModel(CBBModel, modelbase.Model):
    '''
    A super class for CBB Models based on ODEs (no algebraic equilibrium modules)
    '''

    def add_isomerase(self, kf='kf_TPI', eq='Keq_TPI', cnames=['GAP','DHAP'], rname='TPI'):
        self.add_cpds(cnames)

        viso = rl.reversibleMassActionUniUni(kf,eq)
        self.set_rate(rname, viso, *cnames)
        self.set_stoichiometry(rname, {cnames[0]:-1, cnames[1]:1})

    def add_aldolase(self, kf='kf_Ald1', eq='Keq_Ald1', cnames=['DHAP','GAP','FBP'], rname='Ald1'):
        self.add_cpds(cnames)

        vald = rl.reversibleMassActionBiUni(kf,eq)
        self.set_rate(rname, vald, *cnames)
        self.set_stoichiometry(rname, {cnames[0]:-1, cnames[1]:-1, cnames[2]:1})

    def add_allTK(self, f='fTK', k='kTK', ketoses=['X5P','F6P','S7P'], aldoses=['GAP','E4P','R5P'], rnamebase='TK'):
        def make_TK_rate_function(i,j):
            def _rateFunction(p,x,y):
                return rl.massAction(getattr(p,f)*getattr(p,k)[i,j],x,y)
            return _rateFunction

        for i in range(3):
            for j in range(3):
                if i != j:
                    rateFunction = make_TK_rate_function(i,j)
                    ketosub = ketoses[i]
                    aldosub = aldoses[j]
                    ketoprod = ketoses[j]
                    aldoprod = aldoses[i]
                    rateName = rnamebase+'_'+ketosub+'_'+aldosub
                    self.set_rate(rateName, rateFunction, ketosub, aldosub)
                    self.set_stoichiometry(rateName,{ketosub:-1,aldosub:-1,ketoprod:1,aldoprod:1})

    add_uniuni = add_isomerase
    add_biuni = add_aldolase

    def add_bibi(self, kf='kf_PGK', eq='Keq_PGK', cnames=['PGA','ATP','BPGA','ADP'], rname='PGK'):
        self.add_cpds(cnames)

        vbibi = rl.reversibleMassActionBiBi(kf,eq)
        self.set_rate(rname, vbibi, *cnames)
        self.set_stoichiometry(rname, {cnames[0]:-1, cnames[1]:-1, cnames[2]:1, cnames[3]:1})

    def add_unibi(self, kf='kf_uni', eq='Keq_GAPDH', cnames=['BPGA','PGA','Pi'], rname='GAPDH'):
        self.add_cpds(cnames)

        vbibi = rl.reversibleMassActionUniBi(kf,eq)
        self.set_rate(rname, vbibi, *cnames)
        self.set_stoichiometry(rname, {cnames[0]:-1, cnames[1]:1, cnames[2]:1})



#class MinimalCBBModel2(CBBODEModel):
        
 

class ExplicitEQMCBB(modelbase.Model,CBBModel):
    '''
    Super class of the explicit simple models. 
    Contains method to accelerate / decelerate slow / fast reactions
    '''
    
    def modifyFastSlowRatio(self,eqf,noneqf):
        
        pardict = self.par.__dict__
        modKinPars = {}
        for k in pardict.keys():
            if k.startswith('kf_') or k == 'fTK':
                modKinPars[k] = pardict[k] * eqf
            elif k.startswith('Vmax'):
                modKinPars[k] = pardict[k] * noneqf

        self.par.update(modKinPars)



 
# A small CBB model with EQM reactions explicitly modelled.
# 5 additional reactions to complete cycle
class MinimalCBBModel(ExplicitEQMCBB):
    '''
    Class to define a minimal model in which the equilibrium reactions are explicitly modelled
    '''

    defaultPars = defaultEqmReactionPars.copy()
    #defaultPars.update(optimizedMMkineticPars2)
    defaultPars.update(vanillaPars)
    #defaultPars.update({'Vmax6': defaultPars['Vmax4'], 'KM6': defaultPars['KM4']})
    defaultPars.update({'kTK': kTK})

    def __init__(self, pars = {}, eqFactor = 1., noneqFactor = 1., TKsimple = False, TPT = 0):
        '''
        constructor of minimal CBB model with fast reactions explicitly modelled
        :pars: parameters overriding the default
        :eqFactor: factor to multiply close-to-equilibrium reactions with
        :noneqFactor: factor to multiply non-equilibrium reactions with
        :TKsimple: if True, only the two 'standard' TK reactions will be included
        :TPT: switch which TPT export to use. 0: GAP, 1: DHAP, 2: both
        NOTE: pars will be modified if eqFactor and/or noneqFactor are set!
        '''

        defPars = MinimalCBBModel.defaultPars.copy()
        #modKinPars = {}
        #for k in defPars.keys():
        #    if k.startswith('kf_') or k == 'fTK':
        #        modKinPars[k] = defPars[k] * eqFactor
        #    elif k.startswith('Vmax'):
        #        modKinPars[k] = defPars[k] * noneqFactor
        #
        #defPars.update(modKinPars)

        super(MinimalCBBModel, self).__init__(pars, defPars)

        self.modifyFastSlowRatio(eqFactor,noneqFactor)

        #pardict = self.par.__dict__
        #modKinPars = {}
        #for k in pardict.keys():
        #    if k.startswith('kf_') or k == 'fTK':
        #        modKinPars[k] = pardict[k] * eqFactor
        #    elif k.startswith('Vmax'):
        #        modKinPars[k] = pardict[k] * noneqFactor
        #
        #self.par.update(modKinPars)

        # add all compounds
        self.add_cpds(eqConcBassham.keys())

        # add equilibrium module reactions as mass-action

        # TPI: GAP <-> DHAP
        def vTPI(p,y,z):
            return p.kf_TPI*(y-z/p.Keq_TPI)
        self.set_rate('TPI', vTPI, 'GAP', 'DHAP')
        self.set_stoichiometry('TPI',{'GAP':-1,'DHAP':1})

        # Aldolase1 DHAP+GAP <-> FBP
        def vAld1(p,x,y,z):
            return p.kf_Ald1*(x*y-z/p.Keq_Ald1)
        self.set_rate('Ald1', vAld1, 'DHAP', 'GAP', 'FBP')
        self.set_stoichiometry('Ald1', {'DHAP':-1,'GAP':-1,'FBP':1})

        # Aldolase2 DHAP+E4P <-> SBP
        def vAld2(p,x,y,z):
            return p.kf_Ald2*(x*y-z/p.Keq_Ald2)
        self.set_rate('Ald2', vAld2, 'DHAP', 'E4P', 'SBP')
        self.set_stoichiometry('Ald2', {'DHAP':-1,'E4P':-1,'SBP':1})

        # Ribulose Phosphate Epimerase (RPE) X5P <-> Ru5P
        def vRPE(p,y,z):
            return p.kf_RPE*(y-z/p.Keq_RPE)
        self.set_rate('RPE', vRPE, 'X5P', 'Ru5P')
        self.set_stoichiometry('RPE',{'X5P':-1,'Ru5P':1})

        # Ribose Phosphate Ismerase (RPI) R5P <-> Ru5P
        def vRPI(p,y,z):
            return p.kf_RPI*(y-z/p.Keq_RPI)
        self.set_rate('RPI', vRPI, 'R5P', 'Ru5P')
        self.set_stoichiometry('RPI',{'R5P':-1,'Ru5P':1})

        if TKsimple:
            def vTK1(p,a,b,c,d):
                return p.kf_TK1*(a*b-c*d/p.Keq_TK1)
            self.set_rate('TK1', vTK1, 'GAP', 'S7P', 'X5P', 'R5P')
            self.set_stoichiometry('TK1', {'GAP':-1,'S7P':-1,'X5P':1,'R5P':1})

            def vTK2(p,a,b,c,d):
                return p.kf_TK2*(a*b-c*d/p.Keq_TK2)
            self.set_rate('TK2', vTK2, 'GAP', 'F6P', 'X5P', 'E4P')
            self.set_stoichiometry('TK2', {'GAP':-1,'F6P':-1,'X5P':1,'E4P':1})

        else:
            # Transketolase (TK) reactions
            #ketoseList=['X5P','F6P','S7P']
            #aldoseList=['GAP','E4P','R5P']
            #def make_TK_rate_function(i,j):
            #    def _rateFunction(p,x,y):
            #        return rl.massAction(p.fTK*p.kTK[i,j],x,y)
            #    return _rateFunction
            #
            #for i in range(3):
            #    for j in range(3):
            #        if i != j:
            #            rateFunction = make_TK_rate_function(i,j)
            #            ketosub = ketoseList[i]
            #            aldosub = aldoseList[j]
            #            ketoprod = ketoseList[j]
            #            aldoprod = aldoseList[i]
            #            rateName = 'TK_'+ketosub+'_'+aldosub
            #            self.set_rate(rateName, rateFunction, ketosub, aldosub)
            ketoseList=['X5P','F6P','S7P']
            aldoseList=['GAP','E4P','R5P']
            def make_TK_rate_function(i,j):
                def _rateFunction(p,a,b,c,d):
                    return p.fTK*(p.kTK[i,j]*a*b-p.kTK[j,i]*c*d)
                return _rateFunction

            for i in range(3):
                for j in range(3):
                    if i > j:
                        rateFunction = make_TK_rate_function(i,j)
                        ketosub = ketoseList[i]
                        aldosub = aldoseList[j]
                        ketoprod = ketoseList[j]
                        aldoprod = aldoseList[i]
                        rateName = 'TK_'+ketosub+'_'+aldosub
                        self.set_rate(rateName, rateFunction, ketosub, aldosub, ketoprod, aldoprod)
                        self.set_stoichiometry(rateName,{ketosub:-1,aldosub:-1,ketoprod:1,aldoprod:1})


        # irreversible reactions

        def makeIrrMM(r):
            Vmaxstr = 'Vmax_'+r
            KMstr = 'KM_'+r

            def v(p,y):
                return rl.MM1(getattr(p,Vmaxstr), getattr(p,KMstr), y)

            return v

        irr = irreversibleReactions.copy()
        if TPT == 0:
            irr.pop('TPTDHAP')
        elif TPT == 1:
            irr.pop('TPTGAP')
        
        for r in irreversibleReactions.keys():
            virr = makeIrrMM(r)
            
            self.set_rate(r, virr, irreversibleReactions[r])

        self.set_stoichiometry('FBP',{'FBP':-1,'F6P':1})

        self.set_stoichiometry('SBP',{'SBP':-1,'S7P':1})

        self.set_stoichiometry('RuBisCO',{'Ru5P':-1,'GAP':2})

        if 'TPTGAP' in irr:
            self.set_stoichiometry('TPTGAP',{'GAP':-1})

        if 'TPTDHAP' in irr:
            self.set_stoichiometry('TPTDHAP',{'DHAP':-1})

        self.set_stoichiometry('vstarch',{'F6P':-1})

        ## v1: Fructose Bisphosphatase (FBP): FBP -> F6P
        #def v1(p,y):
        #    return rl.MM1(p.Vmax1, p.KM1, y)
        #self.set_rate('FBP', v1, 'FBP')
        #self.set_stoichiometry('FBP',{'FBP':-1,'F6P':1})
        #
        ## v1: Sedoheptulose Bisphosphatase (SBP): SBP -> S6P
        #def v2(p,y):
        #    return rl.MM1(p.Vmax2, p.KM2, y)
        #self.set_rate('SBP', v2, 'SBP')
        #self.set_stoichiometry('SBP',{'SBP':-1,'S7P':1})
        #
        ## v3: Phosphoribulokinase (PRK) + RuBisCo: Ru5P + CO2 -> 2 GAP
        #def v3(p,y): 
        #    return rl.MM1(p.Vmax3, p.KM3, y)
        #self.set_rate('RuBisCO', v3, 'Ru5P')
        #self.set_stoichiometry('RuBisCO',{'Ru5P':-1,'GAP':2})
        #
        ## v4: Triosephosphate Translocator for GAP
        #def v4(p,y):
        #    return rl.MM1(p.Vmax4, p.KM4, y)
        #self.set_rate('TPT', v4, 'GAP')
        #self.set_stoichiometry('TPT',{'GAP':-1})
        #
        ## v5: Export of F6P to starch
        #def v5(p,y):
        #    return rl.MM1(p.Vmax5, p.KM5, y)
        #self.set_rate('vstarch', v5, 'F6P')
        #self.set_stoichiometry('vstarch',{'F6P':-1})
        #
        ## v6: Triosephosphate Transolcator for DHAP
        #if TPT > 1:
        #    def v6(p,y):
        #        return rl.MM1(p.Vmax6, p.KM6, y)
        #    self.set_rate('TPT2', v6, 'DHAP')
        #    self.set_stoichiometry('TPT2',{'DHAP':-1})
            




    def fastKsFromDisequilibrium(self, v0, expc, R, fastReactions = False):
        '''
        calculates forward rate constants for fast reactions based on target flux v0 and given experimental concentrations expc
        :param v0: dict with target fluxes with keys for the seven fast reactions 'Ald1','Ald2','PPE','RPI','TK1','TK2','TPI'
        :param expc: dict with experimental concentrations. Keys are concentrations
        :param R: dict with disequilibrium ratios (as returned from eqm.massActionRatios())
        :param fastReactions: optional list of reaction names. If False, keys of R are used
        :return: dict with key:value reaction_name:kf
        '''

        kf = {}

        if fastReactions == False:
            fastReactions = R.keys()

        for r in fastReactions:
            # TODO: throw error properly
            if r not in self.rateFn:
                print("Model does not have reaction {:s}".format(r))
                raise ModelConstructionError("Reaction {:s} missing".format(r))
            if r not in v0:
                print("Rates v0 does not have reaction {:s}".format(r))
                raise ModelConstructionError("Rate {:s} missing".format(r))

            s = self.stoichiometries[r]
            cprod = 1.
            for k in s.keys():
                if s[k] < 0:
                    cprod = cprod * expc[k]
            kfkey = 'kf_'+r
            kf[kfkey] = v0[r]/cprod/(1-R[r])

        return kf


    def setFastElasticitiesFromDisequilibrium(self, expc, R, fastReactions = False):
        '''
        returns an elasticity matrix of full size (n x r) with zeros except for the fast reactions.
        These are set to 1/(1-Gamma/Keq) for substrates, 1/(1-Keq/Gamma) for products
        :param expc: dict with experimental concentrations. Keys are concentrations
        :param R: dict with disequilibrium ratios (as returned from eqm.massActionRatios())
        :param fastReactions: optional list of reaction names. If False, keys of R are used
        :return: np.array H
        '''

        rids = {v:k for k,v in enumerate(self.rateNames())}
        cids = self.cpdIds()

        # create elasticity matrix
        H = np.zeros([len(self.rateNames()),len(self.cpdNames)])


        for r in fastReactions:
            # TODO: throw error properly
            if r not in self.rateFn:
                print("Model does not have reaction {:s}".format(r))
                raise ModelConstructionError("Reaction {:s} missing".format(r))
 
            s = self.stoichiometries[r]
            for k in s.keys():
                if s[k] < 0:
                    H[rids[r],cids[k]] = 1./(1-R[r])
                else:
                    H[rids[r],cids[k]] = 1./(1-1./R[r])

        return H


    def makeDomEigFunc(self, v0, expc):
        '''
        returns a function that maps elasticities of irreversible reactions to dominant eigenvalue of Jacobian
        :param v0: dict with target fluxes with keys for the irreversible reactions 'SBP','FBP','vstarch','RuBisCO','TPTGAP', and/or 'TPTDHAP'
        :param expc: dict with experimental concentrations. Keys are compound names, values are concentrations
        :return: function, dict irrRea->substrate
        '''
        rids = {v:k for k,v in enumerate(self.rateNames())}
        cids = self.cpdIds()

        #irrReactions = ['SBP','FBP','vstarch','RuBisCO','TPT','TPT2']
        irids = {}
        subids = {}
        for r in irreversibleReactions:
            if r in rids:
                irids[r] = rids[r]
                s = self.stoichiometries[r]
                for k in s.keys():
                    if s[k] < 0:
                        subids[r] = cids[k]
        xarray = np.array(list(irids.values()))
        yarray = np.array(list(subids.values()))

        H = self.setFastElasticities(expc)

        x0 = np.array([expc[self.cpdNames[i]] for i in range(len(self.cpdNames))])
        v0vec = np.zeros(len(v0.keys()))
        v0vec[list(rids.values())] = np.array([v0[r] for r in rids.keys()])
        #print(["v0vec=",v0vec])
        #print(["x0=",x0])

        Nnorm = self.normalizeMatrix(self.stoichiometryMatrix(),v0vec,x0)

        #print(["Nnorm = ", Nnorm])
        #print(["H = ",H])

        def domEigval(eps):
            '''
            must be called with eps as vector of elasticites OF THE CORRECT LENGTH!
            '''
            thisH = H.copy()
            thisH[(xarray,yarray)] = eps
            (l,ev) = np.linalg.eig(Nnorm*thisH)
            return l.real.max()

        return domEigval, subids


    def stabilize(self, v0, expc, method='SLSQP'):
        '''
        attempts to find parameters such that steady-state concentrations are expc, steady-state rates are v0, and all is stable
        :param v0: dict with rates
        :param expc: dict with concentrations
        '''
        
        # first set fast parameters
        self.par.update(self.fastKsFromExp(v0,expc))

        # now find optimal elasticities
        domeig, sid = self.makeDomEigFunc(v0,expc)
        b = np.array([[0.05,0.95] for x in range(len(sid.keys()))])

        res = opt.minimize(lambda x: domeig(x), 
                           b[:,1]/2, 
                           method='SLSQP', 
                           bounds=b, 
                           options={'maxiter':100000})

        vir = np.array([v0[r] for r in sid.keys()])
        xir = np.array([expc[s] for s in irreversibleReactions.values()])

        Vmax, KM = self.mmParameters(xir,vir,res.x)

        # set corresponding parameters
        irrrea = list(sid.keys())
        for i in range(len(irrrea)):
            Vmaxstr = 'Vmax_'+irrrea[i]
            KMstr = 'KM_'+irrrea[i]
            self.par.update({Vmaxstr:Vmax[i],KMstr:KM[i]})


        return res
        




    def optimizeStability(self, y0, method='SLSQP'):
        '''
        returns elasticities leading to small largest eigenvalue
        :input y0: a steady state
        :return: 5 elasticities for 'FBP', 'SBP', 'RuBisCO', 'TPT', 'vstarch'
        '''

        E = self.allElasticities(y0)
        N = self.stoichiometryMatrix()

        varVars = ['FBP', 'SBP', 'Ru5P', 'GAP', 'F6P']
        varRates = ['FBP', 'SBP', 'RuBisCO', 'TPT', 'vstarch']
        allRateIds = {v:k for k,v in enumerate(self.rateNames())}
        varRateIds = [allRateIds[k] for k in varRates]
        Evar = E[varRateIds,:].copy()
        posEvarId = np.where(np.logical_not(np.isclose(Evar,0)))

        # define boundaries
        varVarIds = self.get_argids(*varVars)
        v = np.array([self.rates(y0)[k] for k in self.rateNames()])
        maxe = v[varRateIds] / y0[varVarIds]
        b = np.array([[0.05*x,0.95*x] for x in maxe])
        
        def stability(x):
            Eopt = Evar.copy()
            Eopt[posEvarId] = x
            E2 = E.copy()
            E2[varRateIds,:] = Eopt
            l,v = np.linalg.eig(N*E2)
            return l.real.max()

        res = opt.minimize(lambda x: stability(x), 
                           b[:,1]/2, 
                           method=method, 
                           bounds=b, 
                           options={'maxiter':100000})

        if res.success != True:
            print("Warning: minimization did not return success", res)

        Vmax, KM = self.reverseEngineerMMParameters(y0[varVarIds],v[varRateIds],res.x)

        newpar = {}
        for i in range(len(Vmax)):
            newpar['Vmax'+str(i+1)] = Vmax[i]
            newpar['KM'+str(i+1)] = KM[i]

        self.par.update(newpar)

        return res.x


    def addAllostericInhibition(self, rateName, Vmax, KI, k_Vmax, k_KM, k_KI, substrateName, inhibitorName):
        '''
        :input rateName: name of rate to be changed
        :input Vmax: new Vmax
        :input KI: inhibition constant
        :input k_Vmax: par key of Vmax
        :input k_KM: par key of KM
        :input k_KI: par key of KI
        :input substrateName: name of substrate
        :input inhibitorName: name of inhibitor
        '''

        ratefn = rl.irrMMnoncompInh(k_Vmax,k_KM,k_KI)
        self.par.update({k_Vmax:Vmax, k_KI:KI})
        self.set_rate(rateName, ratefn, substrateName, inhibitorName)


class SimpleTKCBBModel(MinimalCBBModel):

    '''
    Class to define special case of exactly two TK reactions and both TPT transporters.
    Needed only for functionality of 'store' and 'load' functions.
    '''
    
    def __init__(self, pars = {}):
        super(SimpleTKCBBModel, self).__init__(pars, TKsimple = True, TPT = 2)


    def fastKsFromExp(self, v0, expc):
        '''
        calculates forward rate constants for fast reactions based on target flux v0 and given experimental concentrations expc
        :param v0: dict with target fluxes with keys for the seven fast reactions 'Ald1','Ald2','PPE','RPI','TK1','TK2','TPI'
        :param expc: dict with experimental concentrations. Keys are concentrations
        :return: dict with key:value reaction_name:kf
        '''

        # determine mass-action ratios
        R = eqm.massActionRatios([expc[c] for c in eqm.par.compoundNames])

        #fastReactions = ['Ald1','Ald2','RPE','RPI','TK1','TK2','TPI']
        fastReactions = R.keys()

        return self.fastKsFromDisequilibrium(v0, expc, R, fastReactions)



    def setFastElasticities(self, expc):
        '''
        returns an elasticity matrix of full size (n x r) with zeros except for the fast reactions.
        These are set to 1/(1-Gamma/Keq) for substrates, 1/(1-Keq/Gamma) for products
        :param expc: dict with experimental concentrations. Keys are concentrations
        :return: np.array H
        '''
        
        # determine mass-action ratios
        R = eqm.massActionRatios([expc[c] for c in eqm.par.compoundNames])

        #fastReactions = ['Ald1','Ald2','RPE','RPI','TK1','TK2','TPI']
        fastReactions = R.keys()

        return self.setFastElasticitiesFromDisequilibrium(expc, R, fastReactions)




    @classmethod
    def fit(cls, expc, alpha, beta, scale=1e-5):
        '''
        makes a model fitted to experimental concentrations expc (dict) with flux distribution given by alpha and beta
        :input expc: dict with experimental concentrations in M
        :input alpha: fraction of trioses exported as GAP
        :input beta: fraction of carbons exported as hexoses
        :input scale: optional parameter scaling the flux. Default: 1e-5, found to work.
        :returns: model with steady-state concentrations and fluxes fitted
        '''
        m = cls()
        vref = m.standardCBBFluxByPartition(alpha,beta,scale=1e-5)
        res = m.stabilize(vref, expc)
        if res.success != True:
            print("Warning: Optimization not successful!")
            print(res)
        elif res.fun >= 0:
            print("Warning: Optimization did not find stable stationary state!")
            print(res)
            
        return m




class FullTKCBBModel(MinimalCBBModel):

    '''
    Class to define special case of exactly two TK reactions and both TPT transporters.
    Needed only for functionality of 'store' and 'load' functions.
    '''

    TKmap = {'TK1':'TK_S7P_GAP',
             'TK2':'TK_F6P_GAP',
             'TK3':'TK_S7P_E4P'}

    
    def __init__(self, pars = {}):
        super(FullTKCBBModel, self).__init__(pars, TKsimple = False, TPT = 2)


    def standardCBBFluxByPartition(self, alpha, beta, scale=1., TK3=0.):
        v = super(FullTKCBBModel, self).standardCBBFluxByPartition(alpha, beta, scale=scale, TK3=TK3)
        self.fixTK(v)
        return v

    @staticmethod
    def fixTK(d):
        '''
        changes keys for dict d: TK1 -> TK_S7P_GAP, TK2 -> TK_F6P_GAP, TK3 -> TK_S7P_E4P
        :param d: dict that is modified
        '''

        for k,v in FullTKCBBModel.TKmap.items():
            d[v] = d.pop(k)



    def fastKsFromExp(self, v0, expc):
        '''
        calculates forward rate constants for fast reactions based on target flux v0 and given experimental concentrations expc
        :param v0: dict with target fluxes with keys for the seven fast reactions 'Ald1','Ald2','PPE','RPI','TK1','TK2','TPI'
        :param expc: dict with experimental concentrations. Keys are concentrations
        :return: dict with key:value reaction_name:kf
        '''

        # determine mass-action ratios
        R = eqm.massActionRatios([expc[c] for c in eqm.par.compoundNames])
        R['TK3'] = R['TK1']/R['TK2']

        vref = v0.copy()
        # correct notation for TK reactions
        self.fixTK(R)
        #self.fixTK(vref)

        #fastReactions = ['Ald1','Ald2','RPE','RPI','TK1','TK2','TPI']
        fastReactions = R.keys()

        kf = self.fastKsFromDisequilibrium(vref, expc, R, fastReactions)

        # set all TK rates
        kTK = np.zeros((3,3))

        kTK[1,0] = kf['kf_TK_F6P_GAP']
        kTK[0,1] = kf['kf_TK_F6P_GAP']/self.par.Keq_TK2
        kTK[2,0] = kf['kf_TK_S7P_GAP']
        kTK[0,2] = kf['kf_TK_S7P_GAP']/self.par.Keq_TK1
        kTK[2,1] = kf['kf_TK_S7P_E4P']
        kTK[1,2] = kf['kf_TK_S7P_E4P']/(self.par.Keq_TK1/self.par.Keq_TK2)

        kf['kTK'] = kTK
        kf['fTK'] = 1.

        return kf


    def setFastElasticities(self, expc):
        '''
        returns an elasticity matrix of full size (n x r) with zeros except for the fast reactions.
        These are set to 1/(1-Gamma/Keq) for substrates, 1/(1-Keq/Gamma) for products
        :param expc: dict with experimental concentrations. Keys are concentrations
        :return: np.array H
        '''
        
        # determine mass-action ratios
        R = eqm.massActionRatios([expc[c] for c in eqm.par.compoundNames])
        R['TK3'] = R['TK1']/R['TK2']
        self.fixTK(R)

        fastReactions = R.keys()

        return self.setFastElasticitiesFromDisequilibrium(expc, R, fastReactions)



    @classmethod
    def fit(cls, expc, alpha, beta, scale=1e-5, TK3=0., TK0=0.):
        '''
        makes a model fitted to experimental concentrations expc (dict) with flux distribution given by alpha and beta
        :input expc: dict with experimental concentrations in M
        :input alpha: fraction of trioses exported as GAP
        :input beta: fraction of carbons exported as hexoses
        :input scale: optional parameter scaling the flux. Default: 1e-5, found to work.
        :input TK3: sets rate of 'third' TK (E4P+S7P=R5P+F6P)
        :input TK0: sets 'neutral' TKs (proportion of avg of TK1 and TK2)
        :returns: model with steady-state concentrations and fluxes fitted
        '''
        m = cls()
        vref = m.standardCBBFluxByPartition(alpha,beta,scale=1e-5,TK3=TK3)
        res = m.stabilize(vref, expc)
        if res.success != True:
            print("Warning: Optimization not successful!")
            print(res)
        elif res.fun >= 0:
            print("Warning: Optimization did not find stable stationary state!")
            print(res)
       
        # now set 'neutral' TK reactions
        kTK = m.par.kTK
        kTK0ref = (np.sqrt(kTK[1,0]*kTK[0,1])+np.sqrt(kTK[2,0]*kTK[0,2]))/2.

        kTK[(range(3),range(3))] = TK0 * kTK0ref

        return m



    #def deltaGs(self, y0):
    #    '''
    #    :input y0: vector with concentrations
    #    '''
    #    dG = {}
    #    for r in self.rateNames():
            


# The same model but with label tracing ######################################

class LabelCBBModel(modelbase.LabelModel,ExplicitEQMCBB):

    defaultPars = defaultEqmReactionPars.copy()
    #defaultPars.update(optimizedMMkineticPars2)
    defaultPars.update(vanillaPars)
    defaultPars.update({'kTK': kTK})

    def __init__(self, pars = {}, eqFactor = 1., noneqFactor = 1., TKsimple = False, TPT = 0):

        defPars = MinimalCBBModel.defaultPars.copy()
        #modKinPars = {}
        #for k in defPars.keys():
        #    if k.startswith('kf_') or k == 'fTK':
        #        modKinPars[k] = defPars[k] * eqFactor
        #    elif k.startswith('Vmax'):
        #        modKinPars[k] = defPars[k] * noneqFactor
        #
        #defPars.update(modKinPars)

        super(LabelCBBModel, self).__init__(pars, defPars)

        self.modifyFastSlowRatio(eqFactor,noneqFactor)

        # add all compounds
        self.add_base_cpd('GAP', 3)
        self.add_base_cpd('DHAP', 3)
        self.add_base_cpd('E4P', 4)
        self.add_base_cpd('X5P', 5)
        self.add_base_cpd('R5P', 5)
        self.add_base_cpd('Ru5P', 5)
        self.add_base_cpd('F6P', 6)
        self.add_base_cpd('S7P', 7)
        self.add_base_cpd('FBP', 6)
        self.add_base_cpd('SBP', 7)

        # add equilibrium module reactions as mass-action

        # TPI:   GAP <-> DHAP
        def vTPIf(p,y):
            return rl.massAction(p.kf_TPI,y)

        self.add_carbonmap_reaction('TPIf',vTPIf,[2,1,0],['GAP'],['DHAP'],'GAP')

        def vTPIr(p,y):
            return rl.massAction(p.kf_TPI/p.Keq_TPI,y)

        self.add_carbonmap_reaction('TPIr',vTPIr,[2,1,0],['DHAP'],['GAP'],'DHAP')

        # Aldolase1 DHAP+GAP <-> FBP
        def vAld1f(p,y,z):
            return rl.massAction(p.kf_Ald1,y,z)

        self.add_carbonmap_reaction('Ald1f',vAld1f,[0,1,2,3,4,5],['DHAP','GAP'],['FBP'],'DHAP','GAP')

        def vAld1r(p,y):
            return rl.massAction(p.kf_Ald1/p.Keq_Ald1,y)

        self.add_carbonmap_reaction('Ald1r',vAld1r,[0,1,2,3,4,5],['FBP'],['DHAP','GAP'],'FBP')

        # Aldolase2 DHAP+E4P <-> SBP
        def vAld2f(p,y,z):
            return rl.massAction(p.kf_Ald2,y,z)

        self.add_carbonmap_reaction('Ald2f',vAld2f,[0,1,2,3,4,5,6],['DHAP','E4P'],['SBP'],'DHAP','E4P')

        def vAld2r(p,y):
            return rl.massAction(p.kf_Ald2/p.Keq_Ald2,y)

        self.add_carbonmap_reaction('Ald2r',vAld2r,[0,1,2,3,4,5,6],['SBP'],['DHAP','E4P'],'SBP')

        # Ribulose Phosphate Epimerase (RPE) X5P <-> Ru5P
        def vRPEf(p,y):
            return rl.massAction(p.kf_RPE,y)

        self.add_carbonmap_reaction('RPEf',vRPEf,[0,1,2,3,4],['X5P'],['Ru5P'],'X5P')

        def vRPEr(p,y):
            return rl.massAction(p.kf_RPE/p.Keq_RPE,y)

        self.add_carbonmap_reaction('RPEr',vRPEr,[0,1,2,3,4],['Ru5P'],['X5P'],'Ru5P')

        # Ribose Phosphate Ismerase (RPI) R5P <-> Ru5P
        def vRPIf(p,y):
            return rl.massAction(p.kf_RPI,y)

        self.add_carbonmap_reaction('RPIf',vRPIf,[0,1,2,3,4],['R5P'],['Ru5P'],'R5P')

        def vRPIr(p,y):
            return rl.massAction(p.kf_RPI/p.Keq_RPI,y)

        self.add_carbonmap_reaction('RPIr',vRPIr,[0,1,2,3,4],['Ru5P'],['R5P'],'Ru5P')

        if TKsimple:
            def vTK1f(p,x,y):
                return rl.massAction(p.kf_TK1,x,y)
            self.add_carbonmap_reaction('TK1f',vTK1f,[0,1,7,8,9,2,3,4,5,6],['S7P','GAP'],['X5P','R5P'],'S7P','GAP')

            def vTK1r(p,x,y):
                return rl.massAction(p.kf_TK1/p.Keq_TK1,x,y)
            self.add_carbonmap_reaction('TK1r',vTK1r,[0,1,5,6,7,8,9,2,3,4],['X5P','R5P'],['S7P','GAP'],'X5P','R5P')
            
            def vTK2f(p,x,y):
                return rl.massAction(p.kf_TK2,x,y)
            self.add_carbonmap_reaction('TK2f',vTK2f,[0,1,6,7,8,2,3,4,5],['F6P','GAP'],['X5P','E4P'],'F6P','GAP')

            def vTK2r(p,x,y):
                return rl.massAction(p.kf_TK2/p.Keq_TK2,x,y)
            self.add_carbonmap_reaction('TK2r',vTK2r,[0,1,5,6,7,8,2,3,4],['X5P','E4P'],['F6P','GAP'],'X5P','E4P')
            
        else:
            # Transketolase (TK) reactions
            ketoseList=['X5P','F6P','S7P']
            aldoseList=['GAP','E4P','R5P']
            def make_TK_rate_function(i,j):
                def _rateFunction(p,x,y):
                    return rl.massAction(p.fTK*p.kTK[i,j],x,y)
                return _rateFunction

            for i in range(3):
                for j in range(3):
                    rateFunction = make_TK_rate_function(i,j)
                    ketosub = ketoseList[i]
                    aldosub = aldoseList[j]
                    ketoprod = ketoseList[j]
                    aldoprod = aldoseList[i]
                    rateName = 'TK_'+ketosub+'_'+aldosub
                    carbonmap = [0,1]+range(i+5,i+j+8)+range(2,i+5)
                    self.add_carbonmap_reaction(rateName, rateFunction, carbonmap, [ketosub, aldosub], [ketoprod, aldoprod], ketosub, aldosub)



        # now add all additional (irreversible) reactions

        # v1: Fructose Bisphosphatase (FBP): FBP -> F6P
        def v1(p,y,ytot):
            #return p.Vmax1 * y / (p.KM1 + ytot)
            return p.Vmax_FBP * y / (p.KM_FBP + ytot)

        self.add_carbonmap_reaction('FBP',v1,[0,1,2,3,4,5],['FBP'],['F6P'],'FBP','FBP')

        # v2: Sedoheptulose Bisphosphatase (SBP): SBP -> S7P
        def v2(p,y,ytot):
            #return p.Vmax2 * y / (p.KM2 + ytot)
            return p.Vmax_SBP * y / (p.KM_SBP + ytot)

        self.add_carbonmap_reaction('SBP',v2,[0,1,2,3,4,5,6],['SBP'],['S7P'],'SBP','SBP')

        # v3: Phosphoribulokinase (PRK) + RuBisCo: Ru5P + CO2 -> 2 GAP
        def v3(p,y,ytot): 
            #return p.Vmax3 * y / (p.KM3 + ytot)
            return p.Vmax_RuBisCO * y / (p.KM_RuBisCO + ytot)

        self.add_carbonmap_reaction('RuBisCO',v3,[2,1,0,5,3,4],['Ru5P'],['GAP','GAP'],'Ru5P','Ru5P')

        if TPT != 1:
            # v4: Triosephosphate Translocator for GAP
            def v4(p,y,ytot):
                #return p.Vmax4 * y / (p.KM4 + ytot)
                return p.Vmax_TPTGAP * y / (p.KM_TPTGAP + ytot)

            self.add_carbonmap_reaction('TPTGAP',v4,[0,1,2],['GAP'],[],'GAP','GAP')

        if TPT != 0:
            # v4: Triosephosphate Translocator for DHAP
            def v4DHAP(p,y,ytot):
                return p.Vmax_TPTDHAP * y / (p.KM_TPTDHAP + ytot)

            self.add_carbonmap_reaction('TPTDHAP',v4DHAP,[0,1,2],['DHAP'],[],'DHAP','DHAP')

        # v5: Export of F6P to starch
        def v5(p,y,ytot):
            #return p.Vmax5 * y / (p.KM5 + ytot)
            return p.Vmax_vstarch * y / (p.KM_vstarch + ytot)

        self.add_carbonmap_reaction('vstarch',v5,[0,1,2,3,4,5],['F6P'],[],'F6P','F6P')



    def optimizeStability(self, y0, method='SLSQP'):
        '''
        creates non-labelled model, 
        finds steady state near y0 and 
        sets MM parameters to stabilize
        '''
        m = MinimalCBBModel(self.par.__dict__)
	
        y0m = np.array([y0[k] for k in m.cpdNames]) 
        ss = m.findSteadyState(y0m)
	
        e = m.optimizeStability(ss, method)
	
        newpar = {}
        for i in range(len(e)):
            newpar['Vmax'+str(i+1)] = getattr(m.par, 'Vmax'+str(i+1))
            newpar['KM'+str(i+1)] = getattr(m.par, 'KM'+str(i+1))
            
        self.par.update(newpar)
            
        return e


    def findUnlabelledSteadyState(self, y0=None):
        '''
        returns steady-state as full vectors with all compounds set to fully unlabelled
        :input y0 (optional): vector of concentrations as initial guess to find steady-state. If None, use the standard equilibrium concentrations from Bassham1969
        :output: full vector of initial concentrations
        '''
        m = MinimalCBBModel(self.par.__dict__)
        
        if y0 is None:
            y0 = np.array([eqConcBassham[k] for k in m.cpdNames])
        
        ss = m.findSteadyState(y0)

        ssd = {m.cpdNames[i]:ss[i] for i in range(len(m.cpdNames))}

        yinit = self.set_initconc_cpd_labelpos(ssd)

        return yinit


class LabelSimpleTKCBBModel(LabelCBBModel):

    '''
    Class to define special case of exactly two TK reactions and both TPT transporters.
    Needed only for functionality of 'store' and 'load' functions.
    '''
    
    def __init__(self, pars = {}):
        super(LabelSimpleTKCBBModel, self).__init__(pars, TKsimple = True, TPT = 2)

    @classmethod
    def fit(cls, expc, alpha, beta, scale=1e-5):
        '''
        makes a model fitted to experimental concentrations expc (dict) with flux distribution given by alpha and beta
        :input expc: dict with experimental concentrations in M
        :input alpha: fraction of trioses exported as GAP
        :input beta: fraction of carbons exported as hexoses
        :input scale: optional parameter scaling the flux. Default: 1e-5, found to work.
        :returns: model with steady-state concentrations and fluxes fitted
        '''
        m = SimpleTKCBBModel.fit(expc, alpha, beta, scale)
        ml = cls(pars=m.par.__dict__)
        return ml


class LabelFullTKCBBModel(LabelCBBModel):

    '''
    Class to define general case of nine TK reactions and both TPT transporters.
    Needed only for functionality of 'store' and 'load' functions.
    '''
    
    def __init__(self, pars = {}):
        super(LabelFullTKCBBModel, self).__init__(pars, TKsimple = False, TPT = 2)

    @classmethod
    def fit(cls, expc, alpha, beta, scale=1e-5, TK3=0., TK0=0.):
        '''
        makes a model fitted to experimental concentrations expc (dict) with flux distribution given by alpha and beta
        :input expc: dict with experimental concentrations in M
        :input alpha: fraction of trioses exported as GAP
        :input beta: fraction of carbons exported as hexoses
        :input scale: optional parameter scaling the flux. Default: 1e-5, found to work.
        :returns: model with steady-state concentrations and fluxes fitted
        '''
        m = FullTKCBBModel.fit(expc, alpha, beta, scale, TK3, TK0)
        ml = cls(pars=m.par.__dict__)
        return ml





# Implementations of the Pettersson1988 model and variants

class CBBPetterssonNoEQM(CBBODEModel,modelbase.AlgmModel):
    '''
    Class defining Pettersson's Model, but modelling the fast (near equilibrium) reactions explicitly
    '''

    rateConversionFactor = 9.26e-6 # converts microM/(h*mg Chl) into M/s
    # assumption: stromal volume of 30 microL/mg Chl (Poolman2000)
    #rateConversionFactor = 1.

    defaultPars = {'cP': 0.015, # total phosphates 15mM
                   'cA': 0.0005, # total adenosine phosphates (ADP+ATP) 0.5mM

                   # fixed concentrations are in M
                   'NADPH': 0.21e-3,
                   'NADP': 0.29e-3,

                   # original V's are in microM/(h*mg Chl)!!
                   'V1': 340. * rateConversionFactor, 
                   'V6': 200. * rateConversionFactor,
                   'V9': 40. * rateConversionFactor,
                   'V13': 1000. * rateConversionFactor,
                   'V16': 350. * rateConversionFactor,
                   'Vst': 40. * rateConversionFactor,
                   'Vex': 250. * rateConversionFactor,

                   # K's are in M
                   'Km1': 0.02e-3,
                   'Ki11': 0.84e-3,
                   'Ki12': 0.04e-3,
                   'Ki13': 0.075e-3,
                   'Ki14': 0.90e-3,
                   'Ki15': 0.07e-3,

                   'Km6': 0.03e-3,
                   'Ki61': 0.70e-3,
                   'Ki62': 12.0e-3,

                   'Km9': 0.013e-3,
                   'Ki9': 12.0e-3,

                   'Km131': 0.05e-3,
                   'Km132': 0.05e-3,
                   'Ki131': 2.0e-3,
                   'Ki132': 0.7e-3,
                   'Ki133': 4.0e-3,
                   'Ki134': 2.5e-3,
                   'Ki135': 0.4e-3,

                   'Km161': 0.014e-3,
                   'Km162': 0.3e-3,


                   'KPi': 0.63e-3,
                   'KPext': 0.74e-3,
                   'KPGA': 0.25e-3,
                   'KGAP': 0.075e-3,
                   'KDHAP': 0.077e-3,

                   'Kmst1': 0.08e-3,
                   'Kmst2': 0.08e-3,
                   'Kist': 10.0e-3,
                   # the activation constants are assumed to be dimensionless, because otherwise the units in Eq.(41) from Pettersson1998 do not match
                   'Kast1': 0.1,
                   'Kast2': 0.02,
                   'Kast3': 0.02,

                   'Pext': 1e-3

                   #'EQMult': 9e8

    }

    defaultPars.update(defaultEqmReactionPars)
    defaultPars.update({'kTK': kTK})

    defaultPars.update({'kf_uni': 2.0e4,
                        'kf_bi': 1.0e8,
                        'Keq_PGK': 3.1e-4,
                        'Keq_GAPDH': 1.6e7*(10**(-7.9))*defaultPars['NADPH']/defaultPars['NADP'],
                        'Keq_PGI': 2.3,
                        'Keq_PGM': 0.058 })


    cpdList = ['PGA', 'BPGA', 'GAP', 'DHAP', 
               'E4P',
               'X5P', 'R5P', 'Ru5P',
               'G6P', 'F6P', 'G1P', 
               'S7P', 
               'FBP', 
               'SBP',
               'ATP', 'Pi']


    eqConcPettersson = {'PGA': 5.9e-4, # all concentration in M
                        'BPGA': 1.0e-6,
                        'GAP': 1.0e-5,
                        'DHAP': 2.7e-4,
                        'FBP': 2.4e-5,
                        'F6P': 1.36e-3,
                        'G6P': 3.12e-3,
                        'G1P': 1.8e-4,
                        'SBP': 1.3e-4,
                        'S7P': 2.2e-4,
                        'E4P': 4.0e-5,
                        'X5P': 4.0e-5,
                        'R5P': 6.0e-5,
                        'Ru5P': 2.0e-5,
                        'ATP': 3.9e-4,
                        'Pi': 8.1e-3
    }


    def __init__(self, pars = {}):
        
        defPars = CBBPetterssonNoEQM.defaultPars.copy()
        super(CBBPetterssonNoEQM, self).__init__(pars, defPars)

        self.set_cpds(CBBPetterssonNoEQM.cpdList)

        # conserved quantity of adenosine phosphates to determine ADP
        def ap_conrel(par, y):
            return np.array([par.cA - y[0]])

        adp_cr = algModule.AlgebraicModule({'cA':self.par.cA}, ap_conrel)

        self.add_algebraicModule(adp_cr, ['ATP'], ['ADP'])

        # conserved quantity of phosphates to determine RuBP
        def rubp_conrel(par, y):
            (PGA, BPGA, GAP, DHAP, 
             E4P, X5P, R5P, Ru5P, G6P, F6P, G1P,
             S7P, FBP, SBP, ATP, Pi, ADP) = y

            RuBP = (par.cP - (Pi+PGA+2*BPGA+GAP+DHAP+2*FBP+F6P+E4P+2*SBP+S7P+X5P+R5P+Ru5P+G6P+G1P+ATP))/2
            return np.array([RuBP])

        rubp_cr = algModule.AlgebraicModule({'cP':self.par.cP}, rubp_conrel)

        self.add_algebraicModule(rubp_cr, CBBPetterssonNoEQM.cpdList+['ADP'], ['RuBP'])

        # the common denominator for all TPTs
        def tptN(par, y):
            (Pi, PGA, GAP, DHAP) = y
            P = np.array([Pi, PGA, GAP, DHAP])
            KP = np.array([par.KPi, par.KPGA, par.KGAP, par.KDHAP])
            N = 1 + (1 + par.KPext/par.Pext) * (P/KP).sum()

            return np.array([N])

        tptpar = {}
        for k in ['KPi','KPGA','KGAP','KDHAP','KPext','Pext']:
            tptpar[k] = getattr(self.par,k)
        gettptN = algModule.AlgebraicModule(tptpar, tptN)
        self.add_algebraicModule(gettptN, ['Pi','PGA','GAP','DHAP'], ['N'])


        # add fast reactions
        self.add_isomerase(kf='kf_uni', eq='Keq_TPI', cnames=['GAP','DHAP'], rname='TPI')
        self.add_isomerase(kf='kf_uni', eq='Keq_RPE', cnames=['X5P','Ru5P'], rname='RPE')
        self.add_isomerase(kf='kf_uni', eq='Keq_RPI', cnames=['R5P','Ru5P'], rname='RPI')
        self.add_aldolase(kf='kf_bi', eq='Keq_Ald1', cnames=['DHAP','GAP','FBP'], rname='Ald1')
        self.add_aldolase(kf='kf_bi', eq='Keq_Ald2', cnames=['DHAP','E4P','SBP'], rname='Ald2')
        self.add_allTK()
        #self.add_bibi(kf='kf_bi', eq='Keq_PGK', cnames=['PGA','ATP','BPGA','ADP'], rname='PGK')
        vpgk = rl.reversibleMassActionBiBi('kf_bi','Keq_PGK')
        self.set_rate('PGK', vpgk, 'PGA','ATP','BPGA','ADP')
        self.set_stoichiometry('PGK',{'PGA':-1,'ATP':-1,'BPGA':1})
        self.add_unibi(kf='kf_uni', eq='Keq_GAPDH', cnames=['BPGA','GAP','Pi'], rname='GAPDH')
        self.add_isomerase(kf='kf_uni', eq='Keq_PGI', cnames=['F6P','G6P'], rname='PGI')
        self.add_isomerase(kf='kf_uni', eq='Keq_PGM', cnames=['G6P','G1P'], rname='PGM')


        # RuBisCO
        def vRuBisCO(p, RuBP,PGA,FBP,SBP,Pi):
            
            I = 1 + PGA / p.Ki11 + FBP / p.Ki12 + SBP / p.Ki13 + Pi / p.Ki14 + p.NADPH / p.Ki15
            denom = RuBP + p.Km1 * I
            v = p.V1 * RuBP / denom

            return v

        self.set_rate('RuBisCO', vRuBisCO,
                      'RuBP', 'PGA', 'FBP', 'SBP', 'Pi')

        self.set_stoichiometry('RuBisCO',{'PGA':2})

        # FBPase
        def vFBPase(p, FBP, F6P, Pi):

            I = 1 + F6P / p.Ki61 + Pi / p.Ki62
            denom = FBP + p.Km6 * I
            v = p.V6 * FBP / denom

            return v

        self.set_rate('FBPase', vFBPase, 'FBP', 'F6P', 'Pi')

        self.set_stoichiometry('FBPase',{'FBP':-1,'F6P':1,'Pi':1})

        # SBPase
        def vSBPase(p, SBP, Pi):

            I = 1 + Pi / p.Ki9
            denom = SBP + p.Km9 * I
            v = p.V9 * SBP / denom

            return v

        self.set_rate('SBPase', vSBPase, 'SBP', 'Pi')

        self.set_stoichiometry('SBPase',{'SBP':-1,'S7P':1,'Pi':1})


        def vPRK(p, Ru5P, ATP, PGA, RuBP, Pi, ADP):

            I1 = 1 + PGA / p.Ki131 + RuBP / p.Ki132 + Pi / p.Ki133
            d1 = Ru5P + p.Km131 * I1
            d2 = ATP*(1+ADP/p.Ki134) + p.Km132*(1+ADP/p.Ki135)
            v = p.V13 * Ru5P * ATP / (d1 * d2)

            return v

        self.set_rate('PRK', vPRK, 'Ru5P', 'ATP', 'PGA', 'RuBP', 'Pi', 'ADP')

        self.set_stoichiometry('PRK',{'Ru5P':-1,'ATP':-1})


        def vPS(p, ADP, Pi):

            v = p.V16 * ADP * Pi / ((ADP + p.Km161) * (Pi + p.Km162))
            return v

        self.set_rate('PS', vPS, 'ADP', 'Pi')

        self.set_stoichiometry('PS',{'Pi':-1,'ATP':1})


        def vPGA(p, PGA, N):
            v = p.Vex*PGA/(N*p.KPGA)
            return v
        self.set_rate('TPT_PGA', vPGA, 'PGA', 'N')
        self.set_stoichiometry('TPT_PGA',{'PGA':-1,'Pi':1})

        def vGAP(p, GAP, N):
            v = p.Vex*GAP/(N*p.KGAP)
            return v
        self.set_rate('TPT_GAP', vGAP, 'GAP', 'N')
        self.set_stoichiometry('TPT_GAP',{'GAP':-1,'Pi':1})

        def vDHAP(p, DHAP, N):
            v = p.Vex*DHAP/(N*p.KDHAP)
            return v
        self.set_rate('TPT_DHAP', vDHAP, 'DHAP', 'N')
        self.set_stoichiometry('TPT_DHAP',{'DHAP':-1,'Pi':1})


        def vSS(p, G1P, ATP, ADP, Pi, PGA, F6P, FBP):
            d1 = G1P + p.Kmst1
            d21 = (1+ADP/p.Kist)*(ATP+p.Kmst2)
            d22 = p.Kmst2*Pi/(p.Kast1*PGA+p.Kast2*F6P+p.Kast3*FBP)
            v = p.Vst*G1P*ATP/(d1*(d21+d22))
            return v
        
        self.set_rate('SS',vSS,'G1P','ATP','ADP','Pi','PGA','F6P','FBP')
        self.set_stoichiometry('SS',{'G1P':-1,'ATP':-1,'Pi':2})



# Models using equilibrium module #######################################


class CBBEQMModel(modelbase.AlgmModel):
    """
    super class for mass-action and MM models using equilibrium module
    """

    cpdNames = ['P1','P2','Q']
    eqmNames = ['GAP', 'E4P', 'X5P', 'DHAP', 'R5P', 'F6P', 'S7P', 'Ru5P', 'FBP', 'SBP']

    @staticmethod
    def fluxByCPartition(alpha):
        return np.array([2.+alpha,
                         2.,
                         6.,
                         2.-2.*alpha,
                         alpha])

    @staticmethod
    def normalizeMatrix(M,vnumer,vdenom):
        '''
        returns a 'normalized' matrix. E.g. 
        normalizeMatrix(N,v0,y0) normalizes stoichiometry matrix: v_j^0/y_i^0*n_ij -> n_ij^*
        normalizeMatrix(TH,y0,x0) normalizes equilibrium/elasticities: y_k^0/x_l^0*th_lk -> th_lk^*
        '''
        fnorm = (1./vdenom)[np.newaxis].T * vnumer[np.newaxis]
        return(np.multiply(M,fnorm))
    

    def reverseEngineerMassActionParameters(self, y0, alpha, method='direct'):
        """
        calculates the parameters k1...k5 from a given steady-state solution.
        :y0: steady-state solution
        :alpha: determines the ratio of the two elementary modes. v4=alpha, v5=1-alpha
        :method: 'direct' uses alpha as direct ratio of the two EFMs,
                 'carbon' uses alpha as fraction of carbons exported to starch
        returns: parameters k1,...,k5
        """
    
        eqm = self.algebraicModules[0]['am']

        [GAP, E4P, X5P, DHAP, R5P, F6P, S7P, Ru5P, FBP, SBP] = eqm.getConcentrations(y0)

        k = np.zeros(5)

        if method == 'carbon':
            k[0] = (2. + alpha) / FBP
            k[1] = 2. / SBP
            k[2] = 6. / Ru5P
            k[3] = (2. - 2. * alpha) / GAP
            k[4] = alpha / F6P
        else:
            k[0] = (3 - 2*alpha) / FBP
            k[1] = (2 - alpha) / SBP
            k[2] = (6 - 3*alpha) / Ru5P
            k[3] = alpha / GAP
            k[4] = (1 - alpha) / F6P
        

        k = k / k.max()

        kpar = {}
        for i in range(len(k)):
            kstr = 'k'+str(i+1)
            kpar[kstr] = k[i]


        #self.par.update(kpar)

        return kpar


    def getMMParameters(self,y0,v0,e0):
        '''
        calculates Vmax and KM values from stationary concentrations (y0), fluxes (v0) and
        normalized(!) elasticities e0
        :y0: stationary concentrations of (P1,P2,Q)
        :v0: stationary fluxes
        :e0: normalized elasticities
        :returns: Vmax, KM
        '''

        sid = self.get_argids('FBP','SBP','Ru5P','GAP','F6P')
        X = self.fullConcVec(y0)[sid]

        KM = X*(e0/(1-e0))
        Vm = v0/(1-e0)

        return Vm, KM
    
        
    
    def reverseEngineerMMParameters(self, y0, e0, alpha):
        """
        calculates the parameters KM1...KM5 and Vmax1...Vmax5 from a given steady-state solution
        (y0) and pre-defined elasticities (e0). The elasticities are in relation to the k's
        determined by reverseEngineerMassActionParameters. Therefore, 0<=e0[i]<k[i].
        alpha: determines the ratio of the two elementary modes. v4=alpha, v5=1-alpha
        """
    
        eqm = self.algebraicModules[0]['am']

        [GAP, E4P, X5P, DHAP, R5P, F6P, S7P, Ru5P, FBP, SBP] = eqm.getConcentrations(y0)

        Y = np.array([FBP, SBP, Ru5P, GAP, F6P])

        mapar = self.reverseEngineerMassActionParameters(y0, alpha)
        k = np.array([mapar['k'+str(i+1)] for i in range(5)])

        KM = Y / (k / e0 - 1)
        Vmax = k * (KM + Y)

        kpar = {}
        for i in range(len(k)):

            kstr = 'k'+str(i+1)
            kpar['KM'+str(i+1)] = KM[i]
            kpar['Vmax'+str(i+1)] = Vmax[i]


        #self.par.update(kpar)

        return kpar



    def optimizeNormedElasticities(self, y0, v0, boundary=0.05, method='SLSQP', initialGuess=None):
        '''
        finds elasticities minimizing dominant eigval, based on provided 'target' flux v0.
        Does not need to call 'rates', can be used on 'naked' model without pars.
        '''
        eqm = self.algebraicModules[0]['am']
        x0 = np.array(eqm.getConcentrations(y0))
       
        N = self.normalizeMatrix(self.stoichiometryMatrix(),v0,y0)
        TH = self.normalizeMatrix(eqm.elasticities(y0),y0,x0)

        Hshape = (len(v0), len(eqm.par.compoundNames))
        pid = (np.arange(5),self.get_argids('FBP','SBP','Ru5P','GAP','F6P')-len(self.cpdNames))

        # normalize

        #normN = (1./y0)[np.newaxis].T * v0[np.newaxis]
        #N = np.multiply(normN,N)
        #
        #normTH = (1./x0)[np.newaxis].T * y0[np.newaxis]
        #TH = np.multiply(normTH,TH)

        b = np.array([[boundary,(1-boundary)] for x in range(len(v0))]) # determine boundaries
        #print b

        def stability(x):
            myH = np.zeros(Hshape)
            myH[pid] = x
            (l,v) = LA.eig(N*myH*TH)
            return l.real.max()

        if initialGuess is None:
            optinit = (b[:,1]-b[:,0])/2.
        else:
            optinit = initialGuess

        res = opt.minimize(stability, 
                           optinit, 
                           method=method, 
                           bounds=b, 
                           options={'maxiter':100000})

        if res.success != True:
            print("Warning: minimization did not return success")
        return res.x
        


    def optimizeElasticities(self, y0, alpha=0.5, initialGuess=None, norm=True, boundary=0.05, method='SLSQP'):
        eqm = self.algebraicModules[0]['am']
       
        N = self.stoichiometryMatrix()
        H = self.allElasticities(y0)[:,len(self.algebraicModules[0]['amVars']):]
        TH = eqm.elasticities(y0)

        if norm:
            v0 = self.ratesArray(y0)
            x0 = np.array(eqm.getConcentrations(y0))

            normN = (1./y0)[np.newaxis].T * v0[np.newaxis]
            N = np.multiply(normN,N)

            normH = (1./v0)[np.newaxis].T * x0[np.newaxis]
            H = np.multiply(normH,H)

            normTH = (1./x0)[np.newaxis].T * y0[np.newaxis]
            TH = np.multiply(normTH,TH)


        posEIdx = np.where(np.logical_not(np.isclose(H,0)))

        b = np.array([[boundary*x,(1-boundary)*x] for x in np.asarray(H[posEIdx]).reshape([5])]) # determine boundaries

        def stability(x):
            myH = H.copy()
            myH[posEIdx] = x
            (l,v) = LA.eig(N*myH*TH)
            return l.real.max()

        if initialGuess is None:
            optinit = (b[:,1]-b[:,0])/2.
        else:
            optinit = initialGuess

        res = opt.minimize(stability, 
                           optinit, 
                           method=method, 
                           bounds=b, 
                           options={'maxiter':100000})

        if res.success != True:
            print("Warning: minimization did not return success")
        return res.x





    

class CBBEQMModelMassAction(CBBEQMModel):

    defaultPars = {'k1': 0.1078,
                   'k2': 0.9292,
                   'k3': 1.,
                   'k4': 0.1263,
                   'k5': 0.006174
    }

    def __init__(self, pars = {}, adapt2ss = None, adapt2carbonPartition = 0.5, adaptMethod = 'direct'):
        """
        defines a minimal kinetic model of the Calvin Cycle, using the equilibrium module
        defined in calvinmodel.minimalEQM.
        All rate laws are first-oder mass-action.
        If adapt2ss is set to a state vector, the rate constants are automatically 
        set so that this vector is the steady-state of the system.
        """

        super(CBBEQMModelMassAction, self).__init__(pars, CBBEQMModelMassAction.defaultPars)

        self.set_cpds(CBBEQMModel.cpdNames)

        eqm = eqmodule.MinimalCalvinEQM()

        self.add_algebraicModule(eqm,super(self.__class__,self).cpdNames,super(self.__class__,self).eqmNames)
        
        def v1(p,y):
            return rl.massAction(p.k1,y)

        self.set_rate('v1',v1,'FBP')
        self.set_stoichiometry('v1',{'P1':-2,'P2':1,'Q':3})

        def v2(p,y):
            return rl.massAction(p.k2,y)

        self.set_rate('v2',v2,'SBP')
        self.set_stoichiometry('v2',{'P2':-1,'Q':3})

        def v3(p,y):
            return rl.massAction(p.k3,y)

        self.set_rate('v3',v3,'Ru5P')
        self.set_stoichiometry('v3',{'P1':1,'Q':-2})

        def v4(p,y):
            return rl.massAction(p.k4,y)

        self.set_rate('v4',v4,'GAP')
        self.set_stoichiometry('v4',{'P1':-1})

        def v5(p,y):
            return rl.massAction(p.k5,y)

        self.set_rate('v5',v5,'F6P')
        self.set_stoichiometry('v5',{'P2':-1,'Q':-3})

        if adapt2ss is not None:
            kpar = self.reverseEngineerMassActionParameters(adapt2ss, adapt2carbonPartition, method = adaptMethod)
            self.par.update(kpar)


        


class CBBEQMModelMM(CBBEQMModel):

    defaultPars = {'Vmax1': 1.,
                   'KM1': 1.,
                   'Vmax2': 1.,
                   'KM2': 1.,
                   'Vmax3': 1.,
                   'KM3': 1.,
                   'Vmax4': 1.,
                   'KM4': 1.,
                   'Vmax5': 1.,
                   'KM5': 1.
    }

    def __init__(self, pars = {}, adapt2ss = None, adapt2e = None, adapt2carbonPartition = 0.5):
        """
        defines a minimal kinetic model of the Calvin Cycle, using the equilibrium module
        defined in calvinmodel.minimalEQM.
        All rate laws are first-oder irreversible Michaelis-Menten.
        If adapt2ss is set to a state vector, the rate constants are automatically 
        set so that this vector is the steady-state of the system.
        """

        super(CBBEQMModelMM, self).__init__(pars, CBBEQMModelMM.defaultPars)

        self.set_cpds(CBBEQMModel.cpdNames)

        eqm = eqmodule.MinimalCalvinEQM()

        self.add_algebraicModule(eqm,super(self.__class__,self).cpdNames,super(self.__class__,self).eqmNames)
        
        def v1(p,y):
            return rl.MM1(p.Vmax1, p.KM1, y)

        self.set_rate('v1',v1,'FBP')
        self.set_stoichiometry('v1',{'P1':-2,'P2':1,'Q':3})

        def v2(p,y):
            return rl.MM1(p.Vmax2, p.KM2, y)

        self.set_rate('v2',v2,'SBP')
        self.set_stoichiometry('v2',{'P2':-1,'Q':3})

        def v3(p,y):
            return rl.MM1(p.Vmax3, p.KM3, y)

        self.set_rate('v3',v3,'Ru5P')
        self.set_stoichiometry('v3',{'P1':1,'Q':-2})

        def v4(p,y):
            return rl.MM1(p.Vmax4, p.KM4, y)

        self.set_rate('v4',v4,'GAP')
        self.set_stoichiometry('v4',{'P1':-1})

        def v5(p,y):
            return rl.MM1(p.Vmax5, p.KM5, y)

        self.set_rate('v5',v5,'F6P')
        self.set_stoichiometry('v5',{'P2':-1,'Q':-3})

        if adapt2ss is not None and adapt2e is not None:
            kpar = self.reverseEngineerMMParameters(adapt2ss, adapt2e, adapt2carbonPartition)
            self.par.update(kpar)







    def setMMParameters(self,Vm,KM):
        '''
        sets the parameters from arrays containing Vmax- and KM-values
        :Vm: vector of Vmax-values
        :KM: vector of KM-values
        '''

        pkm = {'KM'+str(i+1):KM[i] for i in range(len(KM))}
        pvm={'Vmax'+str(i+1):Vm[i] for i in range(len(Vm))}

        self.par.update(pkm)
        self.par.update(pvm)

        
        

    def optimizeStability(self, y0, carbonPartition=0.5, method='SLSQP', boundary=0.05, initialGuess=None):

        maModel = CBBEQMModelMassAction(adapt2ss=y0, adapt2carbonPartition=carbonPartition)

        maEqm = maModel.algebraicModules[0]['am']
        
        N = maModel.stoichiometryMatrix()
        H = maModel.allElasticities(y0)[:,3:]
        TH = maEqm.elasticities(y0)

        posEIdx = np.where(np.logical_not(np.isclose(H,0)))

        b = np.array([[boundary*x,(1-boundary)*x] for x in np.asarray(H[posEIdx]).reshape([5])]) # determine boundaries

        def stability(x):
            myH = H.copy()
            myH[posEIdx] = x
            (l,v) = LA.eig(N*myH*TH)
            return l.real.max()

        if initialGuess is None:
            optinit = (b[:,1]-b[:,0])/2.
        else:
            optinit = initialGuess

        res = opt.minimize(stability, 
                           optinit, 
                           method=method, 
                           bounds=b, 
                           options={'maxiter':100000})

        if res.success != True:
            print("Warning: minimization did not return success", res)

        kpar = self.reverseEngineerMMParameters(y0, res.x, carbonPartition)

        self.par.update(kpar)

        return res

    def stabilizeByAllostericRegulator(self, y0, rateName, method='SLSQP', boundary=0.05):

        eqm = self.algebraicModules[0]['am']

        N = self.stoichiometryMatrix()
        TH = eqm.elasticities(y0)
        H = self.allElasticities(y0)[:,3:]

        st = self.stoichiometries[rateName]
        rateNameIds = {v:k for k,v in enumerate(self.rateNames())}
        rid = rateNameIds[rateName]

        vss = self.rates(y0)[rateName]
        xss = self.fullConcVec(y0)

        l = {} # max eigenvalue
        e = {} # elasticities
        for c in eqm.par.compoundNames:
            cid = self.get_argids(c)[0]
            hid = cid-3
            if np.isclose(H[rid,hid],0):
                b = [[-vss/xss[cid],0]] # FIXME: check - this does not consider Vm*X/(KM+X)
                
                def stability(x):
                    myH = H.copy()
                    myH[rid,hid] = x
                    (l,v) = LA.eig(N*myH*TH)
                    return l.real.max()

                res = opt.minimize(stability, 
                                   -0.5*vss/xss[cid], 
                                   method=method, 
                                   bounds=b, 
                                   options={'maxiter':100000})

                if res.success:
                    e[c] = res.x
                    l[c] = res.fun

        return e, l





class ModelConstructionError:
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)
