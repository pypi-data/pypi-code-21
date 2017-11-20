import numbers
import xml.etree.ElementTree as ET
import numpy as np
import sqlite3
import doctest
from chem_G5 import reaction_coeffs


class ElementaryRxn():
    '''
    member attributes:
        r_stoich: numeric list of lists or array
                  column length must equal length of x
                  number of columns indicates number of reactions
                  stoichiometric coefficients of reactants
        p_stoich: numeric list of lists or array
                  must be equal in shape to stoich_r
                  stoichiometric coefficients of products
        k:        a numeric value (or values, for multiple reactions)
                  reaction rate coefficient
    '''

    def __init__(self, filename):
        self.parse(filename)

    def parse(self, filename):
        root = ET.parse(filename).getroot()
        specieslist = root.find('phase').find('speciesArray').text.strip().split(' ')
        # commenting out the below because we won't be receiving the
        # concentrations from the input .xml file, however this could be useful
        # later if we might want to specify initial concentrations in the .xml
        #conc_list = list(map(lambda x: float(x),
        #    root.find('phase').find('concentrations').text.strip().split(' ')))
        # k_list = []
        r_stoich = []
        p_stoich = []
        self.reversible = []
        self.rxnparams = []
        for reaction in root.find('reactionData').findall('reaction'):
            if reaction.attrib['reversible'] == 'yes':
                self.reversible.append(True)
            else:
                self.reversible.append(False)
            # the stoichiometric coefficients will be stored in these arrays according
            # to the ordering given in the variable specieslist
            r_coeffs = [0] * len(specieslist)
            p_coeffs = [0] * len(specieslist)
            # these 2 lists are the information of specie and stoichiometric coefficient
            # gleaned from the .xml file
            r_list = reaction.find('reactants').text.strip().split(' ')
            p_list = reaction.find('products').text.strip().split(' ')
            for r in r_list:
                specie_coeff = r.split(':')
                # this indexing ensures that the same ordering is kept as in specieslist
                r_coeffs[specieslist.index(specie_coeff[0])] = float(specie_coeff[1])
            for p in p_list:
                specie_coeff = p.split(':')
                p_coeffs[specieslist.index(specie_coeff[0])] = float(specie_coeff[1])
            r_stoich.append(r_coeffs)
            p_stoich.append(p_coeffs)
            ratecoeff = reaction.find('rateCoeff')
            if ratecoeff.find('Arrhenius') is None:
                # constant rate coeff
                self.rxnparams.append([reaction_coeffs.const(float(ratecoeff.find('k').text))])
            else:
                # Arrhenius
                if ratecoeff.find('Arrhenius').find('A') is None:
                    raise ValueError("A is not found")
                if ratecoeff.find('Arrhenius').find('E') is None:
                    raise ValueError("E is not found")
                A = float(ratecoeff.find('Arrhenius').find('A').text)
                E = float(ratecoeff.find('Arrhenius').find('E').text)
                b = ratecoeff.find('Arrhenius').find('b')
                self.rxnparams.append([A, E, b])

        # the transpose here is just to have the stoichiometric coefficients for each
        # specie lie along a column, with each column being another reaction
        self.r_stoich = np.array(r_stoich).transpose()
        self.p_stoich = np.array(p_stoich).transpose()
        # self.k = k_list
        self.specieslist = specieslist
        # rxn = chemkin.ElementaryRxn(conc_list, r_stoich, k_list)
        # print(chemkin.rxn_rate(conc_list, r_stoich, k_list, p_stoich))
        # return np.array(rxn.rxn_rate(p_stoich))

    def prog_rate(self, x, T):
        '''
        Returns the progress rate for N species going through M
        irreversible, elementary reactions.

        INPUTS
        ======
        x:       numeric list
                 concentrations of A, B, C

        RETURNS
        =======
        omega:   the progress rate for the reaction, numeric

        EXAMPLES
        =======
        >>> ElementaryRxn('chem_G5/test/doctest1.xml').prog_rate([1, 2, 4], 1200)
        [20.0]

        >>> ElementaryRxn('chem_G5/test/doctest2.xml').prog_rate([1,2,1], 1200)
        [40.0, 10.0]
        '''
        k = []
        for elt in self.rxnparams:
            if len(elt) == 1:
                k.append(elt[0])
            elif elt[2] is None:
                k.append(reaction_coeffs.arrh(elt[0], elt[1], T))
            else:
                k.append(reaction_coeffs.mod_arrh(elt[0],
                    float(elt[2].text), elt[1], T))
        x = np.array(x)
        stoich = np.array(self.r_stoich)
        k = np.array(k)

        assert (np.issubdtype(x.dtype, np.number)), "Species concentrations must be numeric"
        assert (np.issubdtype(stoich.dtype, np.number)), "Stoichiometric coefficients must be numeric"
        assert (len(x) == stoich.shape[0]), "All species must have stoichiometric coefficients"

        assert (np.issubdtype(k.dtype, np.number)), "Reaction rate coefficients must be numeric"

#       if len(np.shape(stoich)) == 1: # Handle the one-reaction case
#           return list(k * np.product(x**stoich.T))
#       else:
        return list(k * np.product(x**stoich.T, axis=1))

    def rxn_rate(self, x, T):
        '''
        Returns the reaction rate, f, for each specie (listed in x)
        through one or multiple (number of columns in stoich_r)
        elementary, irreversible reactions.

        f = sum(omega_j*nu_ij) for i species in j reactions.

        INPUTS
        ======
        x:        numeric list or array
                  concentrations of reactants

        RETURNS
        =======
        f:        the reaction rate for each specie, numeric

        EXAMPLES
        =======
        >>> ElementaryRxn('chem_G5/test/doctest3.xml').rxn_rate([1,2,1], 1200)
        array([-30., -60.,  20.])

        '''
        p_stoich = np.array(self.p_stoich)
        r_stoich = np.array(self.r_stoich)
#        assert(stoich_r.shape == stoich_p.shape), "Reactant and product stoich. coefficients must be same dimensions"

        # Get a list of progress rates for each reaction
        omega = self.prog_rate(x, T)

        # Multiply by difference in stoichiometric coefficients,
        # then sum across reactions.
        if np.shape(p_stoich)[1] == 1: # Handle the one-reaction case
            return np.sum(omega * (p_stoich - r_stoich))
        else:
            return np.sum(omega * (p_stoich - r_stoich), axis=1)

    def __str__(self):
        return("Stoichiometric coefficients of reactants: {}\n\
            Stoichiometric coefficients of reactants: {}\n\
            Reaction rate coefficient: {}".format(self.r_stoich,\
            self.p_stoich, self.k))

class ReversibleRxn(ElementaryRxn):

# we should definitely print a lot of things while testing this...
# we should print out the ke's when they're calculated and also the kb's
# to make sure we do those things correctly...

    def __init__(self, filename):
        self.parse(filename)
        self.s = self.specieslist
        self.r = self.r_stoich
        self.p = self.p_stoich
        self.nuij = self.p - self.r
        self.p0 = 1.0e+05
        self.R = 8.3144598
        self.gamma = np.sum(self.nuij, axis=0)

    def read_SQL(self, T):

        def choose_t_range(T):
            t_range=[]
            for species in self.s:
                v=cursor.execute('''SELECT THIGH
                from LOW WHERE species_name= ?''', (species,)).fetchall()
                if v[0][0] > T:
                    t_range.append('high')
                else:
                    t_range.append('low')
            return t_range

        def get_coeffs(species_name, temp_range):
            if temp_range == 'low':
                v=cursor.execute('''SELECT COEFF_1,COEFF_2,COEFF_3,COEFF_4,COEFF_5,COEFF_6,COEFF_7
                from LOW WHERE species_name= ?''',(species_name,)).fetchall()
            elif temp_range == 'high':
                v=cursor.execute('''SELECT COEFF_1,COEFF_2,COEFF_3,COEFF_4,COEFF_5,COEFF_6,COEFF_7
                from HIGH WHERE species_name= ?''',(species_name,)).fetchall()
            coeffs=v[0]
            return coeffs

        assert isinstance(T, numbers.Number), "Please enter a numeric temperature."

        db = sqlite3.connect('chem_G5/data/NASA.sqlite')
        cursor = db.cursor()
        coefs = []
        t_range = choose_t_range(T)
        s_t = zip(self.s, t_range)
        for species, tmp in s_t:
            coef = get_coeffs(species, tmp)
            coefs.append(coef)
        self.nasa = np.array(coefs)

    def Cp_over_R(self, T):
        a = self.nasa
        Cp_R = (a[:,0] + a[:,1] * T + a[:,2] * T**2.0
                + a[:,3] * T**3.0 + a[:,4] * T**4.0)
        return Cp_R

    def H_over_RT(self, T):
        a = self.nasa
        H_RT = (a[:,0] + a[:,1] * T / 2.0 + a[:,2] * T**2.0 / 3.0
                + a[:,3] * T**3.0 / 4.0 + a[:,4] * T**4.0 / 5.0
                + a[:,5] / T)
        return H_RT

    def S_over_R(self, T):
        a = self.nasa
        S_R = (a[:,0] * np.log(T) + a[:,1] * T + a[:,2] * T**2.0 / 2.0
               + a[:,3] * T**3.0 / 3.0 + a[:,4] * T**4.0 / 4.0 + a[:,6])
        return S_R

    def backward_coeffs(self, T):
        # Change in enthalpy and entropy for each reaction
        delta_H_over_RT = np.dot(self.nuij.T, self.H_over_RT(T))
        delta_S_over_R = np.dot(self.nuij.T, self.S_over_R(T))

        # Negative of change in Gibbs free energy for each reaction
        delta_G_over_RT = delta_S_over_R - delta_H_over_RT

        # Prefactor in Ke
        fact = self.p0 / self.R / T
        print("prefactor in Ke: ", fact)
        # Ke
        ke = fact**self.gamma * np.exp(delta_G_over_RT)
        print("ke: ", ke)
        kf = []
        for elt in self.rxnparams:
            if len(elt) == 1:
                kf.append(elt)
            elif elt[2] is None:
                kf.append(reaction_coeffs.arrh(elt[0], elt[1], T))
            else:
                kf.append(reaction_coeffs.mod_arrh(elt[0],
                    float(elt[2].text), elt[1], T))
        self.kf = np.array(kf)
        self.kb = np.copy(self.kf)
        for i in range(len(self.kb)):
            if self.reversible[i]:
                self.kb[i] = self.kf[i] / ke[i]
        print("kb: ", self.kb)

    def prog_rate(self, x, T):

        self.read_SQL(T)
        self.backward_coeffs(T)
        x = np.array(x)

        omega=self.kf*np.product(x**self.r.T)-self.kb*np.product(x**self.p.T)
        return omega

    def rxn_rate(self, x, T):
        omega = self.prog_rate(x, T)
        return np.sum(omega * self.nuij, axis=1)

    def reversible_rxn_rate(x):
        '''
        Returns the reaction rate, f, for each specie (listed in x)
        through one or multiple (number of columns in stoich_r)
        reversible reactions.

        f = sum(omega_j*nu_ij) for i species in j reactions.

        INPUTS
        ======
        x:        numeric list or array
                  concentrations of reactants

        RETURNS
        =======
        f:        the reaction rate for each specie, numeric
        '''
        raise NotImplementedError



class NonelRxn(ElementaryRxn):
    def nonel_rxn_rate(x):
        '''
        Returns the reaction rate, f, for each specie (listed in x)
        through one or multiple (number of columns in stoich_r)
        nonelementary reactions.

        f = sum(omega_j*nu_ij) for i species in j reactions.

        INPUTS
        ======
        x:        numeric list or array
                  concentrations of reactants

        RETURNS
        =======
        f:        the reaction rate for each specie, numeric
        '''
        raise NotImplementedError

