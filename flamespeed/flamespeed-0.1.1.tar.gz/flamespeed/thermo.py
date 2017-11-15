"""Thermodynamics methods for chemical kinetics.
This module contains a thermochem class with methods for
computing the backward reaction rates for a set of
reversible, elementary reactions.
"""

import numpy as np
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

        # Connect to database
        #path = os.path.abspath('./data/thermo.sqlite')
        path = os.path.abspath(os.path.join(__file__, "../..")) 
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
            raise ValueError("NASA coefficients could not be found. " +
                                "Check species and temperature input.")

        species_db = set(result[:,0])
        if species_db != set(self.species):
            diff = set(self.species) - species_db
            raise ValueError("Coefficients not found for {}".format(diff))

        db.commit()
        db.close()

        # Fetch results
        nasa_coeff = np.asarray(result[:,3:], dtype=float)
        return nasa_coeff

    def Cp_over_R(self, T):

        # Get NASA polynomial coefficients
        a = self.nasa7_coeffs

        # Calculate specific heat
        Cp_R = (a[:,0] + a[:,1] * T + a[:,2] * T**2.0
                + a[:,3] * T**3.0 + a[:,4] * T**4.0)

        return Cp_R


    def H_over_RT(self, T):

        # Get NASA polynomial coefficients
        a = self.nasa7_coeffs

        # Calculate enthalpy
        H_RT = (a[:,0] + a[:,1] * T / 2.0 + a[:,2] * T**2.0 / 3.0
                + a[:,3] * T**3.0 / 4.0 + a[:,4] * T**4.0 / 5.0
                + a[:,5] / T)

        return H_RT


    def S_over_R(self, T):

        # Get NASA polynomial coefficients
        a = self.nasa7_coeffs

        # Calculate entropy
        S_R = (a[:,0] * np.log(T) + a[:,1] * T + a[:,2] * T**2.0 / 2.0
               + a[:,3] * T**3.0 / 3.0 + a[:,4] * T**4.0 / 4.0 + a[:,6])

        return S_R


    def backward_coeffs(self, kf, T):

        # Read in NASA coefficients from database
        self.nasa7_coeffs = self.read_nasa_coeffs(T)

        # Change in enthalpy and entropy for each reaction
        delta_H_over_RT = np.dot(self.nu_coef.T, self.H_over_RT(T))
        delta_S_over_R = np.dot(self.nu_coef.T, self.S_over_R(T))

        # Negative of change in Gibbs free energy for each reaction
        delta_G_over_RT = delta_S_over_R - delta_H_over_RT

        # Prefactor in Ke
        fact = self.p0 / self.R / T

        # Ke
        ke = fact**self.gamma * np.exp(delta_G_over_RT)

        return kf / ke
