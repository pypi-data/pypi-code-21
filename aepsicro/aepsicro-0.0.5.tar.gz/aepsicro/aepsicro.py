# -*- encoding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"""
Librería para desarrollo de operaciones psicrométricas.
Autor: Antonio Eduardo Téllez Santos
Año: 2017
Licencia GPLv3
Requiere scipy, numpy, matpolotlib
"""
import math
import copy
from scipy.optimize import fsolve
import matplotlib
import numpy
from matplotlib import pyplot as plt

class UNIDADES():
    T_C = "ºC"
    T_K = "K"
    P_PA = "Pa"
    P_KPA = "kPa"
    L_KM = "km"
    L_M = "m"
    L_DM = "dm"
    L_CM = "cm"
    L_MM = "mm"
    L_INCH = "inch"
    A_M2 = "m2"
    PM_KG_KMOL = "kg/kmol"
    J_MOL_K = "J/(mol·K)"
    PER_100 = "%"
    PER_1 = "%1"
    REL_KGW_KGDA = "kg_w/kg_da"
    VE_M3_KGDA = "m3/kg_da"
    DE_KG_M3 = "kg/m3"
    E_KJ_KGDA = "kJ/kg_da"
    E_KJ_KGW = "kJ/kg_w"
    E_KJ_KG = "kJ/kg"
    E_KJ_KGW_C = "KJ/(kg·ºC)"
    FLUJO_KGDA_S = "kg_da/s"
    FLUJO_KGW_S = "kg_w/s"
    FLUJO_M3_S = "m3/s"
    FLUJO_M3_H = "m3/h"
    FLUJO_L_S = "l/s"
    POT_KW = "kW"
    POT_W = "W"


class CTES():
    # Presión barométrica estándar a nivel del mar
    Pstd0m = (101.325,UNIDADES.P_KPA)
    # Temperatura estándar a nivel del mar
    Tstd0m = (15,UNIDADES.T_C)
    # Peso molecular aire seco
    PM_DRYAIR = (28.966,UNIDADES.PM_KG_KMOL)
    # Peso molecular agua
    PM_WATER = (18.015268,UNIDADES.PM_KG_KMOL)
    # Constante universal de los gases ideales
    R =  (8.314472,UNIDADES.J_MOL_K)
    # Constante universal gas ideal para aire seco
    Rda = (1000*R[0]/PM_DRYAIR[0],UNIDADES.J_MOL_K)
    # Constante universal gas ideal para agua
    Rw = (1000*R[0]/PM_WATER[0],UNIDADES.J_MOL_K)
    # Calor específico del agua liquida a 25ºC Cp
    Cpw = (4186,UNIDADES.E_KJ_KGW_C)

class ATMOSFERA_ESTANDAR():
    def __init__(self,altura):
        self.cu = CONVERSOR_UNIDADES()
        self.setAltura(altura)

    # Altura debe ser una tupla con la unidad. Ej: (20,UNIDADES.L_M)
    def altura(self):
        return self.__altura

    #Presión barométrica de una atmósfera estándar a una altura dada
    def presion(self):
        return (AE_CTES.Pstd0m[0]*\
                (1-2.25577*0.00001*self.__altura[0])**5.2559,UNIDADES.P_KPA)

    #Temperatura de atmósfera estándar a una determinada altura
    def temperatura(self):
        return (AE_CTES.Tstd0m[0]-0.0065*self.__altura[0],UNIDADES.T_C)

    # Altura debe ser una tupla con la unidad. Ej: (20,UNIDADES.L_M)
    def setAltura(self,altura):
        ta = self.cu.longitud(altura,UNIDADES.L_M)
        if ta:
            self.__altura = ta
            return ta
        else:
            return None

class CONVERSOR_UNIDADES():

    def temperatura(self,valor,ud_destino):
        if (type(valor)==tuple):
            u1 = valor[1].casefold()
            u2 = ud_destino.casefold()
            if (u1==u2):
                return valor
            elif (u1==UNIDADES.T_C.casefold() and \
                  u2==UNIDADES.T_K.casefold()):
                return (273.15+valor[0],UNIDADES.T_K)
            elif (u1==UNIDADES.T_K.casefold() and \
                  u2==UNIDADES.T_C.casefold()):
                return (valor[0]-273.15,UNIDADES.T_C)
            else:
                print("Error, no se han introducido unidades soportadas")
                return None
        else:
            print("Error, no se ha introducido el valor como tupla")
            return None

    def presion(self,valor,ud_destino):
        if (type(valor)==tuple):
            u1 = valor[1].casefold()
            u2 = ud_destino.casefold()
            if (u1==u2):
                return valor
            elif (u1==UNIDADES.P_PA.casefold() and \
                  u2==UNIDADES.P_KPA.casefold()):
                return (0.001*valor[0],UNIDADES.P_KPA)
            elif (u1==UNIDADES.P_KPA.casefold() and \
                  u2==UNIDADES.P_PA.casefold()):
                return (1000*valor[0],UNIDADES.P_PA)
            else:
                print("Error, no se han introducido unidades soportadas")
                return None
        else:
            print("Error, no se ha introducido el valor como tupla")
            return None

    def porcentaje(self,valor,ud_destino):
        if (type(valor)==tuple):
            u1 = valor[1].casefold()
            u2 = ud_destino.casefold()
            if (u1==u2):
                return valor
            elif (u1==UNIDADES.PER_100.casefold() and \
                  u2==UNIDADES.PER_1.casefold()):
                return (0.01*valor[0],UNIDADES.PER_1)
            elif (u1==UNIDADES.PER_1.casefold() and \
                  u2==UNIDADES.PER_100.casefold()):
                return (100*valor[0],UNIDADES.PER_100)
            else:
                print("Error, no se han introducido unidades soportadas")
                return None
        else:
            print("Error, no se ha introducido el valor como tupla")
            return None

    def relacion_masica(self,valor,ud_destino):
        if (type(valor)==tuple):
            u1 = valor[1].casefold()
            u2 = ud_destino.casefold()
            if (u1==u2):
                return valor
            else:
                print("Error, no se han introducido unidades soportadas")
                return None
        else:
            print("Error, no se ha introducido el valor como tupla")
            return None

    def potencia(self,valor,ud_destino):
        if (type(valor)==tuple):
            u1 = valor[1].casefold()
            u2 = ud_destino.casefold()
            if (u1==u2):
                return valor
            elif(u1==UNIDADES.POT_KW.casefold() and \
                 u2==UNIDADES.POT_W.casefold()):
                return (valor[0]*1000,UNIDADES.POT_W)
            elif(u1==UNIDADES.POT_W.casefold() and \
                 u2==UNIDADES.POT_KW.casefold()):
                return (valor[0]*0.001,UNIDADES.POT_KW)
            else:
                print("Error, no se han introducido unidades soportadas")
                return None
        else:
            print("Error, no se ha introducido el valor como tupla")
            return None

    def densidad(self,valor,ud_destino):
        if (type(valor)==tuple):
            u1 = valor[1].casefold()
            u2 = ud_destino.casefold()
            if (u1==u2):
                return valor
            else:
                print("Error, no se han introducido unidades soportadas")
                return None
        else:
            print("Error, no se ha introducido el valor como tupla")
            return None

    def caudal(self,valor,ud_destino):
        if (type(valor)==tuple):
            u1 = valor[1].casefold()
            u2 = ud_destino.casefold()
            if (u1==u2):
                return valor
            else:
                print("Error, no se han introducido unidades soportadas")
                return None
        else:
            print("Error, no se ha introducido el valor como tupla")
            return None

    def area(self,valor,ud_destino):
        if (type(valor)==tuple):
            u1 = valor[1].casefold()
            u2 = ud_destino.casefold()
            if (u1==u2):
                return valor
            else:
                print("Error, no se han introducido unidades soportadas")
                return None
        else:
            print("Error, no se ha introducido el valor como tupla")
            return None

    def entalpia(self,valor,ud_destino):
        if (type(valor)==tuple):
            u1 = valor[1].casefold()
            u2 = ud_destino.casefold()
            if (u1==u2):
                return valor
            else:
                print("Error, no se han introducido unidades soportadas")
                return None
        else:
            print("Error, no se ha introducido el valor como tupla")
            return None

    def volumenespecifico(self,valor,ud_destino):
        if (type(valor)==tuple):
            u1 = valor[1].casefold()
            u2 = ud_destino.casefold()
            if (u1==u2):
                return valor
            else:
                print("Error, no se han introducido unidades soportadas")
                return None
        else:
            print("Error, no se ha introducido el valor como tupla")
            return None

    def relacion_masica(self,valor,ud_destino):
        if (type(valor)==tuple):
            u1 = valor[1].casefold()
            u2 = ud_destino.casefold()
            if (u1==u2):
                return valor
            else:
                print("Error, no se han introducido unidades soportadas")
                return None
        else:
            print("Error, no se ha introducido el valor como tupla")
            return None

    def longitud(self,valor,ud_destino):
        if (type(valor)==tuple):
            u1 = valor[1].casefold()
            u2 = ud_destino.casefold()
            if (u1==u2):
                return valor
            elif (u1==UNIDADES.L_KM.casefold() and \
                    u2==UNIDADES.L_M.casefold()):
                return (valor[0]*1000,UNIDADES.L_M)
            elif (u1==UNIDADES.L_KM.casefold() and \
                    u2==UNIDADES.L_DM.casefold()):
                return (valor[0]*10000,UNIDADES.L_DM)
            elif (u1==UNIDADES.L_KM.casefold() and \
                    u2==UNIDADES.L_CM.casefold()):
                return (valor[0]*100000,UNIDADES.L_CM)
            elif (u1==UNIDADES.L_KM.casefold() and \
                    u2==UNIDADES.L_MM.casefold()):
                return (valor[0]*1000000,UNIDADES.L_MM)
            elif (u1==UNIDADES.L_M.casefold() and \
                    u2==UNIDADES.L_KM.casefold()):
                return (valor[0]*0.001,UNIDADES.L_KM)
            elif (u1==UNIDADES.L_M.casefold() and \
                    u2==UNIDADES.L_DM.casefold()):
                return (valor[0]*10,UNIDADES.L_DM)
            elif (u1==UNIDADES.L_M.casefold() and \
                    u2==UNIDADES.L_CM.casefold()):
                return (valor[0]*100,UNIDADES.L_CM)
            elif (u1==UNIDADES.L_M.casefold() and \
                    u2==UNIDADES.L_MM.casefold()):
                return (valor[0]*1000,UNIDADES.L_MM)
            elif (u1==UNIDADES.L_M.casefold() and \
                    u2==UNIDADES.L_INCH.casefold()):
                return (valor[0]*39.3701,UNIDADES.L_INCH)
            elif (u1==UNIDADES.L_DM.casefold() and \
                    u2==UNIDADES.L_KM.casefold()):
                return (valor[0]*0.0001,UNIDADES.L_KM)
            elif (u1==UNIDADES.L_DM.casefold() and \
                    u2==UNIDADES.L_M.casefold()):
                return (valor[0]*0.1,UNIDADES.L_M)
            elif (u1==UNIDADES.L_DM.casefold() and \
                    u2==UNIDADES.L_CM.casefold()):
                return (valor[0]*10,UNIDADES.L_CM)
            elif (u1==UNIDADES.L_DM.casefold() and \
                    u2==UNIDADES.L_MM.casefold()):
                return (valor[0]*100,UNIDADES.L_MM)
            elif (u1==UNIDADES.L_CM.casefold() and \
                    u2==UNIDADES.L_KM.casefold()):
                return (valor[0]*0.00001,UNIDADES.L_KM)
            elif (u1==UNIDADES.L_CM.casefold() and \
                    u2==UNIDADES.L_M.casefold()):
                return (valor[0]*0.01,UNIDADES.L_M)
            elif (u1==UNIDADES.L_CM.casefold() and \
                    u2==UNIDADES.L_DM.casefold()):
                return (valor[0]*0.1,UNIDADES.L_DM)
            elif (u1==UNIDADES.L_CM.casefold() and \
                    u2==UNIDADES.L_MM.casefold()):
                return (valor[0]*10,UNIDADES.L_MM)
            elif (u1==UNIDADES.L_MM.casefold() and \
                    u2==UNIDADES.L_KM.casefold()):
                return (valor[0]*0.000001,UNIDADES.L_KM)
            elif (u1==UNIDADES.L_MM.casefold() and \
                    u2==UNIDADES.L_M.casefold()):
                return (valor[0]*0.001,UNIDADES.L_M)
            elif (u1==UNIDADES.L_MM.casefold() and \
                    u2==UNIDADES.L_DM.casefold()):
                return (valor[0]*0.01,UNIDADES.L_DM)
            elif (u1==UNIDADES.L_MM.casefold() and \
                    u2==UNIDADES.L_CM.casefold()):
                return (valor[0]*0.1,UNIDADES.L_CM)
            elif (u1==UNIDADES.L_INCH.casefold() and \
                    u2==UNIDADES.L_M.casefold()):
                return (valor[0]/39.3701,UNIDADES.L_M)
            else:
                print("Error, no se han introducido unidades soportadas")
                return None
        else:
            print("Error, no se ha introducido el valor como tupla")
            return None

def water_h(temperatura):
    cun = CONVERSOR_UNIDADES()
    return (4.186*cun.temperatura(temperatura,UNIDADES.T_C)[0],\
            UNIDADES.E_KJ_KGW)

class AIRE_HUMEDO():
    """
    Ejemplo de inicialización:
        AIRE_HUMEDO(tseca=(30,"ºC"),presion=(101.325,"kPa"),humrel=(0.5,"%1"))

    Si no se especifican unidades, por defecto se tomarán ºC para temperaturas,
    kPA para presiones, %1 para humedad relativa y kg_w/kg_da para humedad
    absoluta
    """
    # tseca:    temperatura seca [ºC]
    # trocio:   temperatura de rocío (td en ASHRAE) [ºC]
    # presion:  presión barométrica [kPA]
    # pws:      presión de saturación del aire [kPA]
    # pw:       presión parcial de vapor de agua [kPA]
    # humrel:   humedad relativa [%1]
    # humespec: humedad específica [%1] - kg_w/kg
    # humabs:   humedad absoluta [kg_w/m3]
    # W:        ratio de humedad [kg_w/kg_da] - Humedad absoluta española
    # Ws:       ratio de saturación de humedad [kg_w/kg_da]
    # u:        grado de saturación [%1]
    # v:        volumen específico [m3/kg_da]
    # densidad: densidad [kg/m3]
    # h:        entalpía de la mezcla [kJ/kg]
    # ha:       entalpía del aire seco [kJ/kg_da]
    # hg:       entalpía del vapor de agua saturado [kJ/kg_w]
    # tbh:      temperatura de bulbo húmedo [ºC]
    # pwstbh:   presión de saturación del aire [kPA] a la temperatura de
    #           bulbo húmedo
    # Wstbh:    ratio de saturación de humedad a la temperatura de
    #           saturación [%1]

    cu = CONVERSOR_UNIDADES()

    def __init__(self,tseca=None,tbh=None,presion=CTES.Pstd0m,\
                 trocio=None,humrel=None,W=None, h=None, v=None):
        if type(tseca)==float or type(tseca)==int:
            tseca = (tseca,UNIDADES.T_C)
        if type(tbh)==float or type(tbh)==int:
            tbh = (tbh,UNIDADES.T_C)
        if type(trocio)==float or type(trocio)==int:
            trocio = (trocio,UNIDADES.T_C)
        if type(presion)==float or type(presion)==int:
            presion = (presion,UNIDADES.P_KPA)
        if type(humrel)==float or type(humrel)==int:
            humrel = (humrel,UNIDADES.PER_1)
        if type(W)==float or type(W)==int:
            W = (W,UNIDADES.REL_KGW_KGDA)
        if type(h)==float or type(h)==int:
            h = (h,UNIDADES.E_KJ_KGDA)
        if type(v)==float or type(v)==int:
            v = (v,UNIDADES.VE_M3_KGDA)
        self.setEstado(tseca,tbh,presion,trocio,humrel,W,h,v)

    # Calcula la presión de saturación del aire
    def _pws(temperatura):
        t = AIRE_HUMEDO.cu.temperatura(temperatura,UNIDADES.T_K)
        if (t):
            lnpws = None
            if (t[0]<(0+273.15) and t[0]>=(-100+273.15)):
                C1 = -5.6745359e3
                C2 = 6.3925247
                C3 = -9.6778430e-3
                C4 = 6.2215701e-7
                C5 = 2.0747825e-9
                C6 = -9.4840240e-13
                C7 = 4.1635019
                lnpws = C1/t[0]+C2+C3*t[0]+C4*(t[0])**2+C5*(t[0])**3+\
                        C6*(t[0])**4+C7*math.log(t[0])
            elif (t[0]>=(0+273.15) and (t[0]<=200+273.15)):
                C8 = -5.8002206e3
                C9 = 1.3914993
                C10 = -4.8640239e-2
                C11 = 4.1764768e-5
                C12 = -1.4452093e-8
                C13 = 6.5459673
                lnpws = C8/t[0]+C9+C10*t[0]+C11*(t[0])**2+C12*(t[0])**3+\
                        C13*math.log(t[0])
            else:
                print("Error, temperatura fuera del rango -100ºC a 200ºC")
            if (lnpws):
                return (0.001*math.exp(lnpws),UNIDADES.P_KPA)
        print("Error. No se ha introducido la temperatura como tupla"+\
                " con unidades válidas")
        return None

    # Calcula la presión parcial de vapor de agua
    def _pw(pws,humrel):
        return AIRE_HUMEDO.cu.presion((\
                AIRE_HUMEDO.cu.porcentaje(humrel,UNIDADES.PER_1)[0]*\
                    pws[0],pws[1]),UNIDADES.P_KPA)

    # Calcula el volumen específico
    def _v(t,p,W):
        t1 = AIRE_HUMEDO.cu.temperatura(t,UNIDADES.T_K)
        p1 = AIRE_HUMEDO.cu.presion(p,UNIDADES.P_KPA)
        W1 = AIRE_HUMEDO.cu.relacion_masica(W,UNIDADES.REL_KGW_KGDA)
        return (0.287042*t1[0]*(1+1.607858*W1[0])/p1[0],\
                UNIDADES.VE_M3_KGDA)

    def _densidad(v,W):
        v1 =  AIRE_HUMEDO.cu.volumenespecifico(v,UNIDADES.VE_M3_KGDA)[0]
        W1 = AIRE_HUMEDO.cu.relacion_masica(W,UNIDADES.REL_KGW_KGDA)[0]
        return ((1/v1)*(1+W1),UNIDADES.DE_KG_M3)

    def _humespec(W):
        W1 = AIRE_HUMEDO.cu.relacion_masica(W,UNIDADES.REL_KGW_KGDA)
        return (W1[0]/(1+W1[0]),UNIDADES.PER_1)

    # Calcula la entalpía del aire seco
    def _ha(t):
        return (1.006*AIRE_HUMEDO.cu.temperatura(t,UNIDADES.T_C)[0],\
                UNIDADES.E_KJ_KGDA)

    # Calcula la entalpía del vapor saturado
    def _hg(t):
        return (2501+1.86*AIRE_HUMEDO.cu.temperatura(t,UNIDADES.T_C)[0],
                UNIDADES.E_KJ_KGW)

    # Calcula la entalpía del aire húmedo
    def _h(t,W):
        return (1.006*AIRE_HUMEDO.cu.temperatura(t,UNIDADES.T_C)[0]+\
                AIRE_HUMEDO.cu.relacion_masica(W,UNIDADES.REL_KGW_KGDA)[0]*\
                  (2501+1.86*AIRE_HUMEDO.cu.temperatura(t,UNIDADES.T_C)[0]),\
                  UNIDADES.E_KJ_KGDA)

    def _tbh(t,W,p):
        t1 = AIRE_HUMEDO.cu.temperatura(t,UNIDADES.T_C)
        p1 = AIRE_HUMEDO.cu.presion(p,UNIDADES.P_KPA)
        W1 = AIRE_HUMEDO.cu.relacion_masica(W,UNIDADES.REL_KGW_KGDA)
        if(t1[0]>0):
            f = lambda tbh: W1[0] - ((2501-2.326*tbh)*\
                    (0.621945*AIRE_HUMEDO._pws((tbh,UNIDADES.T_C))[0]/\
                     (p1[0]-AIRE_HUMEDO._pws((tbh,UNIDADES.T_C))[0]))\
                    -1.006*(t1[0]-tbh))/(2501 + 1.86*t1[0]-4.186*tbh)
        else:
            f = lambda tbh: W1[0] - ((2830-0.24*tbh)*\
                    (0.621945*AIRE_HUMEDO._pws((tbh,UNIDADES.T_C))[0]/\
                     (p1[0]-AIRE_HUMEDO._pws((tbh,UNIDADES.T_C))[0]))\
                    -1.006*(t1[0]-tbh))/(2830 + 1.86*t1[0]-2.1*tbh)
        sol = fsolve(f,t1[0])
        return (sol[0],UNIDADES.T_C)

    def _trocio(t,p,humrel):
        pws = AIRE_HUMEDO._pws(t)
        pw = AIRE_HUMEDO._pw(pws,humrel)[0]
        t1 = AIRE_HUMEDO.cu.temperatura(t,UNIDADES.T_C)[0]
        f = lambda td: pw - AIRE_HUMEDO._pws((td,UNIDADES.T_C))[0]
        return (fsolve(f,t1)[0],UNIDADES.T_C)

    def __eq__(self,nestado):
        if (self.tseca[0]==nestado.tseca[0] and \
            self.tseca[1]==nestado.tseca[1] and \
            self.presion[0]==nestado.presion[0] and \
            self.presion[1]==nestado.presion[1] and \
            ((self.trocio[0]==nestado.trocio[0] and \
              self.trocio[1]==nestado.trocio[1]) or \
             (self.humrel[0]==nestado.humrel[0] and \
              self.humrel[1]==nestado.humrel[1]) or \
             (self.tbh[0]==nestado.tbh[0] and \
             self.tbh[1]==nestado.tbh[1]))):
            return True
        else:
            return False

    def __ne__(self,nestado):
        return not self.__eq__(nestado)

    def _hhr_(tseca,humrel,presion):
        t = tseca[0]
        hr = humrel[0]
        Ws = 0.621945*AIRE_HUMEDO._pws((t,UNIDADES.T_C))[0]/(presion[0]-AIRE_HUMEDO._pws((t,UNIDADES.T_C))[0])
        W = None
        if hr==0:
            return 1.006*t
        elif hr==1:
            W = Ws
        else:
            W = Ws*hr/(1+(1-hr)*Ws/0.621945)
        return 1.006*t+W*(2501+1.86*t)

    # Establece un estado psicrométrico de aire húmedo
    def setEstado(self,tseca=None, tbh=None, presion=None,\
                  trocio=None, humrel=None, W=None , h=None, v=None):
        tcu = self.__class__.cu
        fail = False
        if ((type(tseca)==tuple and type(presion)==tuple and not h \
                and not v) and \
            ((type(tbh)==tuple and not(trocio) and not(humrel) and not(W)) or \
             (type(trocio)==tuple and not(tbh) and not(humrel) and not(W)) or \
             (type(humrel)==tuple and not(trocio) and not(tbh) and not(W)) or \
             (type(W)==tuple and not(tbh) and not(trocio) and not(humrel))
             )):
            self.tseca = tcu.temperatura(tseca,UNIDADES.T_C)
            self.presion = tcu.presion(presion,UNIDADES.P_KPA)
            if(humrel):
                self.humrel = tcu.porcentaje(humrel,UNIDADES.PER_1)
                self.pws = self.__class__._pws(self.tseca)
                self.pw = self.__class__._pw(self.pws,self.humrel)
                self.W = (0.621945*self.pw[0]/(self.presion[0]-self.pws[0]),\
                        UNIDADES.REL_KGW_KGDA)
                self.Ws = (0.621945*self.pws[0]/(self.presion[0]-self.pws[0])\
                        ,UNIDADES.REL_KGW_KGDA)
                self.humespec = self.__class__._humespec(self.W)
                self.u = (self.W[0]/self.Ws[0],UNIDADES.PER_1)
                self.v = self.__class__._v(self.tseca,self.presion,self.W)
                self.densidad = self.__class__._densidad(\
                        self.v,self.W)
                self.humabs = (self.humespec[0]/self.densidad[0],'kg_w/m3')
                self.ha = self.__class__._ha(self.tseca)
                self.hg = self.__class__._hg(self.tseca)
                self.h = self.__class__._h(self.tseca,self.W)
                self.tbh = self.__class__._tbh(self.tseca,self.W,self.presion)
                self.pwstbh = self.__class__._pws(self.tbh)
                self.Wstbh = (0.621945*self.pwstbh[0]/\
                        (self.presion[0]-self.pwstbh[0]),UNIDADES.PER_1)
                self.trocio = self.__class__._trocio(self.tseca,\
                        self.presion,self.humrel)
            elif(trocio):
                self.trocio = AIRE_HUMEDO.cu.temperatura(trocio,UNIDADES.T_C)
                self.pws = self.__class__._pws(self.tseca)
                self.pw = self.__class__._pws(self.trocio)
                self.humrel = (self.pw[0]/self.pws[0],UNIDADES.PER_1)
                self.W = (0.621945*self.pw[0]/(self.presion[0]-self.pws[0]),\
                        UNIDADES.REL_KGW_KGDA)
                self.Ws = (0.621945*self.pws[0]/(self.presion[0]-self.pws[0])\
                        ,UNIDADES.REL_KGW_KGDA)
                self.humespec = self.__class__._humespec(self.W)
                self.u = (self.W[0]/self.Ws[0],UNIDADES.PER_1)
                self.v = self.__class__._v(self.tseca,self.presion,self.W)
                self.densidad = self.__class__._densidad(\
                        self.v,self.W)
                self.humabs = (self.humespec[0]/self.densidad[0],'kg_w/m3')
                self.ha = self.__class__._ha(self.tseca)
                self.hg = self.__class__._hg(self.tseca)
                self.h = self.__class__._h(self.tseca,self.W)
                self.tbh = self.__class__._tbh(self.tseca,self.W,self.presion)
                self.pwstbh = self.__class__._pws(self.tbh)
                self.Wstbh = (0.621945*self.pwstbh[0]/\
                        (self.presion[0]-self.pwstbh[0]),UNIDADES.PER_1)
            elif(tbh):
                self.tbh = AIRE_HUMEDO.cu.temperatura(tbh,UNIDADES.T_C)
                self.pwstbh = self.__class__._pws(self.tbh)
                self.Wstbh = (0.621945*self.pwstbh[0]/\
                        (self.presion[0]-self.pwstbh[0]),UNIDADES.PER_1)
                if (tseca[0]>=0):
                    self.W = (((2501-2.326*self.tbh[0])*self.Wstbh[0]-\
                           1.006*(self.tseca[0]-self.tbh[0])) / \
                           (2501+1.86*self.tseca[0]-4.186*self.tbh[0]),\
                           UNIDADES.REL_KGW_KGDA)
                else:
                    self.W = (((2830-0.24*self.tbh[0])*self.Wstbh[0]-\
                            1.006*(self.tseca[0]-self.tbh[0]))/\
                            (2830+1.86*self.tseca[0]-2.1*self.tbh[0]),\
                            UNIDADES.REL_KGW_KGDA)
                self.humespec = self.__class__._humespec(self.W)
                self.pws = self.__class__._pws(self.tseca)
                self.Ws = (0.621945*self.pws[0]/(self.presion[0]-self.pws[0])\
                        ,UNIDADES.REL_KGW_KGDA)
                self.u = (self.W[0]/self.Ws[0],UNIDADES.PER_1)

                #self.humrel = (self.u[0]*(0.621945+self.Ws[0])/\
                #        (0.621945+self.Ws[0]*self.u[0]),UNIDADES.PER_1)
                self.humrel = ((self.presion[0]/self.pws[0])/\
                        (1+0.621945/self.W[0]),UNIDADES.PER_1)
                self.v = self.__class__._v(self.tseca,self.presion,self.W)
                self.densidad = self.__class__._densidad(\
                        self.v,self.W)
                self.humabs = (self.humespec[0]/self.densidad[0],'kg_w/m3')
                self.ha = self.__class__._ha(self.tseca)
                self.hg = self.__class__._hg(self.tseca)
                self.h = self.__class__._h(self.tseca,self.W)
                self.pw = (self.presion[0]*self.W[0]/(0.621945+self.W[0]),
                        UNIDADES.P_KPA)
                alfa = math.log(self.pw[0])
                self.trocio = self.__class__._trocio(self.tseca,\
                        self.presion,self.humrel)
                #if (self.tseca[0] >=0) and (self.tseca[0] <= 93):
                #    self.trocio = (6.54+14.526*alfa+0.7389*(alfa**2)+\
                #             0.09486*(alfa**3)+0.4569*(alfa**4),UNIDADES.T_C)
                #elif (self.tseca[0] < 0):
                #    self.trocio = (6.09 + 12608*alfa + 0.4959*(alfa**2),\
                #            UNIDADES.T_C)
                #else:
                #    print("Advertencia -> Temperatura fuera de rango:" +\
                #          " -273.15 ºC a 93 ºC")
                #ALGO PASA QUE NO CUADRA, ESTÁ PRÓXIMO PERO NO COINCIDE
                #REVISAR FÓRMULAS
                #self.pw = ((self.presion[0]*self.W[0])/\
                #        (0.621945+self.W[0]),UNIDADES.P_KPA)
                #self.pw = ((self.presion[0]*self.W[0])/\
                #        (self.W[0]+0.621945),UNIDADES.P_KPA)
                #self.humrel = (self.u[0]/(1-(1-self.u[0])*\
                #        (self.pw[0]/self.presion[0])),\
                #        UNIDADES.PER_1)
            elif(W):
                self.pws = self.__class__._pws(self.tseca)
                self.W = tcu.relacion_masica(W,UNIDADES.REL_KGW_KGDA)
                self.Ws = (0.621945*self.pws[0]/(self.presion[0]-self.pws[0])\
                        ,UNIDADES.REL_KGW_KGDA)
                self.pw = (self.presion[0]*self.W[0]/(0.621945+self.W[0]),
                        UNIDADES.P_KPA)
                self.humrel = (self.pw[0]/self.pws[0],UNIDADES.PER_1)
                self.humespec = self.__class__._humespec(self.W)
                self.u = (self.W[0]/self.Ws[0],UNIDADES.PER_1)
                self.v = self.__class__._v(self.tseca,self.presion,self.W)
                self.densidad = self.__class__._densidad(\
                        self.v,self.W)
                self.humabs = (self.humespec[0]/self.densidad[0],'kg_w/m3')
                self.ha = self.__class__._ha(self.tseca)
                self.hg = self.__class__._hg(self.tseca)
                self.h = self.__class__._h(self.tseca,self.W)
                self.tbh = self.__class__._tbh(self.tseca,self.W,self.presion)
                self.pwstbh = self.__class__._pws(self.tbh)
                self.Wstbh = (0.621945*self.pwstbh[0]/\
                        (self.presion[0]-self.pwstbh[0]),UNIDADES.PER_1)
                self.trocio = self.__class__._trocio(self.tseca,\
                        self.presion,self.humrel)
            #Comprobación de errores
            if self.tseca[0]<=-273.15:
                raise ValueError("Error, temperatura inferior al cero absoluto = ")
            if self.tseca[0]>=100:
                raise ValueError("Error, temperatura fuera de rango (<=100ºC) = "+str(self.tseca))
            if self.presion[0]<=0:
                raise ValueError("Error, presión negativa = "+str(self.presion))
            if self.humrel[0]<0 or self.humrel[0]>1:
                raise ValueError("Error, humedad relativa fuera de rango = "+str(self.humrel))
            if self.W[0]<0 or self.W[0]>1:
                raise ValueError("Error, humedad absoluta errónea = "+str(self.W))
        elif type(h)==tuple and type(presion)==tuple and not v:
            self.h = tcu.entalpia(h,UNIDADES.E_KJ_KGDA)
            self.presion = tcu.presion(presion,UNIDADES.P_KPA)
            if (type(tseca)==tuple and \
                not( humrel and W and tbh and trocio )):
                self.tseca = tcu.temperatura(tseca,UNIDADES.T_C)
                self.W = ((self.h[0]-1.006*self.tseca[0])/\
                        (2501+1.86*self.tseca[0]),UNIDADES.REL_KGW_KGDA)
                self.pws = self.__class__._pws(self.tseca)
                self.Ws = (0.621945*self.pws[0]/(self.presion[0]-self.pws[0])\
                        ,UNIDADES.REL_KGW_KGDA)
                self.pw = (self.presion[0]*self.W[0]/(0.621945+self.W[0]),
                        UNIDADES.P_KPA)
                self.humrel = (self.pw[0]/self.pws[0],UNIDADES.PER_1)
                self.humespec = self.__class__._humespec(self.W)
                self.u = (self.W[0]/self.Ws[0],UNIDADES.PER_1)
                self.v = self.__class__._v(self.tseca,self.presion,self.W)
                self.densidad = self.__class__._densidad(\
                        self.v,self.W)
                self.humabs = (self.humespec[0]/self.densidad[0],'kg_w/m3')
                self.ha = self.__class__._ha(self.tseca)
                self.hg = self.__class__._hg(self.tseca)
                self.h = self.__class__._h(self.tseca,self.W)
                self.tbh = self.__class__._tbh(self.tseca,self.W,self.presion)
                self.pwstbh = self.__class__._pws(self.tbh)
                self.Wstbh = (0.621945*self.pwstbh[0]/\
                        (self.presion[0]-self.pwstbh[0]),UNIDADES.PER_1)
                self.trocio = self.__class__._trocio(self.tseca,\
                        self.presion,self.humrel)
            elif (type(W)==tuple and \
                not( humrel and tseca and tbh and trocio )):
                self.W = tcu.relacion_masica(W,UNIDADES.REL_KGW_KGDA)
                self.tseca = ((self.h[0]-self.W[0]*2501)/\
                        (1.006+self.W[0]*1.86),UNIDADES.T_C)
                self.pws = self.__class__._pws(self.tseca)
                self.Ws = (0.621945*self.pws[0]/(self.presion[0]-self.pws[0])\
                        ,UNIDADES.REL_KGW_KGDA)
                self.pw = (self.presion[0]*self.W[0]/(0.621945+self.W[0]),
                        UNIDADES.P_KPA)
                self.humrel = (self.pw[0]/self.pws[0],UNIDADES.PER_1)
                self.humespec = self.__class__._humespec(self.W)
                self.u = (self.W[0]/self.Ws[0],UNIDADES.PER_1)
                self.v = self.__class__._v(self.tseca,self.presion,self.W)
                self.densidad = self.__class__._densidad(\
                        self.v,self.W)
                self.humabs = (self.humespec[0]/self.densidad[0],'kg_w/m3')
                self.ha = self.__class__._ha(self.tseca)
                self.hg = self.__class__._hg(self.tseca)
                self.h = self.__class__._h(self.tseca,self.W)
                self.tbh = self.__class__._tbh(self.tseca,self.W,self.presion)
                self.pwstbh = self.__class__._pws(self.tbh)
                self.Wstbh = (0.621945*self.pwstbh[0]/\
                        (self.presion[0]-self.pwstbh[0]),UNIDADES.PER_1)
                self.trocio = self.__class__._trocio(self.tseca,\
                        self.presion,self.humrel)
            elif (type(humrel)==tuple and \
                not( W and tseca and tbh and trocio )):
                self.humrel = tcu.porcentaje(humrel,UNIDADES.PER_1)
                if self.humrel[0]==0:
                    self.tseca = (self.h[0]/1.006,UNIDADES.T_C)
                    self.W = (0,UNIDADES.REL_KGW_KGDA)
                elif self.humrel[0]<=1 and self.humrel[0]>0:
                    f = lambda tin: self.h[0] - self.__class__._hhr_((tin,UNIDADES.T_C),self.humrel,self.presion)
                    self.tseca = (fsolve(f,0)[0],UNIDADES.T_C)
                    self.W = ((self.h[0]-1.006)/(2501+1.86*self.tseca[0]),\
                            UNIDADES.REL_KGW_KGDA)
                else:
                    raise ValueError('La humedad relativa tiene que estar entre el 0 y el 100% (0-1 %1)')
                self.pws = self.__class__._pws(self.tseca)
                self.Ws = (0.621945*self.pws[0]/(self.presion[0]-self.pws[0])\
                        ,UNIDADES.REL_KGW_KGDA)
                self.pw = (self.presion[0]*self.W[0]/(0.621945+self.W[0]),
                        UNIDADES.P_KPA)
                self.humespec = self.__class__._humespec(self.W)
                self.u = (self.W[0]/self.Ws[0],UNIDADES.PER_1)
                self.v = self.__class__._v(self.tseca,self.presion,self.W)
                self.densidad = self.__class__._densidad(\
                        self.v,self.W)
                self.humabs = (self.humespec[0]/self.densidad[0],'kg_w/m3')
                self.ha = self.__class__._ha(self.tseca)
                self.hg = self.__class__._hg(self.tseca)
                self.tbh = self.__class__._tbh(self.tseca,self.W,self.presion)
                self.pwstbh = self.__class__._pws(self.tbh)
                self.Wstbh = (0.621945*self.pwstbh[0]/\
                        (self.presion[0]-self.pwstbh[0]),UNIDADES.PER_1)
                if self.humrel[0]==0:
                    print("Advertencia, no existe temperatura de rocío para este punto")
                else:
                    self.trocio = self.__class__._trocio(self.tseca,\
                        self.presion,self.humrel)
            else:
                fail = True
        elif type(v)==tuple and type(presion)==tuple and not h:
            self.presion = tcu.presion(presion,UNIDADES.P_KPA)
            self.v = tcu.volumenespecifico(v,UNIDADES.VE_M3_KGDA)
            if (type(tseca)==tuple and \
                not( humrel and W and tbh and trocio)):
                self.tseca = tcu.temperatura(tseca,UNIDADES.T_C)
                t1 = tcu.temperatura(tseca,UNIDADES.T_K)[0]
                self.W = (((self.presion[0]*self.v[0])/(0.287042*t1)-1)/\
                        1.607858,UNIDADES.REL_KGW_KGDA)
                self.pws = self.__class__._pws(self.tseca)
                self.Ws = (0.621945*self.pws[0]/(self.presion[0]-self.pws[0])\
                        ,UNIDADES.REL_KGW_KGDA)
                self.pw = (self.presion[0]*self.W[0]/(0.621945+self.W[0]),
                        UNIDADES.P_KPA)
                self.humrel = (self.pw[0]/self.pws[0],UNIDADES.PER_1)
                self.humespec = self.__class__._humespec(self.W)
                self.u = (self.W[0]/self.Ws[0],UNIDADES.PER_1)
                self.densidad = self.__class__._densidad(\
                        self.v,self.W)
                self.humabs = (self.humespec[0]/self.densidad[0],'kg_w/m3')
                self.ha = self.__class__._ha(self.tseca)
                self.hg = self.__class__._hg(self.tseca)
                self.h = self.__class__._h(self.tseca,self.W)
                self.tbh = self.__class__._tbh(self.tseca,self.W,self.presion)
                self.pwstbh = self.__class__._pws(self.tbh)
                self.Wstbh = (0.621945*self.pwstbh[0]/\
                        (self.presion[0]-self.pwstbh[0]),UNIDADES.PER_1)
                self.trocio = self.__class__._trocio(self.tseca,\
                        self.presion,self.humrel)
            elif (type(W)==tuple and \
                not( humrel and tseca and tbh and trocio )):
                self.W = tcu.relacion_masica(W,UNIDADES.REL_KGW_KGDA)
                self.tseca=((self.presion[0]*self.v[0])/\
                        (0.287042*(1.607858*self.W[0]+1))-273.15,UNIDADES.T_C)
                self.pws = self.__class__._pws(self.tseca)
                self.Ws = (0.621945*self.pws[0]/(self.presion[0]-self.pws[0])\
                        ,UNIDADES.REL_KGW_KGDA)
                self.pw = (self.presion[0]*self.W[0]/(0.621945+self.W[0]),
                        UNIDADES.P_KPA)
                self.humrel = (self.pw[0]/self.pws[0],UNIDADES.PER_1)
                self.humespec = self.__class__._humespec(self.W)
                self.u = (self.W[0]/self.Ws[0],UNIDADES.PER_1)
                self.densidad = self.__class__._densidad(\
                        self.v,self.W)
                self.humabs = (self.humespec[0]/self.densidad[0],'kg_w/m3')
                self.ha = self.__class__._ha(self.tseca)
                self.hg = self.__class__._hg(self.tseca)
                self.h = self.__class__._h(self.tseca,self.W)
                self.tbh = self.__class__._tbh(self.tseca,self.W,self.presion)
                self.pwstbh = self.__class__._pws(self.tbh)
                self.Wstbh = (0.621945*self.pwstbh[0]/\
                        (self.presion[0]-self.pwstbh[0]),UNIDADES.PER_1)
                self.trocio = self.__class__._trocio(self.tseca,\
                        self.presion,self.humrel)
            else:
                fail = True
        else:
            fail = True
        # Lanza error si no se han suministrado las ternas necesarias para
        # el constructor
        if fail:
            msg = "Error, no se han introducido correctamente las" +\
                    " siguientes ternas: (tseca,thumeda,presion), (tseca," +\
                    "trocio,presion), (tseca,humrel,presion), "\
                    +"(tseca,W,presion), (tseca,presion,h), (presion,h,W), "+\
                    "(presion,h,humrel), (tseca,presion,v), (presion,v,W)"
            print(msg)
            raise ValueError(msg)

    def __str__(self):
        st1 = "- Temperatura seca: " + str(self.tseca[0]) +' '+self.tseca[1]+\
                "\n" +\
              "- Presión: " + str(self.presion[0]) + ' ' + self.presion[1]+\
                "\n" +\
              "- Temperatura bulbo húmedo: " + str(self.tbh[0]) + ' ' +\
                self.tbh[1] + "\n" +\
              "- Temperatura de rocío: " + str(self.trocio[0]) + ' ' +\
                self.trocio[1] + "\n" +\
              "- Presión parcial vapor de agua: " +str(self.pw[0]) + ' ' +\
                self.pw[1] + "\n" +\
              "- Presión de saturación del aire: " +str(self.pws[0]) + ' ' +\
                self.pws[1] + "\n" +\
              "- Humedad relativa: " + str(self.humrel[0]) + ' ' + \
                self.humrel[1] + "\n" +\
              "- Humedad específica: " + str(self.humespec[0]) + ' ' + \
                self.humespec[1] + "\n" +\
              "- Humedad absoluta: " + str(self.humabs[0]) + ' ' + \
                self.humabs[1] + "\n" +\
              "- Ratio de humedad (humedad absoluta española): " + \
                str(self.W[0]) + ' ' + self.W[1] + "\n" +\
              "- Ratio de saturación de humedad: " + str(self.Ws[0]) + ' ' +\
                self.Ws[1] + "\n" +\
              "- Grado de saturación: " + str(self.u[0]) + ' ' + \
                self.u[1] + "\n" +\
              "- Volumen específico: " + str(self.v[0]) + ' ' + \
                self.v[1] + "\n" +\
              "- Densidad: " + str(self.densidad[0]) + ' ' + \
                self.densidad[1] + "\n" +\
              "- Entalpía mezcla: " + str(self.h[0]) +' '+self.h[1] + "\n" +\
              "- Entalpía aire seco: " + str(self.ha[0]) + ' ' + \
                self.ha[1] + "\n" +\
              "- Entalpía vapor de agua saturado: " + str(self.hg[0]) + ' ' +\
                self.hg[1] + "\n" +\
              "- Presión de saturación del aire a la temperatura de " +\
                "bulbo húmedo: " + str(self.pwstbh[0])+ ' ' + \
                self.pwstbh[1] + "\n" +\
              "- Ratio de saturación de humedad a la temperatura de " +\
              "saturación: " + str(self.Wstbh[0])+' '+self.Wstbh[1]
        return st1

    def muestra_estado(self):
        print(str(self))

class FLUJO():
    """Los caudales de entrada admiten las siguientes unidades:
        - kg_da/s (kg de aire seco por segundo)
        - m3/s (metros cúbicos por segundo de la mezcla)
        - m3/h (metros cúbicos por hora de la mezcla)
        - l/s (litros por segundo de la mezcla)
       Se inicializa como FLUJO(estado_psicrometrico,caudal). Ejemplo:
           FLUJO(AIRE_HUMEDO(tseca=(30,"ºC"),presion=(101.325,"kPa"),humrel=(0.5,"%1")),(5,'m3/s'))

        Si no se especifica unidad para el caudal, por defecto se interpreta
        que son m3/h
    """
    def __init__(self, aire_humedo, caudal):
        if type(caudal)==float or type(caudal)==int:
            caudal = (caudal,UNIDADES.FLUJO_M3_H)
        self.estado = aire_humedo
        unidad = caudal[1].casefold()
        if unidad == UNIDADES.FLUJO_KGDA_S:
            self.caudal = (caudal[0],UNIDADES.FLUJO_KGDA_S)
        elif unidad == UNIDADES.FLUJO_M3_S:
            self.caudal = (caudal[0]/self.estado.v[0],UNIDADES.FLUJO_KGDA_S)
        elif unidad == UNIDADES.FLUJO_M3_H:
            self.caudal = (caudal[0]/(self.estado.v[0]*3600),\
                    UNIDADES.FLUJO_KGDA_S)
        elif unidad == "l/s":
            self.caudal = (caudal[0]/(self.estado.v[0]*1000),\
                    UNIDADES.FLUJO_KGDA_S)

    def stream_caudal_vol(self):
        return (self.caudal[0]*self.estado.v[0]*3600,UNIDADES.FLUJO_M3_H)

    def __str__(self):
        he1 = self.stream_h()
        st1 = "**FLUJO**\n" + \
              "* CAUDAL FLUJO: " + str(self.caudal[0])+ ' ' +self.caudal[1] +\
                "\n" + \
              "* ENTALPÍA FLUJO: " + str(he1[0]) + ' '+ he1[1] + "\n" + \
              str(self.estado)
        return st1

    def __add__(self,flujo):
        mda1 = self.caudal[0]
        mda2 = flujo.caudal[0]
        mda3 = mda1 + mda2
        W3 = (flujo.estado.W[0]+self.estado.W[0]*(mda1/mda2))/(1 + mda1/mda2)
        h3 = (self.stream_h()[0]+flujo.stream_h()[0])/mda3
        tseca3 = ((h3 - 2501*W3)/(1.006+1.86*W3),UNIDADES.T_C)
        p3 = None
        W3 = (W3,UNIDADES.REL_KGW_KGDA)
        if (self.estado.presion[0] == flujo.estado.presion[0]):
            p3 = self.estado.presion
        if p3:
            return FLUJO(AIRE_HUMEDO(tseca=tseca3, \
                                     presion=p3, \
                                     W = W3),\
                                     (mda3,UNIDADES.FLUJO_KGDA_S))
        else:
            print("Advertencia, no se ha implementado mezcla a diferentes presiones")
            return None

    def __radd__(self,flujo):
        return self.__add__(flujo)

    def __sub__(self,flujo):
        mda1 = self.caudal[0]
        mda2 = -1*flujo.caudal[0]
        mda3 = mda1 + mda2
        W3 = (flujo.estado.W[0]+self.estado.W[0]*(mda1/mda2))/(1 + mda1/mda2)
        h3 = (self.stream_h()[0]-flujo.stream_h()[0])/mda3
        tseca3 = ((h3 - 2501*W3)/(1.006+1.86*W3),UNIDADES.T_C)
        p3 = None
        W3 = (W3,UNIDADES.REL_KGW_KGDA)
        if (self.estado.presion[0] == flujo.estado.presion[0]):
            p3 = self.estado.presion
        if p3:
            return FLUJO(AIRE_HUMEDO(tseca=tseca3, \
                                     presion=p3, \
                                     W = W3),\
                                     (mda3,UNIDADES.FLUJO_KGDA_S))
        else:
            print("Advertencia, no se ha implementado mezcla a diferentes presiones")
            return None

    def __rsub__(self,flujo):
        mda1 = -1*self.caudal[0]
        mda2 = flujo.caudal[0]
        mda3 = mda1 + mda2
        W3 = (flujo.estado.W[0]+self.estado.W[0]*(mda1/mda2))/(1 + mda1/mda2)
        h3 = (-1*self.stream_h()[0]-flujo.stream_h()[0])/mda3
        tseca3 = ((h3 - 2501*W3)/(1.006+1.86*W3),UNIDADES.T_C)
        p3 = None
        W3 = (W3,UNIDADES.REL_KGW_KGDA)
        if (self.estado.presion[0] == flujo.estado.presion[0]):
            p3 = self.estado.presion
        if p3:
            return FLUJO(AIRE_HUMEDO(tseca=tseca3, \
                                     presion=p3, \
                                     W = W3),\
                                     (mda3,UNIDADES.FLUJO_KGDA_S))
        else:
            print("Advertencia, no se ha implementado mezcla a diferentes presiones")
            return None

    def __mul__(self, factor):
        return FLUJO(copy.deepcopy(self.estado),\
                (self.caudal[0]*factor,self.caudal[1]))

    def __pos__(self):
        return FLUJO(copy.deepcopy(self.estado),\
                (+self.caudal[0],self.caudal[1]))

    def __neg__(self):
        return FLUJO(copy.deepcopy(self.estado),\
                (-self.caudal[0],self.caudal[1]))

    def __truediv__(self, divisor):
        return FLUJO(copy.deepcopy(self.estado),\
                (self.caudal[0]/divisor,self.caudal[1]))

    def __floordiv__(self, divisor):
        return FLUJO(copy.deepcopy(self.estado),\
                (self.caudal[0]//divisor,self.caudal[1]))

    def __mod__(self, divisor):
        return FLUJO(copy.deepcopy(self.estado),\
                (self.caudal[0]%divisor,self.caudal[1]))

    def __rmul__(self, factor):
        return self.__mul__(factor)

    def __pow__(self, potencia):
        return FLUJO(copy.deepcopy(self.estado),\
                (self.caudal[0]**potencia,self.caudal[1]))

    def __abs__(self):
        return FLUJO(copy.deepcopy(self.estado),\
                (abs(self.caudal[0]),self.caudal[1]))

    def __eq__(self, flujo):
        if (self.caudal[0]==flujo.caudal[0] and \
            self.caudal[1]==flujo.caudal[1] and \
            self.estado==flujo.estado):
            return True
        else:
            return False

    def __ne__(self,flujo):
        return not self.__eq__(flujo)

    def stream_h(self):
        """
        Devuelve la entalpía del flujo
        """
        return (self.estado.h[0] * self.caudal[0], UNIDADES.POT_KW)

    def stream_sheating(self, power):
        """
        Calentamiento o enfriamiento sensible
        power = potencia
        Ejemplo stream_sheating((20,'kW'))
        """
        if type(power)==int or type(power)==float:
            power = (power,UNIDADES.POT_KW)
        potencia = self.estado.cu.potencia(power,UNIDADES.POT_KW)[0]
        h2 = self.estado.h[0]+potencia/self.caudal[0]
        w2 = self.estado.W
        tseca2 = ((h2 - 2501*w2[0])/(1.006+1.86*w2[0]),UNIDADES.T_C)
        presion2 = self.estado.presion
        return FLUJO(AIRE_HUMEDO(tseca=tseca2,presion=presion2,\
                W=self.estado.W),
                self.caudal)

    def q_stream_sheating(self, estado_destino):
        """
        Devuelve el calor necesario para realizar un calentamiento
        sensible desde el estado actual al estado dado por el estado
        de destino, que tiene que tener la misma humedad absoluta que
        el de origen
        """
        ed2 = estado_destino
        if (self.estado.W[0]==ed2.W[0] and \
            self.estado.W[1]==ed2.W[1] and \
            self.estado.presion[0]==ed2.presion[0] and \
            self.estado.presion[1]==ed2.presion[1]):
            she = self.stream_h()
            return (ed2.h[0]*self.caudal[0]-she[0], she[1])
        else:
            print("Error, el estado de destino contiene diferente humedad absoluta que el de origen, por lo que no es un proceso de calentamiento o enfriamiento sensible; o las presiones barométricas son diferentes")
            return None

    def qm_stream_deshum_cooling(self, estado_destino):
        es1 = self.estado
        es2 = estado_destino
        if (es1.W[0]==es2.W[0] and
                es1.W[0]==es2.W[0]):
            return {'q' : q_stream_sheating(estado_destino)}
        elif (es1.W[0]>=es2.W[0] and es1.W[1]==es2.W[1] and
                es1.presion[0]==es2.presion[0] and \
                        es1.presion[1]==es2.presion[1]):
            mda = self.caudal[0]
            mw = mda*(es1.W[0]-es2.W[0])
            q2 = mda*(es2.h[0]-es1.h[0])+mw*water_h(es2.tseca)[0]
            return {'q':(q2, UNIDADES.POT_KW), 'mw':(mw,UNIDADES.FLUJO_KGW_S)}
        else:
            print("Error, el estado de destino suministrado contiene mayor humedad que el de origen, por lo que no se trata de una deshumectación; o tiene presiones barométricas diferentes")
            return None

    def stream_deshum_cooling(self, power, tseca=None, W=None):
        if type(tseca)==int or type(tseca)==float:
            tseca = (tseca,UNIDADES.T_C)
        if type(W)==int or type(W)==float:
            W = (W,UNIDADES.REL_KGW_KGDA)
        if type(power)==int or type(power)==float:
            power = (power,UNIDADES.POT_KW)
        if (power[0] >= 0):
            if (not tseca and not W) or \
                 (not tseca and type(W)==tuple and \
                  W[0]==self.estado.W[0] and \
                  W[1]==self.estado.W[1]):
                return q_stream_sheating(power)
            else:
                print("Error, se ha suministrado un calentamiento en lugar de enfriamiento, pero no es sensible, puesto que se la humedad de destino es diferente a la de origen, o se ha suministrado una temperatura seca, lo cual no está permitido en este caso")
                return None
        elif (type(tseca)==tuple and not W):
            ts2 = self.estado.cu.temperatura(tseca,UNIDADES.T_C)
            pot = self.estado.cu.potencia(power,UNIDADES.POT_KW)[0]
            we1 = self.estado.W[0]
            mda = self.caudal[0]
            hw2 = water_h(ts2)[0]
            ts2 = ts2[0]
            he1 = self.estado.h[0]
            #bloque1 = (2501+1.86*ts2-hw2)/mda
            #bloque2 = we1-pot/mda-he1+1.006*ts2
            bloque2 = pot/mda + he1 - (1.006+4.186*we1)*ts2
            bloque1 = 2501-2.326*ts2
            we2 = bloque2 / bloque1
            mw = mda*(we1-we2)
            #mw = bloque2 / bloque1
            #we2 = ((pot-mw*hw2)/mda + he1 -1.006*ts2)/(2501+1.86*ts2)
            est2 = AIRE_HUMEDO(tseca=(ts2,UNIDADES.T_C), \
                               presion=self.estado.presion, \
                               W = (we2,self.estado.W[1]))
            return FLUJO(est2,(mda,self.caudal[1]))
        elif (type(W)==tuple and not tseca):
            pot = self.estado.cu.potencia(power,UNIDADES.POT_KW)[0]
            we1 = self.estado.W[0]
            mda = self.caudal[0]
            he1 = self.estado.h[0]
            we2 = self.estado.cu.relacion_masica(W,UNIDADES.REL_KGW_KGDA)[0]
            mw = mda*(we1-we2)
            bloque1 = pot/mda + he1 -2501*we2
            bloque2 = 1.006 + 1.86*we2 + (mw*4.186)/mda
            ts2 = bloque1 / bloque2
            est2 = AIRE_HUMEDO(tseca=(ts2,UNIDADES.T_C), \
                               presion=self.estado.presion, \
                               W = (we2,self.estado.W[1]))
            return FLUJO(est2,(mda,self.caudal[1]))
        else:
            print("Error, no ha definido una potencia y una temperatura seca o humedad absoluta válidos. Para un enfriamiento la potencia debe ser negativa, y se debe suministrar uno de los datos: temperatura seca (tseca) o humedad absoluta (W), pero no los dos simultáneamente")
            return None

    def stream_hum_adiabatica(self, tsatsteam=None, trocio=None, W=None, \
                                    retmw=None):
        if type(trocio)==int or type(trocio)==float:
            trocio = (trocio,UNIDADES.T_C)
        if type(tsatsteam)==int or type(tsatsteam)==float:
            tsatsteam = (tsatsteam,UNIDADES.T_C)
        if type(W)==int or type(W)==float:
            W = (W,UNIDADES.REL_KGW_KGDA)
        if(type(trocio)==tuple and type(tsatsteam)==tuple and W==None):
            tsst =  self.estado.cu.temperatura(tsatsteam,UNIDADES.T_C)[0]
            tro =  self.estado.cu.temperatura(trocio,UNIDADES.T_C)[0]
            hg = 2501+1.86*tsst
            pw = self.estado.__class__._pws(trocio)[0]
            we1 = self.estado.W[0]
            we2 = (pw*0.621945)/(self.estado.presion[0]-pw)
            mda = self.caudal[0]
            mw = mda*(we2-we1)
            he1 = self.estado.h[0]
            he2 = (mda*he1+mw*hg)/mda
            tseca2 = (he2-2501*we2)/(1.006+1.86*we2)
            fe2 = FLUJO(AIRE_HUMEDO(tseca=tseca2, \
                    presion=self.estado.presion, W=we2), \
                    (mda,UNIDADES.FLUJO_KGDA_S))
            if(retmw==True):
                return {'f':fe2, 'mw':(mw,UNIDADES.FLUJO_KGW_S)}
            else:
                return fe2
        elif (type(W)==tuple and type(tsatsteam)==tuple and trocio==None):
            we1 = self.estado.W[0]
            we2 = self.estado.cu.relacion_masica(W,UNIDADES.REL_KGW_KGDA)[0]
            mda = self.caudal[0]
            mw = mda*(we2-we1)
            tsst =  self.estado.cu.temperatura(tsatsteam,UNIDADES.T_C)[0]
            hg = 2501+1.86*tsst
            he1 = self.estado.h[0]
            he2 = (mda*he1+mw*hg)/mda
            tseca2 = (he2-2501*we2)/(1.006+1.86*we2)
            fe2 = FLUJO(AIRE_HUMEDO(tseca=tseca2, \
                    presion=self.estado.presion, W=we2), \
                    (mda,UNIDADES.FLUJO_KGDA_S))
            if(retmw==True):
                return {'f':fe2, 'mw':(mw,UNIDADES.FLUJO_KGW_S)}
            else:
                return fe2
        else:
            print("Error, no se han introducido las condiciones adecuadas")
            return None

class PSICROMETRICO():
    """
    Crea un diagrama psicrométrico
    """

    def __init__(self):
        self.fig = self.__class__.__diagrama_psicrometrico__()
        self.ylength = 0.03
        self.xlength = 50
        self.escount = 0
        self.colormap = {'blue':'b', 'red':'r', 'green':'g', 'cyan':'c',
                    'magenta':'m', 'yellow':'y', 'black':'k', 'white':'w', }

    def __diagrama_psicrometrico__():
        plt.ion()
        f=plt.figure()
        temps = []
        tetiq = 30
        for t in list(numpy.arange(0,50,0.1)):
            temps.append(float(t))
        es = []
        for t in temps:
            es.append(AIRE_HUMEDO(tseca=t,trocio=t))
        ws = []
        for e in es:
            ws.append(e.W[0])
        p = plt.plot(temps,ws)
        for hr in range(1,10):
            es = []
            ws = []
            wetiq = None
            for t in temps:
                e = AIRE_HUMEDO(tseca=t,humrel=(hr*10,'%'))
                es.append(e)
                if t == tetiq:
                    wetiq = e.W[0]
            for e in es:
                ws.append(e.W[0])
            etiq = str(hr*10)+' %'
            p = plt.plot(temps,ws,'k--', linewidth = 1, label=etiq)
            plt.text(tetiq,wetiq,etiq)
        plt.xlabel('Temperatura seca (ºC)')
        plt.xlim(0,50)
        ax = f.add_subplot(111)
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position("right")
        plt.ylim(0,0.03)
        plt.ylabel('Humedad absoluta (kg_w/kg_da)')
        plt.grid(True)
        plt.grid(color='k', linestyle=':', linewidth=0.5)
        plt.title('Diagrama psicrométrico a presión atmosférica (101.325 kPa)')
        plt.minorticks_on()
        return f

    def marca_estado(self, estado, colorplot='red', colortext='red', printtag=True):
        plt.figure(self.fig.number)
        plt.plot([estado.tseca[0]],[estado.W[0]],self.colormap[colorplot]+'o')
        if printtag:
            self.escount += 1
        plt.text(estado.tseca[0], estado.W[0], \
                ("  "+str(int(self.escount))) if printtag else "", \
                color=colortext, weight='roman')#, size='x-small')

    def marca_proceso(self, *args):
        estado1 = None
        estado2 = None
        for est in args:
            if issubclass(est.__class__, AIRE_HUMEDO):
                estado2 = est
            elif issubclass(est.__class__, FLUJO):
                estado2 = est.estado
            else:
                raise ValueError('Error. No ha suministrado un objeto AIRE_HUMEDO o FLUJO')
            plt.figure(self.fig.number)
            self.marca_estado(estado2)
            #self.marca_estado(estado1)
            #self.marca_estado(estado2)
            if estado1:
                ts = [estado1.tseca[0],estado2.tseca[0]]
                ws = [estado1.W[0],estado2.W[0]]
                plt.plot(ts,ws,'b-')
                x0 = (ts[1]+ts[0])/2.0
                y0 = (ws[1]+ws[0])/2.0
                escalay = self.ylength/self.xlength
                if (ts[1]==ts[0]):
                    ix = 0
                    if ws[1]==ws[0]:
                        iy = 0
                    else:
                        iy = 0.5*escalay*(ws[1]-ws[0])/abs(ws[1]-ws[0])
                    iwidth = 0.0001/escalay
                    ihwidth = 4*iwidth
                    ihlength = iwidth*6*escalay
                else:
                    pend = (ws[1]-ws[0])/float(ts[1]-ts[0])
                    ix = 0.5*(ts[1]-ts[0])/abs(ts[1]-ts[0])
                    iy = pend*ix
                    if pend==0:
                        iwidth = 0.0001
                    else:
                        #iwidth = 0.0001/pend
                        iwidth = 0
                    ihwidth = 4*iwidth
                    ihlength = iwidth*6
                plt.arrow(x0, y0, ix, iy, width=iwidth, \
                    head_width=ihwidth, head_length=ihlength, \
                    head_starts_at_zero=True, length_includes_head=False)
            estado1 = estado2

class ESPACIO():
    """
    Definición de espacio con cargas sensibles y latentes
    """
    def __init__(self, tseca, qs, ql=None, mw=None, hw=None, humrel=None, \
            nombre=None, superficie=None, altura=None):
        self.cu = CONVERSOR_UNIDADES()
        if type(tseca)==int or type(tseca)==float:
            tseca = (tseca,UNIDADES.T_C)
        if type(qs)==int or type(qs)==float:
            qs = (qs,UNIDADES.POT_KW)
        if type(ql)==int or type(ql)==float:
            ql = (ql,UNIDADES.POT_KW)
        if type(mw)==int or type(mw)==float:
            mw = (mw,UNIDADES.FLUJO_KGW_S)
        if type(hw)==int or type(hw)==float:
            hw = (hw,UNIDADES.E_KJ_KGW)
        if type(humrel)==int or type(humrel)==float:
            humrel = (humrel,UNIDADES.PER_1)
        if (type(nombre)==str):
            self.nombre = nombre
        if type(superficie)==int or type(superficie)==float:
            superficie = (superficie,UNIDADES.A_M2)
        if type(altura)==int or type(altura)==float:
            altura = (altura,UNIDADES.L_M)
        self.tseca = self.cu.temperatura(tseca,UNIDADES.T_C)
        self.qsensible = self.cu.potencia(qs,UNIDADES.POT_KW)
        if ql:
            self.qlatente = self.cu.potencia(ql,UNIDADES.POT_KW)
        if mw:
            self.mw = self.cu.caudal(mw,UNIDADES.FLUJO_KGW_S)
        if hw:
            self.hw = self.cu.entalpia(hw,UNIDADES.E_KJ_KGW)
        if humrel:
            self.humrel = self.cu.porcentaje(hw,UNIDADES.PER_1)
        if not ql and mw and hw:
            self.ql = (self.mw[0]*self.hw[0],UNIDADES.POT_KW)
        if not tseca or not qs or not ql:
            print("ERROR, no ha definido correctamente los parámetros de entrada para el espacio")

    def proceso():
        #TODO
        return None
