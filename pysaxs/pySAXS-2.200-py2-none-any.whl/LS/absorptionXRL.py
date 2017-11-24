"""
This module use  the xraylib library
and provide high level functions for
absorption factors for chemical compounds

August 2012 by OT
based on work by AT
"""
from string import *
import numpy
import os
from pySAXS import xraylib

ATOMS_NAME=["Hydrogen","Helium","Lithium","Beryllium","Boron","Carbon, Graphite","Nitrogen","Oxygen","Fluorine","Neon","Sodium","Magnesium","Aluminum","Silicon","Phosphorus","Sulfur","Chlorine","Argon","Potassium","Calcium","Scandium","Titanium","Vanadium","Chromium","Manganese","Iron","Cobalt","Nickel","Copper","Zinc","Gallium","Germanium","Arsenic","Selenium","Bromine","Krypton","Rubidium","Strontium","Yttrium","Zirconium","Niobium","Molybdenum","Technetium","Ruthenium","Rhodium","Palladium","Silver","Cadmium","Indium","Tin","Antimony","Tellurium","Iodine","Xenon","Cesium","Barium","Lanthanum","Cerium","Praseodymium","Neodymium","Promethium","Samarium","Europium","Gadolinium","Terbium","Dysprosium","Holmium","Erbium","Thulium","Ytterbium","Lutetium","Hafnium","Tantalum","Tungsten","Rhenium","Osmium","Iridium","Platinum","Gold","Mercury","Thallium","Lead","Bismuth","Polonium","Astatine","Radon","Francium","Radium","Actinium","Thorium","Protactinium","Uranium"]
COMMON_XRAY_SOURCE_MATERIALS=['Cu','Cr','Mo']
MENDELEIEV_TABLE =[['H', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 'He'],\
            ['Li', 'Be', None, None, None, None, None, None, None, None, None, None, 'B', 'C', 'N', 'O', 'F', 'Ne'],\
             ['Na', 'Mg', None, None, None, None, None, None, None, None, None, None, 'Al', 'Si', 'P', 'S', 'Cl', 'Ar'],\
              ['K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr'],\
               ['Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe'],\
               ['Cs','Ba','La','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn'],\
               ['Fr','Ra','Ac',None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],\
               [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],\
               ['Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu',None, None, None, None],\
               ['Th', 'Pa', 'U', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]]

KEV2ANGST = xraylib.KEV2ANGST #12.39841875

def getZName(name):
    '''
    return the Atomic Number Z from compound name
    >>> getZName("Copper")
    29
    '''
    Z=ATOMS_NAME.index(name)+1
    return Z

def SymbolToAtomicNumber(symbol):
    '''
    get the atomic number of a symbol
    copy of xraylib.SymbolToAtomicNumber(symbol)
    >>> SymbolToAtomicNumber('Cu')
    29
    '''
    return xraylib.SymbolToAtomicNumber(symbol)

def AtomicNumberToSymbol(Z):
    '''
    get the symbol from an atomic number
    copy of xraylib.AtomicNumberToSymbol(Z)
    >>> AtomicNumberToSymbol(29)
    'Cu'
    '''
    return xraylib.AtomicNumberToSymbol(Z)

def getNameZ(Z):
    '''
    return the name from a Z
    >>> getNameZ(29)
    'Copper'
    '''
    return ATOMS_NAME[Z-1]
    

def getAtomsFormula(S):
    '''
    Transform a string containing a chemical formula ('C 1 O 2') in two array
    - list of atoms
    - numeric array of atoms number
    7-13-2012 by OT
    >>> getAtomsFormula('C 1 O 2')
    ['C','O'] [1,2]
    '''
    S=S.strip()
    L=S.split(' ') #cut at all spaces
    rS=L[::2] #Symbols to be return
    rN=numpy.array(L[1::2],dtype='float') #Numbers to be return
    return rS,rN

def getFormulaAtoms(atomS,atomN):
    '''
    transform a compound list and number in string
    >>> AtomsToCompound(['H','O'],[2,1])
    'H 2 O 1' 
    '''
    S=''
    if len(atomS)==len(atomN):
        for i in range(len(atomS)):
            S=S+' '+str(atomS[i])+' '+str(atomN[i])
    return S.strip()

def getMuZ(Z,energy=8.028):
    '''
    return Mu from Atomic number Z
    >>> getMuZ(4)
    0.8719998598098755
    '''
    return xraylib.CS_Photo(Z,energy)

def getMuSymbol(S,energy=8.028):
    """
    This function returns the xray absorption coefficient of the atom with
    symbole S (ie 'C' fo carbon, 'Au' for gold) by default energy is 8.03 keV
    and mass-energy absorption coefficient are return. To get the mass
    absorption coefficient ISEN has to be 0
    """
    Z=xraylib.AtomicNumberToSymbol(S)
    return getMuZ(Z ,energy)
    
def getMuName(name,energy=8.028):
    '''
    This function returns the xray absorption coefficient of the atom with
    name S (ie 'Carbon' , 'Gold') by default energy is 8.028 keV and mass-energy
    absorption coefficient are return. To get the mass absorption coefficient
    '''
    Z=getZName(name)
    return getMuZ(Z,energy)
    


def getMasseZ(Z):
    '''
    returns the molar mass (atomic weight) of the atomic number Z
    '''
    return xraylib.AtomicWeight(Z)

def getMasseSymbol(S):
    '''
    returns the molar mass (atomic weight) of the atom with atomic number Z
    (ie 'C' fo carbon, 'Au' for gold)
    '''
    Z=xraylib.SymbolToAtomicNumber(S)
    return getMasseZ(Z)



def getMuFormula(S,energy=8.028):
    '''
    This function returns the mass attenuation coefficient for a chemical
    formula in the form 'C 6 H 6 O 2 N 1'
    '''
    #29-8-2012 by OT use of xraylib
    #7-13-2012 by OT improved for formula with fraction 'Si 1.2 Al 0.8'
    
    if len(S)!=0:
        S,N=getAtomsFormula(S)
        Mu=numpy.zeros(len(S),float)
        Ma=numpy.zeros(len(S),float)
        CMa=0.0
        CMu=0.0
        for i in numpy.arange(len(S)):
            Z=xraylib.SymbolToAtomicNumber(S[i])
            Mu[i]=xraylib.CS_Photo(Z,energy)
            Ma[i]=xraylib.AtomicWeight(Z)
            CMa=CMa+Ma[i]*N[i]
            CMu=CMu+Mu[i]*Ma[i]*N[i]
        return CMu/CMa
    else:
        return 0.0

def getMasseFormula(S,energy=8.028):
    """
    This function returns the molar mass a chemical formula
    in the form  'C 6 H 6 O 2 N 1'
    """
    if len(S)!=0:
        S,N=getAtomsFormula(S)
        Ma=numpy.zeros(len(S),float)
        CMa=0.0
        for i in numpy.arange(len(S)):
            Ma[i]=getMasseSymbol(S[i])
            CMa=CMa+Ma[i]*N[i]
        return CMa
    else:
        return 0.0

def getElectronNumber(S):
    S,N=getAtomsFormula(S)
    Z=0
    for i in numpy.arange(len(S)):
        Z=Z+(xraylib.SymbolToAtomicNumber(S[i]))*N[i]
    return Z

def getElectronDensity(S,rho):
    '''
    return the electron density and the scattering length density
    '''
    #Thomson scattering length
    Belec=0.282e-12
    Navo=xraylib.AVOGNUM*1e24
    M=getMasseFormula(S)
    Z=getElectronNumber(S)
    ED=(rho*Z*Navo)/M
    #print "rho=",rho,"\tZ=",Z,"\tNavo=",Navo,"\tM=",M,"\tED=",ED
    return ED,ED*Belec
    
    
def getEnergyFromSource(source='Cu'):
    '''
    return the KA LINE (most used) energy from the x-ray source
    >>> getEnergyFromSource('Cu')
    8.04105057076251
    >>> getEnergyFromSource('Mo')
    17.443217030477935
    '''
    Z=xraylib.SymbolToAtomicNumber(source)
    return xraylib.LineEnergy(Z,xraylib.KA_LINE)

def getAngstFromSource(source='Cu'):
    '''
    return the KA LINE (most used) energy in ANGSTROM from the x-ray source
    >>> getAngstFromSource('Cu')
    1.5418904085842968
    '''
    Z=xraylib.SymbolToAtomicNumber(source)
    return xraylib.KEV2ANGST/xraylib.LineEnergy(Z,xraylib.KA_LINE)

def getTransmission(formula,thickness=1.0,density=1.0,energy=8.03):
    '''
    return the transmission of a compound
    thickness in cm
    >>> getTransmission('H 2 O 1',0.1,density=1.0,energy=8.03)
    0.376802369048
    '''
    #calculate mu for compound
    mu=getMuFormula(formula,energy)
    #calculate Transmission
    return numpy.exp(-density*mu*thickness)
                            
if __name__== '__main__':
    formula="H 2 O 1"
    density=1.0
    thickness=0.1 #1 mm
    source='Cu'
    energy=getEnergyFromSource(source)
    print "energy for ",source," : ",energy," keV ->",getAngstFromSource(source),' A'
    print "Calculate Mu from formula for water : ",formula
    mu=getMuFormula(formula,energy)
    print mu
    print "X-ray transmission = ",numpy.exp(-density*mu*thickness)
    print getTransmission(formula,thickness,density,energy)
    print "--------------------"
    source='Mo'
    energy=getEnergyFromSource(source)
    print "energy for ",source," : ",energy," keV ->",getAngstFromSource(source),' A'
    print "Calculate Mu from formula for water : ",formula
    mu=getMuFormula(formula,energy)
    print mu
    print "X-ray transmission = ",numpy.exp(-density*mu*thickness)
    print getTransmission(formula,thickness,density,energy)
    print "--------------------"
    
