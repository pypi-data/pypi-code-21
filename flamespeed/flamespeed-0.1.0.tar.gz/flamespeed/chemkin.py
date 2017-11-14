"""Flamespeed chemical kinetics library."""

# Author:   Bernard Kleynhans
#           Yaniv Toledano
#           Timothy Lee

import os
import numpy as np
import xml.etree.ElementTree as ET


class ReactionParser():
    """This class contains functions to parse reaction data from XML."""

    def __init__(self):
        """Initialize ReactionParser."""
        self.struct = []
        self.keys = []
        self.keys.append('phase')
        self.keys.append('reactionData')
        self.keys.append('reaction')
        self.keys.append('rateCoeff')
        self.keys.append('reactants')
        self.keys.append('products')

    def check_keys(self):
        """Function checks XML tags for completeness.

        INPUTS:
        =======
        rxns: XML file

        RETURNS:
        ========
        Error message if tags are missing

        """
        for k in self.keys:
            varlist = [j.tag for j in self.rxns.iter(k)]
            if len(varlist) == 0:
                raise ValueError(k + " type not included in input file.")
            self.struct.append([k, len(varlist)])

    def check_consistency(self):
        """Function checks XML consistency.

        INPUTS:
        =======
        rxns: XML file

        RETURNS:
        ========
        Error message if system not covered or if data is missing

        """
        num_items = 0
        for k in self.struct:
            key, val = k
            if key in ('phase', 'reactionData'):
                if val != 1:
                    raise NotImplementedError("Cannot deal with more than one system.")
            else:
                if num_items == 0:
                    num_items = val
                elif num_items != val:
                    raise ValueError("Missing data in input file.")

    def check_reaction_types(self):
        """Function checks reaction types.

        INPUTS:
        =======
        rxns: XML file

        RETURNS:
        ========
        Error message if reaction type not covered

        """
        for r in self.rxns.iter('reaction'):
            if r.attrib['reversible'] != 'no' or r.attrib['type'] != 'Elementary':
                raise NotImplementedError(r.attrib['id'] +
                                          ": Can only deal with reversible," +
                                          " elementary reactions at present.")

    def check_input_file(self, rxns):
        """Function performs initial checks on XML file.

        INPUTS:
        =======
        rxns: XML file

        RETURNS:
        ========
        Error messages if any

        """
        self.rxns = rxns
        self.check_keys()
        self.check_consistency()
        self.check_reaction_types()

    def parse_species(self, rxns):
        """Function that returns list of species.

        INPUTS:
        =======
        rxns: XML file

        RETURNS:
        ========
        species: list of species

        """
        try:
            for s in rxns.findall('phase'):
                species = s.find('speciesArray').text.split()
        except:
            raise NotImplementedError("XML file contains no phase element.")
        return species

    def parse_reaction_rate_params(self, reaction):
        """Function that returns reaction rate coefficient parameters.

        INPUTS:
        =======
        reaction: parsed from XML

        RETURNS:
        ========
        d: dictionary of reaction rate coefficient type and relevant parameters

        """
        for rateCoeff in reaction.find('rateCoeff'):
            if rateCoeff.tag == 'Arrhenius':
                try:
                    A = float(rateCoeff.find('A').text)
                    E = float(rateCoeff.find('E').text)
                    d = {'Type': rateCoeff.tag, 'A': A, 'E': E}
                except:
                    raise ValueError("Reaction coefficient parameters not as expected.")

            elif rateCoeff.tag == 'modifiedArrhenius':
                try:
                    A = float(rateCoeff.find('A').text)
                    b = float(rateCoeff.find('b').text)
                    E = float(rateCoeff.find('E').text)
                    d = {'Type': rateCoeff.tag, 'A': A, 'b': b, 'E': E}
                except:
                    raise ValueError("Reaction coefficient parameters not as expected.")

            elif rateCoeff.tag == 'Constant':
                try:
                    k = float(rateCoeff.find('k').text)
                    d = {'Type': rateCoeff.tag, 'k': k}
                except:
                    raise ValueError("Non-numeric coefficient rate parameters.")

            else:
                raise NotImplementedError(rateCoeff.tag +
                                          " has not been implemented.")

            return d

    def parse_stoich_coefs(self, string, species):
        """Function that returns stoichiometric coefficients.

        INPUTS:
        =======
        species: string parsed from XML

        RETURNS:
        ========
        coef_out: dictionary of stoichiometric coefficients

        """
        coef_out = np.zeros(len(species))
        components = string.split()
        try:
            for c in components:
                specie, coef = c.split(':')
                idx = species.index(specie)
                coef_out[idx] = int(coef)
        except:
            raise ValueError("Coefficient could not be matched with specie.")
        return coef_out


class ReactionCoefficients():
    """This class contains functions that return reaction rate coefficients."""

    def k_const(self, k=1.0):
        """Simply returns a constant reaction rate coefficient.

        INPUTS:
        =======
        k: float, default value = 1.0
           Constant reaction rate coefficient

        RETURNS:
        ========
        self.k: float
           Constant reaction rate coefficient

        EXAMPLES:
        =========
        >>> ReactionCoefficients().k_const()
        1.0
        >>> ReactionCoefficients().k_const(5)
        5.0

        """
        if k < 0:
            raise ValueError("Negative reaction rate coefficients are prohibited.")

        return float(k)

    def k_arrhenius(self, A, E, T, R=8.314):
        """Arrhenius reaction rate coefficient.

        INPUTS
        =======
        A: float, positive
           Arrhenius prefactor
        E: float
           Activation energy
        T: float, positive
           Temperature in Kelvin
        R: float, positive, default value = 8.314
           Ideal gas constant

        RETURNS
        ========
        self.arr: float
           Arrhenius reaction rate coefficient

        EXAMPLES
        =========
        >>> ReactionCoefficients().k_arrhenius(A=10**7, E=15**2, T=100, R=8.314)
        7629003.518942502
        >>> ReactionCoefficients().k_arrhenius(A=2**7, E=15**2, T=100)
        97.65124504246403

        """
        if A < 0:
            raise ValueError("A = {0:18.16e}:  \
                    Negative Arrhenius prefactor not allowed.".format(A))

        if T < 0.0:
            raise ValueError("T = {0:18.16e}: \
                    Negative temperatures not allowed".format(T))

        if R < 0.0:
            raise ValueError("R = {0:18.16e}: \
                    Negative ideal gas constant is prohibited!".format(R))

        self.arr = A * np.exp(-(E / (R * T)))
        return float(self.arr)

    def k_arrhenius_mod(self, A, b, E, T, R=8.314):
        """Modified Arrhenius reaction rate coefficient.

        INPUTS
        =======
        A: float, positive
           Arrhenius prefactor
        b: float
           Modified Arrhenius parameter
        E: float
           Activation energy
        T: float, positive
           Temperature in Kelvin
        R: float, positive, default value = 8.314
           Ideal gas constant

        RETURNS
        ========
        self.k_modarr: float
           Modified Arrhenius reaction rate coefficient

        EXAMPLES
        =========

        >>> ReactionCoefficients().k_arrhenius_mod(A=2**7, b=1, E=15**2, T=100, R=8.314)
        9765.124504246403
        >>> ReactionCoefficients().k_arrhenius_mod(A=2**7, b=3, E=15**2, T=100)
        97651245.04246403

        """
        if A < 0:
            raise ValueError("A = {0:18.16e}:  \
                    Negative Arrhenius prefactor not allowed.".format(A))

        if T <= 0.0:
            raise ValueError("T = {0:18.16e}: \
                    Negative temperatures not allowed".format(T))

        if R < 0.0:
            raise ValueError("R = {0:18.16e}: \
                    Negative ideal gas constant is prohibited!".format(R))

        self.k_modarr = A * T**b * np.exp(-(E / (R * T)))
        return float(self.k_modarr)


class ReactionRate(ReactionCoefficients, ReactionParser):
    """Base class with functions to calculate progress and reaction rates."""

    def __init__(self):
        """Initialize ReactionRate class."""
        super().__init__()
        self.num_reactions = 0
        self.num_species = 0
        self.rev = ""
        self.rtype = ""
        self.species_list = []
        self.k_params = []
        self.k = []
        self.reactant_coef = []
        self.product_coef = []

    def __str__(self):
        """Return summary of XML file contents."""
        if self.num_reactions == 0:
            return "None"
        else:
            return "Number_of_reactions:{} \
                    \nNumber_of_species:{} \
                    \nReversible:{} \
                    \nReaction_type:{} \
                    \nSpecies_list:{}\n" \
                        .format(self.num_reactions,
                                self.num_species,
                                self.rev,
                                self.rtype,
                                self.species_list)

    def __repr__(self):
        """Return class type."""
        return "<chemkin.ReactionRate>"

    def __len__(self):
        """Returns number of reactions."""
        return self.num_reactions

    def read_XML(self, path):
        """Reads XML from file path and extracts reaction information.

        INPUTS
        =======
        path: string, path to the XML file

        RETURNS
        ========
        self: ReactionRate class instance

        EXAMPLE
        ========
        >>> ReactionRate().read_XML('../data/rxns_hw5.xml')
        <chemkin.ReactionRate>

        """
        # Clear local class variable contents
        self.__init__()
        # Import file
        # path = os.path.join(os.getcwd(), path)
        tree = ET.parse(path)
        rxns = tree.getroot()

        # Checks
        self.check_input_file(rxns)

        # Get list of species
        self.species_list = self.parse_species(rxns)
        self.num_species = len(self.species_list)

        # Get reaction data
        for reaction in rxns.find('reactionData').findall('reaction'):
            self.num_reactions += 1

            self.rev = False if reaction.attrib['reversible'] == 'no' else True
            self.rtype = reaction.attrib['type']

            # Elementary, reversible reactions
            if not self.rev and self.rtype == 'Elementary':

                # Get reaction rate coefficient parameters
                p = self.parse_reaction_rate_params(reaction)
                self.k_params.append(p)

                # Get stoichiometric coefficients
                s = reaction.find('reactants').text
                r = self.parse_stoich_coefs(s, self.species_list)
                self.reactant_coef.append(r)

                # Get stoichiometric coefficients for products
                s = reaction.find('products').text
                p = self.parse_stoich_coefs(s, self.species_list)
                self.product_coef.append(p)

            else:
                raise NotImplementedError('Non-elementary / ' +
                                          'Reversible reactions not implemented')

        # Transpose and convert to np arrays
        self.reactant_coef = np.asarray(self.reactant_coef).T
        self.product_coef = np.asarray(self.product_coef).T

        return self

    def set_temp(self, T):
        """Calculate reaction rate coefficients at specified temperature.

        INPUTS
        =======
        T: Float, positive
           Temperature in Kelvin

        RETURNS
        =======
        k: float
           Reaction rate coefficients for each reaction

        EXAMPLE
        ========
        >>> ReactionRate().read_XML('../data/rxns_hw5.xml').set_temp(1500)
        <chemkin.ReactionRate>

        """
        try:
            T = float(T)
        except:
            raise ValueError("Temperature must be numeric.")

        if len(self.k_params) == 0:
            raise TypeError("Reaction data not imported. Use read_XML method.")

        for d in self.k_params:
            name = d['Type']
            if name == 'Arrhenius':
                A, E = d['A'], d['E']
                val = self.k_arrhenius(A, E, T)
            elif name == "modifiedArrhenius":
                A, b, E = d['A'], d['b'], d['E']
                val = self.k_arrhenius_mod(A, b, E, T)
            elif name == "Constant":
                c = d['k']
                val = self.k_const(c)
            self.k.append(val)

        return self

    def get_progress_rate(self, concs):
        """Calculate progress rate for a system of elementary, irreversible reactions.

        INPUTS
        =======
        concs:          numpy array of floats
                        size: num_species
                        concentration of species

        RETURNS
        ========
        w:              numpy array of floats
                        size: num_reactions
                        progress rate for each reaction

        EXAMPLES
        =========
        >>> ReactionRate().read_XML('../data/rxns_hw5.xml').set_temp(1500).get_progress_rate(np.array([2.0, 1.0, 0.5, 1.0, 1.0]))
        array([  2.81117621e+08,   5.00000000e+03,   4.48493847e+06])

        """
        if len(self.reactant_coef) == 0:
            raise TypeError("Reaction data not imported. Use read_XML method.")

        if len(self.k) == 0:
            raise TypeError("Reaction coefficients needs to be calculated with set_temp method.")

        if self.num_species != len(concs):
            raise ValueError("Dimensions of concentration and coefficient arrays are not aligned.")

        if np.sum(concs < 0) != 0:
            raise ValueError("Negative specie concentrations.")

        # Get progress rate
        w = []
        for i in range(self.num_reactions):
            r = self.k[i] * np.product(np.power(concs, self.reactant_coef[:,i]))
            w.append(r)

        return np.asarray(w)

    def get_reaction_rate(self, concs):
        """Calculate reaction rate for a system of elementary, irreversible reactions.

        INPUTS
        =======
        concs:          numpy array of floats
                        size: num_species
                        concentration of species

        RETURNS
        ========
        f:              numpy array of floats
                        size: num_species
                        reaction rate for each specie

        EXAMPLES
        =========
        >>> ReactionRate().read_XML('../data/rxns_hw5.xml').set_temp(1500).get_reaction_rate(np.array([2.0, 1.0, 0.5, 1.0, 1.0]))
        array([ -2.81117621e+08,  -2.85597559e+08,   5.66715180e+08,
                 4.47993847e+06,  -4.47993847e+06])

        """
        # Input values
        if np.sum(concs < 0) != 0:
            raise ValueError("Specie concentrations cannot be negative.")

        # Get progress rate
        w = self.get_progress_rate(concs)

        # Reaction rates
        nu = self.product_coef - self.reactant_coef
        f = np.dot(nu, w)

        return f
