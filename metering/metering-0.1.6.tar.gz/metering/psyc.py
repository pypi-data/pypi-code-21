# -*- coding: utf-8 -*-
"""
Created on Thu Sep 03 20:18:37 2015

@author: Ari.Jackson
Sources: Vaisala 2013, HUMIDITY CONVERSION FORMULAS
    and
    W. Wagner and A. Pruß:" The IAPWS Formulation 1995 for the
    Thermodynamic Properties of Ordinary Water Substance for General and
    Scientific Use ", Journal of Physical and Chemical Reference Data, June
    2002 ,Volume 31, Issue 2, pp.387535
Link: http://www.vaisala.com/Vaisala%20Documents/Application%20notes/
      Humidity_Conversion_Formulas_B210973EN-F.pdf
"""

import numpy as np
import matplotlib
matplotlib.use('QT4Agg')
import matplotlib.pyplot as plt


class Psyc():

    @staticmethod
    def dew_point_2(T, RH):
        # Source: https://en.wikipedia.org/wiki/Dew_point
        """T in deg c adn # % RH"""
        b = 17.67
        c = 243.5
        g = lambda t, rh: np.log(RH / 100.) + (17.67 * T) / (243.5 + T)
        Tdp = (c * g(T, RH)) / (b - g(T, RH))
        # return dew pt temp in deg c
        return Tdp

    @staticmethod
    def rho_air(Tc, RH):
        """Air temperature [deg C], RH [%], 1 Atm."""
        # Total pressure [Pa]
        pt = 101325.0
        # Dew point temperature [deg C]
        Tdp = Psyc.dew_point_2(Tc, RH)
        # Partial pressure water vapor [Pa]
        pv = Psyc.water_vapor_saturation_pressure(Tdp + 273.15) * 100.0
        # Partial pressure dry air [Pa]
        pd = pt - pv
        # Molar mass dry air [kg/mol]
        md = 0.028964
        # Molar mass water vapor [kg/mol]
        mv = 0.018016
        # Universal gas constant [J/(K*mol)]
        R = 8.314
        # Density of air and water vapor mixture [kg/m^3]
        rho = (pd * md + pv * mv) / (R * (Tc + 273.15))
        return rho

    @staticmethod
    def dew_point(Pw):
        """Enter water vapor pressure in hPa"""
        # A, m, and Tn are constants from vaisala, Table 1
        A = 6.116441
        m = 7.591386
        Tn = 240.7263
        # Dew point in deg C
        Td = Tn / ((m / np.log10(Pw / A)) - 1)
        return Td

    @staticmethod
    def dry_air_density(T):
        """Method to calculate the density of dry air, T in deg C."""
        # Air temperature [K]
        T += 273.15
        # Total atmospheric pressure [Pa]
        P = 101317.
        # Specific gas constant of dry air [J/(kg*K)]
        R = 286.9
        # Density of dry air [Pa][kg][K][Pa^-1][m^-3][-K]
        return P / (R * T)

    # calculate water vapor saturation pressure between 0 deg C and 373 deg C
    @staticmethod
    def water_vapor_saturation_pressure(T):
        ''' input temperature in degrees Kelvin '''
        T = T / 1.0
        # Critical temperature (deg K)
        Tc = 647.096
        # Critical pressure (hPa)
        Pc = 220640.
        # Coefficients
        C1 = -7.85951783
        C2 = 1.84408259
        C3 = -11.7866497
        C4 = 22.6807411
        C5 = -15.9618719
        C6 = 1.80122502
        # functions
        v = 1 - T / Tc
        Pws = Pc * np.exp((Tc / T) * (
            C1 * v + C2 * v ** 1.5 + C3 * v ** 3 +
            C4 * v ** 3.5 + C5 * v ** 4 + C6 * v ** 7.5))
        # return water vapor saturatino pressure in hPa
        return Pws

    # calculate water vapor pressure
    @staticmethod
    def water_vapor_pressure(Pws, RH):
        ''' input water vapor saturation pressure in hPa
            and percent relitive humidity'''
        Pws = Pws / 1.0
        RH = RH / 1.0
        Pw = Pws * (RH / 100.)
        # return water vapor pressure in hPa
        return Pw

    # calculate mixing ratio
    @staticmethod
    def mixing_ratio(Pw, Pt):
        ''' input water vapor pressure in hPa and
            total ambient pressure in hPa'''
        Pw = Pw / 1.0
        Pt = Pt / 1.0
        # B is equal to the molecular weight of water divided by the molecular
        # weight of air times 1000.
        B = 621.9907
        X = (Pw * B) / (Pt - Pw)
        # return mixing ratio in grams of water over kilograms
        # of dry air (g/kg)
        return X

    # calculate mixing ratio with different inputs
    @staticmethod
    def mixing_ratio_2(T, RH, Pt):
        ''' input temperature in deg C, percent relitive humidity and total
            ambient pressure in hPa'''
        X2 = Psyc.mixing_ratio(
            Psyc.water_vapor_pressure(
                Psyc.water_vapor_saturation_pressure(T + 273.15), RH), Pt)
        # return mixing ratio in grams of water over kilograms
        # of dry air (g/kg)
        return X2

    # calculate enthalpy
    @staticmethod
    def enthalpy(T, RH, Pt):
        ''' input temperature in deg C, percent relitive humidity and total
            ambient pressure in hPa'''
        X = Psyc.mixing_ratio_2(T, RH, Pt)
        H = T * (1.01 + .00189 * X) + 2.5 * X
        # return H in kilojoules per kilogram of dry air (kJ/kga)
        return H

    @staticmethod
    def psyc_chart():
        # total ambient pressure in hPa
        Pt = 1013.25
        # temperature range in degrees C
        T = np.arange(-10, 56, 1)
        # relitive humidity range in percent
        RH = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        fig = plt.figure()
        ax = fig.add_subplot(111)
        # read relitive humidity off right hand axis
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position('right')
        # plot a curve for each relitive humidity in RH array
        for i in RH:
            y = []
            # iterate over temperature array and append humidity ratio to y
            for j in T:
                y.append(Psyc.mixing_ratio_2(j, i, Pt))
            # annotate each curve to indicate percent relitive humidity
            if i == 50:
                # add 'RH=' to label at 50%
                ax.annotate(r'$RH=$' + str(i) + r'$\%$',
                            xy=(T[30], y[33]),
                            xytext=(T[30], y[33]),
                            rotation=np.rad2deg(
                            np.arctan((y[32] - y[31]) / (1))))
            else:
                ax.annotate(str(i) + r'$\%$',
                            xy=(T[30], y[32] - i * 0.006),
                            xytext=(T[30], y[32] - i * 0.006),
                            rotation=np.rad2deg(
                            np.arctan((y[30] - y[29]) / (1))))
            plt.plot(T, y, color='k', lw='1')
        plt.title(r'Psychrometric Chart' + '\n' + ' $P=1013.25 \ (hPa)$')
        plt.xlabel(r'Dry Bulb Temperature $\left(^{\circ} C\right)$')
        plt.ylabel(
            r'Humidity Ratio $\left(\frac{g_{water}}{kg_{dry \ air}}\right)$')
        plt.xlim(-10, 55)
        plt.ylim(0, 35)
        plt.grid()
        plt.xticks(np.arange(-10, 56, 5))
        plt.yticks(np.arange(0, 35, 1))
        plt.get_current_fig_manager().window.showMaximized()
        plt.tight_layout()
        plt.show()
