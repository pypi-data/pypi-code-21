"""Thermodynamics methods for chemical kinetics.
This module contains a thermochem class with methods for
computing the backward reaction rates for a set of
reversible, elementary reactions.
"""

import numpy as np
from flamespeed import chemkin
import sqlite3
import os

class thermochem:
    """Methods for calculating the backward reaction rate.

    Methods:
    =======
    Cp_over_R:          Returns specific heat of each specie given by
                        the NASA polynomials.
    H_over_RT:          Returns the enthalpy of each specie given by
                        the NASA polynomials.
    S_over_R:           Returns the entropy of each specie given by
                        the NASA polynomials.
    backward_coeffs:    Returns the backward reaction rate
                        coefficient for reach reaction.
    """

    def __init__(self, species, nu_coef):
        self.species = species
        self.nu_coef = nu_coef
        self.p0 = 1.0e+05 # Pa
        self.R = 8.3144598 # J / mol / K
        self.gamma = np.sum(self.nu_coef, axis=0)


    def read_nasa_coeffs(self, T):
        """Function to read NASA Coefficients from the NASA database file.

        INPUTS:
        =======
        T: Temperature (in Kelvin)

        RETURNS:
        ========
        NASA Coefficients
        """

        # Connect to database
        path = os.path.dirname(__file__)
        db = sqlite3.connect(path + '/data/thermo.sqlite')
        cursor = db.cursor()

        # Create temp table to store coefficients
        cursor.execute("DROP TABLE IF EXISTS TEMP")
        cursor.execute('''CREATE TABLE TEMP (
                           SPECIES_NAME TEXT PRIMARY KEY NOT NULL,
                           TLOW INT NOT NULL,
                           THIGH INT NOT NULL,
                           COEFF_1 FLOAT,
                           COEFF_2 FLOAT,
                           COEFF_3 FLOAT,
                           COEFF_4 FLOAT,
                           COEFF_5 FLOAT,
                           COEFF_6 FLOAT,
                           COEFF_7 FLOAT)''')

        # Populate temp table with NASA coefficients in temp range
        tbls =['LOW', 'HIGH']
        for sp in self.species:
            for t in tbls:
                query = '''INSERT INTO TEMP
                           SELECT * FROM ''' + t + '''
                           WHERE SPECIES_NAME = "''' + sp + '''"
                           AND ''' + str(T) + ''' BETWEEN TLOW AND THIGH '''
                cursor.execute(query)

        # Check if coefficients returned for each specie
        query = "SELECT * FROM TEMP"
        result = np.array(cursor.execute(query).fetchall())
        if len(result) == 0:
            db.close()
            raise ValueError("NASA coefficients could not be found in database. " +
                                "Check species and temperature input.")

        species_db = set(result[:,0])
        if species_db != set(self.species):
            db.close()
            diff = set(self.species) - species_db
            raise ValueError("Coefficients not found for {}".format(diff))

        db.commit()
        db.close()

        # Fetch results
        nasa_coeff = np.asarray(result[:,3:], dtype=float)
        
        return nasa_coeff

    def Cp_over_R(self, T, nasa7_coeffs):
        """Function to return Specific Heat at constant pressure over Ideal Gas Constant (R) from NASA database file.

        INPUTS:
        =======
        T: Temperature (in Kelvin)

        RETURNS:
        ========
        Specific Heat at constant pressure over Ideal Gas Constant (C/R)

        EXAMPLE
        ========

        >>> r = chemkin.ReactionRate()
        >>> read_object = r.read_XML('./data/rxns_reversible.xml')
        >>> thermo = thermochem(r.species_list, r.nu_coef)
        >>> coef = thermo.read_nasa_coeffs(750)
        >>> thermo.Cp_over_R(750, coef)
        array([ 2.5       ,  2.52868224,  3.58287894,  3.54323475,  4.58446853,
                4.01605268,  5.34001984,  6.90765739])
        """

        # Get NASA polynomial coefficients
        a = nasa7_coeffs

        # Calculate specific heat
        Cp_R = (a[:,0] + a[:,1] * T + a[:,2] * T**2.0
                + a[:,3] * T**3.0 + a[:,4] * T**4.0)

        return Cp_R


    def H_over_RT(self, T, nasa7_coeffs):
        """Function to return Enthalpy Change (Delta S) over Ideal Gas Constant times Temperature (RT) from the NASA database.

        INPUTS:
        =======
        T: Temperature (in Kelvin)

        RETURNS:
        ========
        Enthalpy Change (Delta S) over Ideal Gas Constant times Temperature (RT).

        EXAMPLE
        ========

        >>> r = chemkin.ReactionRate()
        >>> read_object = r.read_XML('./data/rxns_reversible.xml')
        >>> thermo = thermochem(r.species_list, r.nu_coef)
        >>> coef = thermo.read_nasa_coeffs(750)
        >>> thermo.H_over_RT(750, coef)
        array([ 36.46487987,  41.50114822,   8.45447683,   2.12014526,
               -36.20075884,   2.27065186,   4.90875924, -18.12328001])
        """

        # Get NASA polynomial coefficients
        a = nasa7_coeffs

        # Calculate enthalpy
        H_RT = (a[:,0] + a[:,1] * T / 2.0 + a[:,2] * T**2.0 / 3.0
                + a[:,3] * T**3.0 / 4.0 + a[:,4] * T**4.0 / 5.0
                + a[:,5] / T)

        return H_RT


    def S_over_R(self, T, nasa7_coeffs):

        """Function to return Entropy Change (Delta S) over Ideal Gas Constant (R) from the NASA database.

        INPUTS:
        =======
        T: Temperature (in Kelvin)

        RETURNS:
        ========
        Entropy Change (Delta S) over Ideal Gas Constant (R).

        EXAMPLE
        ========

        >>> r = chemkin.ReactionRate()
        >>> read_object = r.read_XML('./data/rxns_reversible.xml')
        >>> thermo = thermochem(r.species_list, r.nu_coef)
        >>> coef = thermo.read_nasa_coeffs(750)
        >>> thermo.S_over_R(750, coef)
        array([ 16.10350016,  21.74032158,  25.3834352 ,  18.96095961,
                26.62123356,  28.11496866,  31.90497296,  33.69036738])
        """

        # Get NASA polynomial coefficients
        a = nasa7_coeffs

        # Calculate entropy
        S_R = (a[:,0] * np.log(T) + a[:,1] * T + a[:,2] * T**2.0 / 2.0
               + a[:,3] * T**3.0 / 3.0 + a[:,4] * T**4.0 / 4.0 + a[:,6])

        return S_R


    def backward_coeffs(self, kf, T):
        """Function to calculate and return the backword coefficents.

        INPUTS:
        =======
        kf: Forward Reaction Rate Coefficient
        T: Temperature (in Kelvin)

        RETURNS:
        ========
        kf / ke where ke is the equilibrium coefficient

        EXAMPLE
        ========
        >>> x = np.array([2.0, 1.0, 0.5, 1.0, 1.0, 1.5, 0.5, 1])
        >>> r = chemkin.ReactionRate()
        >>> _ = r.read_XML('./data/rxns_reversible.xml')
        >>> _ = r.set_temp(750)
        >>> _ = r.get_progress_rate(x)
        >>> thermo = thermochem(r.species_list, r.nu_coef)
        >>> thermo.backward_coeffs(r.kf, 750)
        array([  6.87957490e+16,   1.46799091e+12,   4.59745372e+08,
                 2.20804467e+15,   3.20879584e-03,   1.01529193e+02,
                 1.19667070e-02,   1.16060459e-06,   1.34790770e-08,
                 5.63257222e+07,   1.98391875e+07])
        """

        # Read in NASA coefficients from database
        nasa7_coeffs = self.read_nasa_coeffs(T)

        # Change in enthalpy and entropy for each reaction
        delta_H_over_RT = np.dot(self.nu_coef.T, self.H_over_RT(T, nasa7_coeffs))
        delta_S_over_R = np.dot(self.nu_coef.T, self.S_over_R(T, nasa7_coeffs))

        # Negative of change in Gibbs free energy for each reaction
        delta_G_over_RT = delta_S_over_R - delta_H_over_RT

        # Prefactor in Ke
        fact = self.p0 / self.R / T

        # Ke
        ke = fact**self.gamma * np.exp(delta_G_over_RT)

        return kf / ke